#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

try:
    from corekit.ffmpeg_locator import ffmpeg_exe
    from corekit.subtitle_to_json import parse_srt
except ModuleNotFoundError:
    from ffmpeg_locator import ffmpeg_exe
    from subtitle_to_json import parse_srt


TIME_RE = re.compile(r"^(\d{2}):(\d{2}):(\d{2}),(\d{3})$")


def to_seconds(ts: str) -> float:
    match = TIME_RE.match(ts)
    if not match:
        raise ValueError(f"invalid SRT timestamp: {ts}")
    h, m, s, ms = (int(v) for v in match.groups())
    return h * 3600 + m * 60 + s + ms / 1000


def fmt_time(seconds: float) -> str:
    total_ms = max(0, int(round(seconds * 1000)))
    hours, rem = divmod(total_ms, 3_600_000)
    mins, rem = divmod(rem, 60_000)
    secs, ms = divmod(rem, 1_000)
    return f"{hours:02d}:{mins:02d}:{secs:02d},{ms:03d}"


def slugify(text: str, fallback: str) -> str:
    compact = re.sub(r"\s+", "-", text.strip())
    compact = re.sub(r"[^\w\u4e00-\u9fff-]", "", compact, flags=re.UNICODE)
    compact = re.sub(r"-{2,}", "-", compact).strip("-").lower()
    return compact or fallback


def run_ffmpeg_cut(src_video: Path, start: float, end: float, dst_video: Path) -> None:
    duration = max(0.01, end - start)
    cmd = [
        ffmpeg_exe(),
        "-y",
        "-ss",
        f"{start:.3f}",
        "-i",
        str(src_video),
        "-t",
        f"{duration:.3f}",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "18",
        "-c:a",
        "aac",
        "-movflags",
        "+faststart",
        str(dst_video),
    ]
    subprocess.run(cmd, check=True)


def write_windowed_srt(cues: list[dict[str, Any]], start: float, end: float, dst_srt: Path) -> None:
    selected: list[tuple[float, float, str]] = []
    for cue in cues:
        if cue["end_seconds"] <= start or cue["start_seconds"] >= end:
            continue
        selected.append(
            (
                max(0.0, cue["start_seconds"] - start),
                max(0.0, min(end, cue["end_seconds"]) - start),
                str(cue["text"]).strip(),
            )
        )

    lines: list[str] = []
    for idx, (cue_start, cue_end, text) in enumerate(selected, start=1):
        lines.extend([str(idx), f"{fmt_time(cue_start)} --> {fmt_time(cue_end)}", text, ""])
    dst_srt.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def build_clip_folder_name(index: int, clip: dict[str, Any]) -> str:
    clip_id = str(clip.get("id", f"clip-{index:02d}"))
    title = str(clip.get("title", "")).strip()
    return f"{index:02d}-{slugify(title, clip_id)}"


def get_clip_bounds(clip: dict[str, Any]) -> tuple[float, float]:
    start = clip.get("start_seconds")
    end = clip.get("end_seconds")
    if start is None and "start" in clip:
        start = to_seconds(str(clip["start"]))
    if end is None and "end" in clip:
        end = to_seconds(str(clip["end"]))
    if start is None or end is None:
        raise ValueError(f"clip missing time bounds: {clip}")
    start_f = float(start)
    end_f = float(end)
    if end_f <= start_f:
        raise ValueError(f"clip has non-positive duration: {clip}")
    return start_f, end_f


def export_one(
    index: int,
    clip: dict[str, Any],
    src_video: Path,
    cues: list[dict[str, Any]],
    output_root: Path,
    render_if_zh: bool,
    fontfile: str,
) -> dict[str, Any]:
    start, end = get_clip_bounds(clip)
    clip_dir = output_root / build_clip_folder_name(index, clip)
    clip_dir.mkdir(parents=True, exist_ok=True)

    clip_video = clip_dir / "clip.mp4"
    clip_src_srt = clip_dir / "clip.src.srt"
    clip_zh_srt = clip_dir / "clip.zh.srt"
    clip_hardsub = clip_dir / "clip.hardsub.mp4"

    run_ffmpeg_cut(src_video, start, end, clip_video)
    write_windowed_srt(cues, start, end, clip_src_srt)

    if render_if_zh and clip_zh_srt.exists():
        cmd = [sys.executable, "-m", "corekit.render_hardsubs", str(clip_video), str(clip_zh_srt), str(clip_hardsub)]
        title = str(clip.get("title", "")).strip()
        if title:
            cmd.extend(["--title", title])
        if fontfile:
            cmd.extend(["--fontfile", fontfile])
        subprocess.run(cmd, check=True)

    return {
        "id": clip.get("id", f"clip-{index:02d}"),
        "start_seconds": start,
        "end_seconds": end,
        "duration_seconds": round(end - start, 3),
        "title": clip.get("title", ""),
        "clip_dir": str(clip_dir),
        "clip_video": str(clip_video),
        "clip_src_srt": str(clip_src_srt),
        "clip_zh_srt": str(clip_zh_srt),
        "clip_hardsub": str(clip_hardsub) if clip_hardsub.exists() else "",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Batch export clips from selected_clips.json.")
    parser.add_argument("source_video", help="Source MP4 path")
    parser.add_argument("source_srt", help="Source SRT path")
    parser.add_argument("selected_clips_json", help="selected_clips.json path")
    parser.add_argument("output_dir", help="Output clips directory")
    parser.add_argument("--workers", type=int, default=4, help="Parallel workers (default: 4)")
    parser.add_argument("--render-if-zh", action="store_true", help="Render clip.hardsub.mp4 if clip.zh.srt exists")
    parser.add_argument("--fontfile", default="", help="Optional font path passed to render_hardsubs")
    args = parser.parse_args()

    src_video = Path(args.source_video).expanduser().resolve()
    src_srt = Path(args.source_srt).expanduser().resolve()
    selected_path = Path(args.selected_clips_json).expanduser().resolve()
    output_root = Path(args.output_dir).expanduser().resolve()

    if not src_video.exists():
        raise FileNotFoundError(f"source video not found: {src_video}")
    if not src_srt.exists():
        raise FileNotFoundError(f"source SRT not found: {src_srt}")
    if not selected_path.exists():
        raise FileNotFoundError(f"selected_clips.json not found: {selected_path}")

    output_root.mkdir(parents=True, exist_ok=True)
    cues = parse_srt(src_srt.read_text(encoding="utf-8", errors="ignore"))
    selected = json.loads(selected_path.read_text(encoding="utf-8"))
    if not isinstance(selected, list):
        raise ValueError("selected_clips.json must be a JSON array")

    reports: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = [
            pool.submit(
                export_one,
                idx,
                clip,
                src_video,
                cues,
                output_root,
                args.render_if_zh,
                args.fontfile,
            )
            for idx, clip in enumerate(selected, start=1)
        ]
        for future in as_completed(futures):
            reports.append(future.result())

    reports.sort(key=lambda item: str(item["id"]))
    report_path = output_root.parent / "export-report.json"
    report_path.write_text(json.dumps(reports, ensure_ascii=False, indent=2), encoding="utf-8")
    print(report_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
