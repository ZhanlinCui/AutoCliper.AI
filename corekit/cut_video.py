#!/usr/bin/env python3
"""Cut an exact time-range segment from a source video."""
import subprocess
import sys
from pathlib import Path

try:
    from corekit.ffmpeg_locator import ffmpeg_exe, h264_encoder, aac_encoder
except ModuleNotFoundError:
    from ffmpeg_locator import ffmpeg_exe, h264_encoder, aac_encoder


def main() -> int:
    if len(sys.argv) != 5:
        print("Usage: cut_video.py input.mp4 start_sec end_sec output.mp4", file=sys.stderr)
        return 1
    src = Path(sys.argv[1])
    start = float(sys.argv[2])
    end = float(sys.argv[3])
    dst = Path(sys.argv[4])
    duration = max(0.01, end - start)

    dst.parent.mkdir(parents=True, exist_ok=True)

    enc = h264_encoder()
    aac = aac_encoder()
    cmd = [
        ffmpeg_exe(),
        "-y",
        "-ss", str(start),
        "-i", str(src),
        "-t", str(duration),
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

    print(f"[cut] encoder={enc}, {start:.1f}→{end:.1f}", file=sys.stderr)
    return subprocess.run(cmd).returncode


if __name__ == "__main__":
    raise SystemExit(main())
