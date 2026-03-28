#!/usr/bin/env python3
import argparse
import shlex
import subprocess
from pathlib import Path

try:
    from scripts._ffmpeg import ffmpeg_exe
except ModuleNotFoundError:
    from _ffmpeg import ffmpeg_exe


def escape_filter_path(path: Path) -> str:
    raw = str(path.resolve())
    return raw.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_video")
    parser.add_argument("input_srt")
    parser.add_argument("output_video")
    parser.add_argument("--title", default="")
    parser.add_argument("--fontfile", default="")
    args = parser.parse_args()

    src = Path(args.input_video)
    srt = Path(args.input_srt)
    dst = Path(args.output_video)
    dst.parent.mkdir(parents=True, exist_ok=True)

    vf_parts = [f"subtitles='{escape_filter_path(srt)}'"]
    if args.title:
        fontfile = Path(args.fontfile) if args.fontfile else Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf")
        safe_title = args.title.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
        drawtext = (
            "drawtext="
            f"fontfile='{escape_filter_path(fontfile)}':"
            f"text='{safe_title}':"
            "fontcolor=white:fontsize=48:borderw=3:bordercolor=black:"
            "x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,0,1)'"
        )
        vf_parts.append(drawtext)

    cmd = [
        ffmpeg_exe(),
        "-y",
        "-i",
        str(src),
        "-vf",
        ",".join(vf_parts),
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
        str(dst),
    ]
    return subprocess.run(cmd).returncode


if __name__ == "__main__":
    raise SystemExit(main())
