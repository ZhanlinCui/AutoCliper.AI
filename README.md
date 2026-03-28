<p align="center">
  <strong>AutoCliper.AI</strong><br>
  <em>One long video in. A dozen ready-to-post short clips out.</em><br>
  <em>自动剪辑长视频到短视频，可以直接发布，标题，字幕全部自动生成</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.9+-blue?style=flat-square" alt="Python 3.9+">
  <img src="https://img.shields.io/badge/ffmpeg-required-orange?style=flat-square" alt="FFmpeg">
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="MIT">
  <img src="https://img.shields.io/badge/libass-optional-lightgrey?style=flat-square" alt="libass optional">
</p>

<p align="center">
  <a href="#english">English</a> · <a href="#中文">中文</a>
</p>

---

<a id="english"></a>

## English

AutoCliper.AI takes a YouTube interview, podcast, or talk and turns it into **5–15 Chinese-subtitled short clips** — packaged with titles, descriptions, and hard-burned subtitles — ready for Shorts, Douyin, TikTok, and Reels.

### Why AutoCliper

| Pain Point | AutoCliper Solution |
|---|---|
| Manually scrubbing through hour-long interviews | AI-driven transcript analysis surfaces the strongest moments |
| Subtitle rendering breaks on different ffmpeg builds | Runtime detection: **libass** when available, **drawtext** chain as universal fallback |
| H.264 encoder mismatch across environments | Auto-selects `libx264` → `h264_videotoolbox` → `libopenh264` |
| Cutting clips loses subtitle sync | Windowed SRT extraction preserves frame-accurate timing |
| No idea what makes a good short clip | Built-in playbooks score candidates on hook, clarity, standalone, and payoff |

### Pipeline

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

### Quick Start

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

### Workspace Layout

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

### Corekit Modules

| Module | Purpose |
|--------|---------|
| `corekit.fetch_source` | Download video + subtitles via yt-dlp (English preferred, Chinese fallback) |
| `corekit.subtitle_to_json` | Parse SRT into JSON with cue index, timestamps, and seconds |
| `corekit.cut_video` | Extract a precise time-range segment as re-encoded MP4 |
| `corekit.window_subtitles` | Slice subtitle cues for a clip window, shift to 00:00:00 |
| `corekit.render_hardsubs` | Burn Chinese SRT + first-second title overlay into final MP4 |
| `corekit.ffmpeg_locator` | Resolve ffmpeg path and detect best available H.264/AAC encoders |

### Clip Selection Criteria

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

### ffmpeg Compatibility

AutoCliper adapts to whatever ffmpeg is available:

| Capability | Preferred | Fallback |
|------------|-----------|----------|
| Subtitle rendering | `subtitles=` filter (libass) | `drawtext` chain per cue (libfreetype) |
| Video encoding | `libx264` | `h264_videotoolbox` (macOS) → `libopenh264` |
| Audio encoding | `aac` | `aac_at` (macOS AudioToolbox) |

No manual configuration needed — detection happens at runtime.

### Requirements

- **Python** 3.9+
- **yt-dlp** — `pip install yt-dlp` or `brew install yt-dlp`
- **ffmpeg** — any build with libfreetype (libass optional)

---

<a id="中文"></a>

## 中文

AutoCliper.AI 做一件事：把 YouTube 上的长访谈、播客、演讲，拆成 **5–15 条带中文硬字幕的短视频**——标题、文案、字幕全部就位，直接可发 Shorts、抖音、TikTok、小红书。

### 为什么选 AutoCliper

| 痛点 | AutoCliper 的解法 |
|------|-------------------|
| 一小时视频要手动翻来翻去找亮点 | AI 逐句分析字幕，自动挖掘最值得切的片段 |
| 不同机器的 ffmpeg 烧字幕动不动报错 | 运行时自动检测：有 **libass** 就用，没有就走 **drawtext** 逐条渲染，通吃所有环境 |
| H.264 编码器五花八门 | 自动选择 `libx264` → `h264_videotoolbox`（macOS）→ `libopenh264` |
| 切完片字幕错位 | 窗口化 SRT 提取，帧级精准对齐 |
| 不知道什么内容适合做短视频 | 内置 Playbook，从钩子、清晰度、独立性、收尾四个维度打分筛选 |

### 工作流程

```
YouTube 链接
    │
    ▼
┌──────────┐    ┌──────────┐    ┌───────────────┐
│ 下载素材  │───▶│ 字幕转JSON │───▶│ Agent 分析字幕 │
│ 视频+字幕 │    │ SRT→结构化 │    │ 生成候选清单   │
└──────────┘    └──────────┘    └───────┬───────┘
                                        │
                                        ▼
                                ┌───────────────┐
                                │  用户审核清单   │
                                │  选择要导出的片段│
                                └───────┬───────┘
                                        │
                  ┌─────────────────────┼─────────────────────┐
                  ▼                     ▼                     ▼
            ┌──────────┐         ┌──────────┐         ┌──────────┐
            │ 切视频    │         │ 切视频    │         │ 切视频    │
            │ 窗口字幕  │         │ 窗口字幕  │         │ 窗口字幕  │
            │ 翻译中文  │         │ 翻译中文  │         │ 翻译中文  │
            │ 烧录字幕  │         │ 烧录字幕  │         │ 烧录字幕  │
            └────┬─────┘         └────┬─────┘         └────┬─────┘
                 ▼                     ▼                     ▼
           成品.hardsub.mp4      成品.hardsub.mp4      成品.hardsub.mp4
```

### 快速开始

```bash
# 1  下载素材（视频 + 字幕）
PYTHONPATH="$PWD" python3 -m corekit.fetch_source \
  "https://youtube.com/watch?v=..." \
  "studio/my-interview/intake"

# 2  字幕结构化（SRT → JSON）
PYTHONPATH="$PWD" python3 -m corekit.subtitle_to_json \
  "studio/my-interview/intake/raw.en.srt" \
  "studio/my-interview/intel/transcript.json"

# 3  Agent 分析字幕 → 生成 selected_clips.json
#    （遵循 playbooks/content-analysis-playbook.md）

# 4  对每个选中的片段执行：

#    切出视频片段
PYTHONPATH="$PWD" python3 -m corekit.cut_video \
  "studio/my-interview/intake/raw.mp4" \
  723.0 802.5 \
  "studio/my-interview/exports/01-ai-will-replace/clip.mp4"

#    提取片段对应的字幕窗口
PYTHONPATH="$PWD" python3 -m corekit.window_subtitles \
  "studio/my-interview/intake/raw.en.srt" \
  723.0 802.5 \
  "studio/my-interview/exports/01-ai-will-replace/clip.src.srt"

#    Agent 翻译 clip.src.srt → clip.zh.srt

#    烧录中文字幕 + 首秒标题
PYTHONPATH="$PWD" python3 -m corekit.render_hardsubs \
  "studio/my-interview/exports/01-ai-will-replace/clip.mp4" \
  "studio/my-interview/exports/01-ai-will-replace/clip.zh.srt" \
  "studio/my-interview/exports/01-ai-will-replace/clip.hardsub.mp4" \
  --title "AI终将取代一切？"
```

### 输出目录

```
studio/<video-slug>/
├── intake/                         # YouTube 原始素材
│   ├── raw.mp4
│   └── raw.<lang>.srt
├── intel/                          # 分析产物
│   ├── transcript.json             # 结构化字幕
│   ├── selected_clips.json         # 切片决策（schema 见 clip-contract.md）
│   ├── candidate-board.md          # 候选清单（供审核）
│   └── packaging-copy.md           # 所有片段的标题 + 文案
└── exports/                        # 每条片段一个文件夹
    └── 01-<slug>/
        ├── clip.mp4                # 裸切片段
        ├── clip.src.srt            # 窗口化源语言字幕
        ├── clip.zh.srt             # 中文翻译字幕
        ├── clip.hardsub.mp4        # 最终成品（硬字幕）
        └── metadata.txt            # 标题 + 文案（用于分发）
```

### 核心模块

| 模块 | 功能 |
|------|------|
| `corekit.fetch_source` | 通过 yt-dlp 下载视频和字幕（英文优先，中文兜底） |
| `corekit.subtitle_to_json` | 将 SRT 解析为带索引、时间戳、秒数的 JSON |
| `corekit.cut_video` | 按精确时间范围切出重编码的 MP4 片段 |
| `corekit.window_subtitles` | 提取片段时间窗口内的字幕，时间轴归零 |
| `corekit.render_hardsubs` | 烧录中文字幕 + 首秒标题叠加层 |
| `corekit.ffmpeg_locator` | 定位 ffmpeg 并检测最优 H.264/AAC 编码器 |

### 选段标准

Playbook 定义了什么是好的候选片段：

- **时长**：20 秒 – 3 分钟，一条一个核心观点
- **钩子**：前 3 秒内必须有吸引人的开场
- **收尾**：观点必须讲完，不在半句话处截断
- **独立性**：不看原视频也能理解
- **密度**：优先选反直觉观点、可执行方法论、情绪强记忆点

候选数量随素材时长递增：

| 素材时长 | 建议候选数 |
|----------|-----------|
| < 20 分钟 | 5 – 8 条 |
| 20 – 60 分钟 | 8 – 12 条 |
| > 60 分钟 | 10 – 15 条 |

### ffmpeg 兼容性

AutoCliper 自动适配各种 ffmpeg 环境：

| 能力 | 首选方案 | 兜底方案 |
|------|---------|---------|
| 字幕渲染 | `subtitles=` 滤镜（需 libass） | `drawtext` 逐条渲染（仅需 libfreetype） |
| 视频编码 | `libx264` | `h264_videotoolbox`（macOS）→ `libopenh264` |
| 音频编码 | `aac` | `aac_at`（macOS AudioToolbox） |

无需手动配置，运行时自动检测。

### 环境要求

- **Python** 3.9+
- **yt-dlp** — `pip install yt-dlp` 或 `brew install yt-dlp`
- **ffmpeg** — 任意包含 libfreetype 的构建版本（libass 可选）

---

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
