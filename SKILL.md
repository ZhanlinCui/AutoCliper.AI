---
name: autocliper-ai
description: |
  Turn any long YouTube interview, talk, or podcast into high-retention Chinese short clips for Shorts/Reels/Douyin/TikTok.
  Triggers: YouTube URL + short clips / 切片 / 短视频 / 中文字幕 / hard subtitles.
  Pipeline: source fetch -> subtitle parsing -> candidate analysis -> user review -> clip export -> subtitle burn.
---

# AutoCliper.AI Skill

Convert one long YouTube video into 5-15 short clips with Chinese packaging and hard subtitles.

## Prerequisites

- `yt-dlp`
- `ffmpeg` (or `imageio-ffmpeg` fallback)
- Run with `PYTHONPATH="$PWD"` and `python3 -m corekit.<module>`

## Recommended Workspace Layout

```text
studio/<video-slug>/
  intake/
    raw.mp4
    raw.<lang>.srt
  intel/
    transcript.json
    selected_clips.json
    candidate-board.md
    packaging-copy.md
  exports/
    01-<slug>/
      clip.mp4
      clip.src.srt
      clip.zh.srt
      clip.hardsub.mp4
      metadata.txt
```

## Workflow

### 1) Fetch Source Assets

```bash
PYTHONPATH="$PWD" python3 -m corekit.fetch_source "<YouTube_URL>" "studio/<slug>/intake"
```

### 2) Convert SRT to JSON

```bash
PYTHONPATH="$PWD" python3 -m corekit.subtitle_to_json "studio/<slug>/intake/raw.en.srt" "studio/<slug>/intel/transcript.json"
```

### 3) Analyze and Propose Candidates

Read:
- [playbooks/clip-contract.md](playbooks/clip-contract.md)
- [playbooks/content-analysis-playbook.md](playbooks/content-analysis-playbook.md)

Output:
- `studio/<slug>/intel/selected_clips.json`
- `studio/<slug>/intel/candidate-board.md`

### 4) User Review

Show a table:
| ID | Time | Duration | Title | Summary |

Ask user to choose IDs, unless user says to auto-pick.

### 5) Batch Export (Enhanced)

Use the manifest exporter for parallel cut + subtitle window:

```bash
PYTHONPATH="$PWD" python3 -m corekit.export_manifest \
  "studio/<slug>/intake/raw.mp4" \
  "studio/<slug>/intake/raw.en.srt" \
  "studio/<slug>/intel/selected_clips.json" \
  "studio/<slug>/exports" \
  --workers 6
```

This generates:
- `clip.mp4`
- `clip.src.srt`
- `intel/export-report.json`

### 6) Translate and Burn

For each clip:
1. Translate `clip.src.srt` -> `clip.zh.srt`
2. Burn:

```bash
PYTHONPATH="$PWD" python3 -m corekit.render_hardsubs \
  "studio/<slug>/exports/01-<slug>/clip.mp4" \
  "studio/<slug>/exports/01-<slug>/clip.zh.srt" \
  "studio/<slug>/exports/01-<slug>/clip.hardsub.mp4" \
  --title "你的标题"
```

You can also rerun exporter with `--render-if-zh` to bulk render existing `clip.zh.srt`.

## Clip Selection Rules

- Clip length: 20s to 180s (can stretch to 3 min if payoff is strong)
- One clip = one clean idea
- Hook in first 3 seconds
- Must end on a complete thought
- Prefer information density, strong claims, contrarian takes, emotional moments
- Reject greetings, sponsor reads, filler, context-heavy setup

## Translation Rules

- Spoken Simplified Chinese, natural rhythm
- Keep names, numbers, products, and key claims accurate
- Keep timestamps stable; only light cue rebalance
- If source is already Chinese, clean noise/duplication only

## Packaging Rules

- Overlay title: <= 15 Chinese characters, sharp and faithful
- Description: <= 140 Chinese characters, include speaker + source + key takeaway
- Write per clip `metadata.txt` and full `packaging-copy.md`

## Modules

- `corekit.fetch_source` - download video/subtitles from YouTube
- `corekit.subtitle_to_json` - parse SRT into JSON cues
- `corekit.window_subtitles` - extract local subtitle windows
- `corekit.cut_video` - cut MP4 segments
- `corekit.render_hardsubs` - burn subtitles and first-second title
- `corekit.export_manifest` - parallel batch export from selected_clips manifest
- `corekit.ffmpeg_locator` - resolve ffmpeg executable

## Output Contract

Return:
- source asset directory path
- candidate list with timestamps/title/two-line summary
- packaging file path
- final `clip.hardsub.mp4` paths

If blocked, report exact blocker: stale cookies, subtitle not available, ffmpeg missing, low-quality transcript.
