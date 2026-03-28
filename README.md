<p align="center">
  <strong>AutoCliper.AI</strong><br>
  <em>One long video in. A dozen ready-to-post short clips out.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.9+-blue?style=flat-square" alt="Python 3.9+">
  <img src="https://img.shields.io/badge/ffmpeg-required-orange?style=flat-square" alt="FFmpeg">
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="MIT">
  <img src="https://img.shields.io/badge/libass-optional-lightgrey?style=flat-square" alt="libass optional">
</p>

---

AutoCliper.AI takes a YouTube interview, podcast, or talk and turns it into **5–15 Chinese-subtitled short clips** — packaged with titles, descriptions, and hard-burned subtitles — ready for Shorts, Douyin, TikTok, and Reels.

## Why AutoCliper

| Pain Point | AutoCliper Solution |
|---|---|
| Manually scrubbing through hour-long interviews | AI-driven transcript analysis surfaces the strongest moments |
| Subtitle rendering breaks on different ffmpeg builds | Runtime detection: **libass** when available, **drawtext** chain as universal fallback |
| H.264 encoder mismatch across environments | Auto-selects `libx264` → `h264_videotoolbox` → `libopenh264` |
| Cutting clips loses subtitle sync | Windowed SRT extraction preserves frame-accurate timing |
| No idea what makes a good short clip | Built-in playbooks score candidates on hook, clarity, standalone, and payoff |

## Pipeline

```
YouTube URL
    │
    ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────────┐
│ fetch_source │───▶│subtitle_to_ │───▶│  Agent analyzes  │
│  (yt-dlp)   │    │  json (SRT  │    │  transcript and  │
│  video+subs  │    │  → JSON)    │    │  proposes clips  │
└─────────────┘    └─────────────┘    └────────┬────────┘
                                               │
                                               ▼
                                     ┌─────────────────┐
                                     │   User reviews   │
                                     │  candidate board │
                                     └────────┬────────┘
                                              │
                        ┌─────────────────────┼─────────────────────┐
                        ▼                     ▼                     ▼
                  ┌───────────┐        ┌───────────┐        ┌───────────┐
                  │ cut_video │        │ cut_video │        │ cut_video │
                  │ + window  │        │ + window  │        │ + window  │
                  │ + translate│       │ + translate│       │ + translate│
                  │ + burn    │        │ + burn    │        │ + burn    │
                  └─────┬─────┘        └─────┬─────┘        └─────┬─────┘
                        ▼                     ▼                     ▼
                  clip.hardsub.mp4     clip.hardsub.mp4     clip.hardsub.mp4
```

## Quick Start

```bash
# 1  Download source video + subtitles
PYTHONPATH="$PWD" python3 -m corekit.fetch_source \
  "https://youtube.com/watch?v=..." \
  "studio/my-interview/intake"

# 2  Parse subtitles into structured JSON
PYTHONPATH="$PWD" python3 -m corekit.subtitle_to_json \
  "studio/my-interview/intake/raw.en.srt" \
  "studio/my-interview/intel/transcript.json"

# 3  Agent analyzes transcript → selected_clips.json
#    (follows playbooks/content-analysis-playbook.md)

# 4  For each selected clip:

#    Cut the segment
PYTHONPATH="$PWD" python3 -m corekit.cut_video \
  "studio/my-interview/intake/raw.mp4" \
  723.0 802.5 \
  "studio/my-interview/exports/01-ai-will-replace/clip.mp4"

#    Extract windowed subtitle
PYTHONPATH="$PWD" python3 -m corekit.window_subtitles \
  "studio/my-interview/intake/raw.en.srt" \
  723.0 802.5 \
  "studio/my-interview/exports/01-ai-will-replace/clip.src.srt"

#    Agent translates clip.src.srt → clip.zh.srt

#    Burn Chinese subtitles + title overlay
PYTHONPATH="$PWD" python3 -m corekit.render_hardsubs \
  "studio/my-interview/exports/01-ai-will-replace/clip.mp4" \
  "studio/my-interview/exports/01-ai-will-replace/clip.zh.srt" \
  "studio/my-interview/exports/01-ai-will-replace/clip.hardsub.mp4" \
  --title "AI终将取代一切？"
```

## Workspace Layout

```
studio/<video-slug>/
├── intake/                         # raw assets from YouTube
│   ├── raw.mp4
│   └── raw.<lang>.srt
├── intel/                          # analysis artifacts
│   ├── transcript.json             # structured subtitle cues
│   ├── selected_clips.json         # clip decisions (see clip-contract.md)
│   ├── candidate-board.md          # review table for user approval
│   └── packaging-copy.md           # titles + descriptions for all clips
└── exports/                        # one folder per clip
    └── 01-<slug>/
        ├── clip.mp4                # raw cut
        ├── clip.src.srt            # windowed source-language subtitle
        ├── clip.zh.srt             # translated Chinese subtitle
        ├── clip.hardsub.mp4        # final deliverable with burned subs
        └── metadata.txt            # title + description for distribution
```

## Corekit Modules

| Module | Purpose |
|--------|---------|
| `corekit.fetch_source` | Download video + subtitles via yt-dlp (English preferred, Chinese fallback) |
| `corekit.subtitle_to_json` | Parse SRT into JSON with cue index, timestamps, and seconds |
| `corekit.cut_video` | Extract a precise time-range segment as re-encoded MP4 |
| `corekit.window_subtitles` | Slice subtitle cues for a clip window, shift to 00:00:00 |
| `corekit.render_hardsubs` | Burn Chinese SRT + first-second title overlay into final MP4 |
| `corekit.ffmpeg_locator` | Resolve ffmpeg path and detect best available H.264/AAC encoders |

## Clip Selection Criteria

The playbooks define what makes a strong candidate:

- **Length**: 20s – 3min, one core idea per clip
- **Hook**: compelling opening line within first 3 seconds
- **Closure**: thought must complete — never cut mid-sentence
- **Standalone**: understandable without watching the full source
- **Density**: favor sharp claims, contrarian takes, actionable insights, emotional peaks

Candidate count scales with source length:

| Source Duration | Target Candidates |
|-----------------|-------------------|
| < 20 min | 5 – 8 |
| 20 – 60 min | 8 – 12 |
| > 60 min | 10 – 15 |

## ffmpeg Compatibility

AutoCliper adapts to whatever ffmpeg is available:

| Capability | Preferred | Fallback |
|------------|-----------|----------|
| Subtitle rendering | `subtitles=` filter (libass) | `drawtext` chain per cue (libfreetype) |
| Video encoding | `libx264` | `h264_videotoolbox` (macOS) → `libopenh264` |
| Audio encoding | `aac` | `aac_at` (macOS AudioToolbox) |

No manual configuration needed — detection happens at runtime.

## Requirements

- **Python** 3.9+
- **yt-dlp** — `pip install yt-dlp` or `brew install yt-dlp`
- **ffmpeg** — any build with libfreetype (libass optional)

## Project Structure

```
AutoCliper.AI/
├── SKILL.md                        # agent skill definition
├── corekit/                        # core processing modules
│   ├── fetch_source.py
│   ├── subtitle_to_json.py
│   ├── cut_video.py
│   ├── window_subtitles.py
│   ├── render_hardsubs.py
│   └── ffmpeg_locator.py
├── playbooks/                      # selection & analysis rules
│   ├── clip-contract.md            # selected_clips.json schema
│   └── content-analysis-playbook.md
└── LICENSE
```

## License

MIT
