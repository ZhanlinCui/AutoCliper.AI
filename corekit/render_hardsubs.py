#!/usr/bin/env python3
"""Burn Chinese subtitles and an optional first-second title into a clip.

Supports two rendering backends:
  1. ``subtitles=`` filter (requires libass) — preferred, supports ASS styling.
  2. ``drawtext`` chain fallback — works on any ffmpeg with libfreetype.

The script auto-detects libass at runtime and picks the best available path.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

try:
    from corekit.ffmpeg_locator import ffmpeg_exe, h264_encoder, aac_encoder
except ModuleNotFoundError:
    from ffmpeg_locator import ffmpeg_exe, h264_encoder, aac_encoder

_TIME_RE = re.compile(
    r"(?P<h>\d{2}):(?P<m>\d{2}):(?P<s>\d{2}),(?P<ms>\d{3})"
)

_FONT_CANDIDATES = [
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
]


def _resolve_font(explicit: str) -> Path:
    if explicit:
        p = Path(explicit)
        if p.exists():
            return p
    for candidate in _FONT_CANDIDATES:
        p = Path(candidate)
        if p.exists():
            return p
    return Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf")


def _has_libass() -> bool:
    try:
        out = subprocess.check_output(
            [ffmpeg_exe(), "-filters"], stderr=subprocess.STDOUT, text=True,
        )
        for line in out.splitlines():
            parts = line.split()
            if len(parts) >= 2 and parts[1] in ("subtitles", "ass"):
                return True
    except Exception:
        pass
    return False


def _escape_filter_path(path: Path) -> str:
    raw = str(path.resolve())
    return raw.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")


def _ts_to_seconds(ts_str: str) -> float:
    m = _TIME_RE.match(ts_str.strip())
    if not m:
        return 0.0
    return int(m["h"]) * 3600 + int(m["m"]) * 60 + int(m["s"]) + int(m["ms"]) / 1000


def _parse_srt(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    blocks = re.split(r"\n\s*\n", text.strip(), flags=re.M)
    cues: list[dict] = []
    ts_line_re = re.compile(
        r"(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})"
    )
    for block in blocks:
        lines = [ln.rstrip() for ln in block.splitlines() if ln.strip()]
        if len(lines) < 2:
            continue
        ts_match = None
        text_start = 0
        for i, ln in enumerate(lines):
            ts_match = ts_line_re.match(ln)
            if ts_match:
                text_start = i + 1
                break
        if not ts_match:
            continue
        body = " ".join(lines[text_start:]).strip()
        if not body:
            continue
        cues.append({
            "start": _ts_to_seconds(ts_match.group(1)),
            "end": _ts_to_seconds(ts_match.group(2)),
            "text": body,
        })
    return cues


def _escape_drawtext(text: str) -> str:
    out = text.replace("\\", "\\\\\\\\")
    out = out.replace("'", "\u2019")
    out = out.replace(":", "\\:")
    out = out.replace("%", "%%")
    return out


def _build_drawtext_subtitle_filters(
    cues: list[dict], fontfile: Path, fontsize: int = 28,
) -> list[str]:
    safe_font = _escape_filter_path(fontfile)
    filters: list[str] = []
    for cue in cues:
        safe_text = _escape_drawtext(cue["text"])
        s, e = cue["start"], cue["end"]
        dt = (
            "drawtext="
            f"fontfile='{safe_font}':"
            f"text='{safe_text}':"
            f"fontcolor=white:fontsize={fontsize}:"
            "borderw=2:bordercolor=black:"
            "x=(w-text_w)/2:y=h-text_h-40:"
            f"enable='between(t,{s:.3f},{e:.3f})'"
        )
        filters.append(dt)
    return filters


def _build_title_filter(title: str, fontfile: Path) -> str:
    safe_font = _escape_filter_path(fontfile)
    safe_title = _escape_drawtext(title)
    return (
        "drawtext="
        f"fontfile='{safe_font}':"
        f"text='{safe_title}':"
        "fontcolor=white:fontsize=48:borderw=3:bordercolor=black:"
        "x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,0,1)'"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Burn subtitles (+ optional title) into a video clip.",
    )
    parser.add_argument("input_video")
    parser.add_argument("input_srt")
    parser.add_argument("output_video")
    parser.add_argument("--title", default="")
    parser.add_argument("--fontfile", default="")
    parser.add_argument(
        "--subtitle-fontsize", type=int, default=28,
        help="Font size for drawtext subtitle fallback (default 28)",
    )
    args = parser.parse_args()

    src = Path(args.input_video)
    srt = Path(args.input_srt)
    dst = Path(args.output_video)
    dst.parent.mkdir(parents=True, exist_ok=True)

    fontfile = _resolve_font(args.fontfile)
    use_libass = _has_libass()

    vf_parts: list[str] = []

    if use_libass:
        vf_parts.append(f"subtitles='{_escape_filter_path(srt)}'")
        print(f"[render] using subtitles filter (libass)", file=sys.stderr)
    else:
        cues = _parse_srt(srt)
        if not cues:
            print(f"[render] WARNING: no subtitle cues found in {srt}", file=sys.stderr)
        else:
            dt_filters = _build_drawtext_subtitle_filters(
                cues, fontfile, args.subtitle_fontsize,
            )
            vf_parts.extend(dt_filters)
            print(
                f"[render] using drawtext fallback ({len(cues)} cues, no libass)",
                file=sys.stderr,
            )

    if args.title:
        vf_parts.append(_build_title_filter(args.title, fontfile))

    if not vf_parts:
        print("[render] WARNING: no filters to apply, copying input", file=sys.stderr)
        import shutil
        shutil.copy2(src, dst)
        return 0

    enc = h264_encoder()
    aac = aac_encoder()
    cmd = [
        ffmpeg_exe(),
        "-y",
        "-i", str(src),
        "-vf", ",".join(vf_parts),
        "-c:v", enc,
        "-c:a", aac,
        "-movflags", "+faststart",
        str(dst),
    ]
    if enc == "libx264":
        cmd.insert(-1, "-preset")
        cmd.insert(-1, "medium")
        cmd.insert(-1, "-crf")
        cmd.insert(-1, "18")

    print(f"[render] encoder={enc}", file=sys.stderr)
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"[render] ffmpeg exited with code {result.returncode}", file=sys.stderr)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
