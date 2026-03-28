---
name: youtube-shorts-zh
description: |
  Convert any long YouTube video (interview, talk, podcast, keynote, tutorial) into multiple short clips with Chinese hard subtitles and attention-grabbing titles.
  Triggers: YouTube URL + short clips / shorts / 切短视频 / 短片 / 中文字幕 / hard subtitles / 切片.
  Downloads video + subtitles, analyzes transcript, selects strong standalone moments, cuts clips, translates to Chinese, burns subtitles + title overlay.
  Outputs review-ready candidate list for user approval before final export.
---

# YouTube Shorts ZH

Convert a long YouTube video into 5-15 Chinese-subtitled short clips ready for TikTok / Douyin / Shorts / Reels.

## Prerequisites

Verify before starting:
- `yt-dlp` installed (`pip3 install yt-dlp` or `brew install yt-dlp`)
- `ffmpeg` installed (`brew install ffmpeg` or via `imageio-ffmpeg` fallback)
- Run all scripts with `PYTHONPATH="$PWD"`: `python3 -m scripts.<name>`

## Workflow

### 1. Download

Run `download_youtube.py <url> <output_dir>`:
- Prefers browser Chrome cookies; refresh if expired
- Downloads English subtitles (falls back to `zh-Hans` if unavailable)
- Downloads MP4 via Android client path (more reliable)

### 2. Parse & Deduplicate Subtitles

Run `srt_to_json.py <input.srt> <output.json>` and save to `analysis/transcript.json`.

**Important:** Auto-generated subtitles often contain heavy duplication (the same phrase split across multiple cues). When reading `transcript.json`, merge consecutive cues with overlapping text before analysis. This reduces the effective transcript size by 2-3x and speeds up analysis significantly.

### 3. Analyze Transcript

Read [references/clip-schema.md](references/clip-schema.md) for the JSON schema.
Read [references/analysis-prompt.md](references/analysis-prompt.md) for analysis prompts.

Analyze in passes:
1. Scan for dense, memorable, or surprising lines
2. Re-read each candidate with neighbors for clean boundaries
3. Verify first line hooks, final line completes the thought
4. Assign title, timestamps, two-sentence summary

Write results to `analysis/selected_clips.json` and `analysis/candidate-review.txt`.

### 4. User Review

Present candidates in a table:
| ID | Time | Duration | Title | Summary |

Let user pick clip IDs to export. If user says "proceed without review", pick the strongest set yourself.

### 5. Export Each Clip

For each chosen clip:
1. Cut: `clip_video.py <input.mp4> <start_sec> <end_sec> <output.mp4>`
2. Window subtitles: `window_srt.py <input.srt> <start_sec> <end_sec> <output.srt>`
3. Translate clip-local SRT to simplified Chinese (or clean if already Chinese)
4. Burn: `burn_subtitles.py <input.mp4> <zh.srt> <output.mp4> --title "<TITLE>" [--fontfile <path>]`
5. Write `metadata.txt` with title + 140-char description

Compile all packaging copy into `analysis/clip-packaging.txt`.

### 6. (Optional) Vertical Crop

If user requests vertical shorts, crop after the core pipeline using ffmpeg:
`-vf "crop=ih*9/16:ih,scale=1080:1920"` or similar.

## Performance Notes

- **Parallelize clip cutting**: Run all `clip_video.py` calls in parallel (background `&` + `wait`) to cut 7+ clips simultaneously.
- **Parallelize window_srt**: Same approach — all window extractions can run in parallel.
- **Parallelize burn**: All `burn_subtitles.py` calls can also run in parallel.
- **Deduplicate before analysis**: Auto-caption SRT files often have 3-4x redundancy. Merge consecutive duplicate cues before analyzing to dramatically reduce context usage and processing time.
- **Use sub-agents for translation**: When translating 7+ clips, spawn sub-agents to translate SRT files in parallel instead of serial processing.

## Selection Rules

**Target count:**
- Videos < 20 min: 5-8 clips
- Videos 20-60 min: 8-12 clips
- Videos > 60 min: 10-15 clips
Adjust based on material density; default failure mode = "too few candidates."

**Prefer clips that:**
- 20s to 3 minutes, one clear idea
- Strong opening within first 3 seconds
- Self-contained (no heavy prior context needed)
- Informative, opinionated, counterintuitive, motivating, or quotable
- Complete thought by end (never mid-sentence)

**Reject segments that are:**
- Filler, greetings, sponsor reads, long digressions
- Context-dependent (need 5 min of prior explanation)
- Setup without payoff

When extending boundaries for a clean ending, allow overlap but avoid heavy duplication with adjacent clips.

## Translation Rules

- Translate into natural spoken Simplified Chinese
- Preserve timestamps; only rebalance for readability
- Keep names, numbers, products, quoted phrases accurate
- Default failure mode = slightly too many subtitle cues, not too few
- If source is already Chinese, keep it; only clean obvious duplication

## Packaging Rules

**Title:** Short, sharp, clickable. 12 Chinese characters ideal for overlay. May be provocative but must be faithful to content.

**Description** (under 140 Chinese characters): who is speaking, source show/topic, key claim or takeaway.

Write per-clip `metadata.txt` and compile into `analysis/clip-packaging.txt`.

## File Layout

```
work/<video-slug>/
  source/
    original.mp4
    original.<lang>.srt
  analysis/
    transcript.json
    selected_clips.json
    candidate-review.txt
    clip-packaging.txt
  clips/
    01-<slug>/
      clip.mp4
      clip.en.srt       (if source was English)
      clip.zh.srt
      clip.hardsub.mp4
      metadata.txt
```

## Scripts

All in `scripts/`:
- `download_youtube.py` - yt-dlp wrapper, cookies + subtitles + video
- `srt_to_json.py` - SRT to JSON parser
- `clip_video.py` - Cut video segment (re-encoded MP4)
- `window_srt.py` - Extract subtitle window, shift to 00:00:00
- `burn_subtitles.py` - Burn Chinese SRT + title overlay via ffmpeg
- `_ffmpeg.py` - ffmpeg path resolver (system or imageio-ffmpeg fallback)

## References

- [clip-schema.md](references/clip-schema.md) - JSON schema for selected_clips.json
- [analysis-prompt.md](references/analysis-prompt.md) - Analysis + translation prompts

## Error Handling

If blocked, report the exact issue:
- Stale cookies → refresh browser login
- Missing subtitles → try `--write-auto-sub` fallback
- Missing ffmpeg → install via brew or pip
- Low transcript quality → inform user, proceed with best-effort

## Output Contract

Return:
- Source asset folder path
- Candidate clip list (timestamps, duration, title, summaries)
- Packaging text file path
- Final `clip.hardsub.mp4` path per exported clip