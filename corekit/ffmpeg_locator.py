#!/usr/bin/env python3
"""Locate ffmpeg and probe available encoders at runtime.

Usage::

    from corekit.ffmpeg_locator import ffmpeg_exe, h264_encoder

    ffmpeg_exe()      # -> "/opt/anaconda3/bin/ffmpeg"
    h264_encoder()    # -> "h264_videotoolbox" | "libx264" | "libopenh264"
"""
import functools
import shutil
import subprocess
import sys
from pathlib import Path


def ffmpeg_exe() -> str:
    direct = shutil.which("ffmpeg")
    if direct:
        return direct

    try:
        out = subprocess.check_output(
            [sys.executable, "-c", "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())"],
            text=True,
        ).strip()
    except Exception as exc:
        raise RuntimeError("ffmpeg not available; install imageio-ffmpeg or system ffmpeg") from exc

    if not out or not Path(out).exists():
        raise RuntimeError("ffmpeg executable path not found")
    return out


@functools.lru_cache(maxsize=1)
def h264_encoder() -> str:
    """Return the best available H.264 encoder name.

    Preference order:
      1. libx264      — best quality/control, requires GPL build
      2. h264_videotoolbox — macOS hardware encoder, fast
      3. libopenh264  — always-available fallback
    """
    try:
        out = subprocess.check_output(
            [ffmpeg_exe(), "-encoders"], stderr=subprocess.STDOUT, text=True,
        )
    except Exception:
        return "libopenh264"

    available: set[str] = set()
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 2:
            available.add(parts[1])

    for choice in ("libx264", "h264_videotoolbox", "libopenh264"):
        if choice in available:
            return choice
    return "libopenh264"


@functools.lru_cache(maxsize=1)
def aac_encoder() -> str:
    """Return best available AAC encoder."""
    try:
        out = subprocess.check_output(
            [ffmpeg_exe(), "-encoders"], stderr=subprocess.STDOUT, text=True,
        )
    except Exception:
        return "aac"
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "aac_at":
            return "aac_at"
    return "aac"
