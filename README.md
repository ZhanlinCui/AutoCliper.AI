# AutoCliper.AI

把一条长视频，变成一组可发布的高传播短视频。

AutoCliper.AI 专注于一个目标：  
将 YouTube 访谈/播客/演讲快速拆解为多条 **中文硬字幕短视频**，直接用于 Shorts、抖音、TikTok、Reels。

## 为什么它更适合做增长内容

- 高效：拉取素材、字幕解析、候选切片、批量导出一条链路完成
- 可控：先出候选清单给你审核，再导出，不盲切
- 可扩展：支持并行批量切片，适合 10+ clip 的生产场景
- 可传播：内置标题与文案规范，天然面向短视频平台分发

## 核心能力

- YouTube 下载（视频 + 字幕，英文优先，中文兜底）
- 字幕转结构化 JSON，便于语义分析
- 候选片段筛选规范（强开场、完整收尾、信息密度）
- 批量导出：并行切视频 + 并行窗口字幕
- 中文字幕硬烧录 + 首秒标题 overlay

## 快速开始

```bash
# 1) 下载素材
PYTHONPATH="$PWD" python3 -m corekit.fetch_source "<YOUTUBE_URL>" "studio/<slug>/intake"

# 2) 字幕结构化
PYTHONPATH="$PWD" python3 -m corekit.subtitle_to_json \
  "studio/<slug>/intake/raw.en.srt" \
  "studio/<slug>/intel/transcript.json"

# 3) 按 playbook 生成 selected_clips.json（由 Agent 分析）

# 4) 并行批量导出
PYTHONPATH="$PWD" python3 -m corekit.export_manifest \
  "studio/<slug>/intake/raw.mp4" \
  "studio/<slug>/intake/raw.en.srt" \
  "studio/<slug>/intel/selected_clips.json" \
  "studio/<slug>/exports" \
  --workers 6

# 5) 单条烧录（可循环/并行）
PYTHONPATH="$PWD" python3 -m corekit.render_hardsubs \
  "studio/<slug>/exports/01-<slug>/clip.mp4" \
  "studio/<slug>/exports/01-<slug>/clip.zh.srt" \
  "studio/<slug>/exports/01-<slug>/clip.hardsub.mp4" \
  --title "你的标题"
```

## 目录结构（品牌化命名）

```text
AutoCliper.AI/
├── SKILL.md
├── corekit/
│   ├── fetch_source.py
│   ├── subtitle_to_json.py
│   ├── cut_video.py
│   ├── window_subtitles.py
│   ├── render_hardsubs.py
│   ├── export_manifest.py
│   └── ffmpeg_locator.py
├── playbooks/
│   ├── clip-contract.md
│   └── content-analysis-playbook.md
└── LICENSE
```

## 输出结构

```text
studio/<video-slug>/
├── intake/
│   ├── raw.mp4
│   └── raw.<lang>.srt
├── intel/
│   ├── transcript.json
│   ├── selected_clips.json
│   ├── candidate-board.md
│   ├── packaging-copy.md
│   └── export-report.json
└── exports/
    └── 01-<slug>/
        ├── clip.mp4
        ├── clip.src.srt
        ├── clip.zh.srt
        ├── clip.hardsub.mp4
        └── metadata.txt
```

## 建议的选段标准

- 20 秒到 3 分钟，一条 clip 一个核心观点
- 前 3 秒就有钩子
- 结尾必须完整，不截断
- 优先反直觉观点、可执行方法论、情绪强记忆点

## 安装与依赖

- Python 3.9+
- `yt-dlp`
- `ffmpeg`（或 `imageio-ffmpeg` 兜底）

## License

MIT
