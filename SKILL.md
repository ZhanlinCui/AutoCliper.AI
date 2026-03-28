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
- `ffmpeg` (or `imageio-ffmpeg` fallback; libass is optional — the burn step auto-detects and uses a drawtext fallback)
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
PYTHONPATH="$PWD" python3 -m corekit.subtitle_to_json \
  "studio/<slug>/intake/raw.en.srt" \
  "studio/<slug>/intel/transcript.json"
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

### 5) Export Each Chosen Clip

For each clip in `selected_clips.json`:

#### a) Cut the video segment

```bash
PYTHONPATH="$PWD" python3 -m corekit.cut_video \
  "studio/<slug>/intake/raw.mp4" \
  <start_seconds> <end_seconds> \
  "studio/<slug>/exports/01-<slug>/clip.mp4"
```

#### b) Window the source subtitle

```bash
PYTHONPATH="$PWD" python3 -m corekit.window_subtitles \
  "studio/<slug>/intake/raw.en.srt" \
  <start_seconds> <end_seconds> \
  "studio/<slug>/exports/01-<slug>/clip.src.srt"
```

#### c) Translate `clip.src.srt` → `clip.zh.srt`

Translate the windowed English SRT into simplified Chinese SRT. Preserve timestamps; rewrite into natural spoken Chinese. See Translation Rules below.

#### d) Burn subtitles and title

```bash
PYTHONPATH="$PWD" python3 -m corekit.render_hardsubs \
  "studio/<slug>/exports/01-<slug>/clip.mp4" \
  "studio/<slug>/exports/01-<slug>/clip.zh.srt" \
  "studio/<slug>/exports/01-<slug>/clip.hardsub.mp4" \
  --title "你的标题"
```

IMPORTANT: Always pass the **Chinese** `.zh.srt` file, not the source `.src.srt`.

The burn step auto-detects libass. If libass is unavailable, it renders each subtitle cue via drawtext — no manual workaround needed.

## Clip Selection Rules

- Clip length: 20s to 180s (can stretch to 3 min if payoff is strong)
- One clip = one clean idea
- Hook in first 3 seconds
- Must end on a complete thought
- Prefer information density, strong claims, contrarian takes, emotional moments
- Reject greetings, sponsor reads, filler, context-heavy setup

Count guidance:
- < 20 min video → 5-8 candidates
- 20-60 min → 8-12 candidates
- > 60 min → 10-15 candidates

When in doubt, include more rather than fewer. The user will prune.

## Translation Rules

- Spoken Simplified Chinese, natural rhythm
- Keep names, numbers, products, and key claims accurate
- Keep timestamps stable; only light cue rebalance
- Prefer concise Chinese lines fitting short-form video pacing
- If an English sentence spans multiple cues, rebalance text between neighbors while preserving order
- Do not collapse cue-dense SRT into a tiny summary
- Default: slightly too many cues, not far too few
- If source is already Chinese, clean noise/duplication only

## Packaging Rules

- Overlay title: <= 15 Chinese characters, sharp and faithful
- Description: <= 140 Chinese characters, include speaker + source + key takeaway
- Write per clip `metadata.txt` and full `intel/packaging-copy.md`

## Modules

- `corekit.fetch_source` — download video + subtitles from YouTube
- `corekit.subtitle_to_json` — parse SRT into JSON cues
- `corekit.window_subtitles` — extract local subtitle window for a time range
- `corekit.cut_video` — cut MP4 segment by start/end seconds
- `corekit.render_hardsubs` — burn Chinese subtitles and first-second title (auto libass/drawtext)
- `corekit.ffmpeg_locator` — resolve ffmpeg executable

## Output Contract

Return:
- source asset directory path
- candidate list with timestamps/title/two-line summary
- packaging file path
- final `clip.hardsub.mp4` paths

If blocked, report exact blocker: stale cookies, subtitle not available, ffmpeg missing, low-quality transcript.
