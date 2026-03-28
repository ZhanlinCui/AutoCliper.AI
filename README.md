# YouTube Shorts ZH

将任意 YouTube 长视频（访谈、演讲、播客、教程）自动切割为多条带中文字幕的短视频，适合 TikTok / 抖音 / YouTube Shorts / Instagram Reels。

## ✨ 特性

- **全自动流水线**：下载 → 字幕提取 → 转录分析 → 片段精选 → 切片 → 翻译 → 烧录
- **智能选段**：基于内容分析自动挑选高传播力片段，支持用户审核后导出
- **中文硬字幕**：自动翻译为简体中文并烧录进视频，含 1 秒标题 overlay
- **自适应数量**：根据视频时长自动调整片段数量（<20min→5-8, 20-60min→8-12, >60min→10-15）
- **竖版可选**：支持 9:16 竖版裁剪输出
- **自包含**：内置下载器，不依赖外部路径

## 📋 前置要求

- Python 3.9+
- `yt-dlp`：`pip3 install yt-dlp` 或 `brew install yt-dlp`
- `ffmpeg`：`brew install ffmpeg`

## 🚀 使用方法

### 作为 OpenClaw Skill

1. 将本仓库放入 `~/.qclaw/skills/youtube-shorts-zh/`
2. 发送 YouTube 链接给 AI Agent
3. Agent 自动执行完整流水线
4. 审核候选片段列表后，选择要导出的 ID

### 手动运行脚本

```bash
cd youtube-shorts-zh

# 1. 下载视频 + 字幕
PYTHONPATH="$PWD" python3 -m scripts.download_youtube "<YouTube_URL>" ./work/source/

# 2. 解析字幕
PYTHONPATH="$PWD" python3 -m scripts.srt_to_json ./work/source/*.en.srt ./work/analysis/transcript.json

# 3. 切片
PYTHONPATH="$PWD" python3 -m scripts.clip_video ./work/source/*.mp4 <start_sec> <end_sec> ./work/clips/01/clip.mp4

# 4. 窗口化字幕
PYTHONPATH="$PWD" python3 -m scripts.window_srt ./work/source/*.en.srt <start_sec> <end_sec> ./work/clips/01/clip.en.srt

# 5. 烧录中文字幕 + 标题
PYTHONPATH="$PWD" python3 -m scripts.burn_subtitles ./work/clips/01/clip.mp4 ./work/clips/01/clip.zh.srt ./work/clips/01/clip.hardsub.mp4 --title "标题"
```

## 📁 文件结构

```
youtube-shorts-zh/
├── SKILL.md              # Agent 指令文件
├── scripts/
│   ├── download_youtube.py   # yt-dlp 封装（cookies + 字幕 + 视频）
│   ├── srt_to_json.py        # SRT → JSON 解析器
│   ├── clip_video.py         # 视频片段切割
│   ├── window_srt.py         # 字幕时间窗口提取
│   ├── burn_subtitles.py     # 字幕 + 标题烧录
│   └── _ffmpeg.py            # ffmpeg 路径解析器
├── references/
│   ├── clip-schema.md        # selected_clips.json 的 JSON Schema
│   └── analysis-prompt.md    # 分析 + 翻译 prompt 参考
└── LICENSE
```

## 🎬 输出结构

```
work/<video-slug>/
├── source/
│   ├── original.mp4
│   └── original.en.srt
├── analysis/
│   ├── transcript.json
│   ├── selected_clips.json
│   ├── candidate-review.txt
│   └── clip-packaging.txt
└── clips/
    └── 01-<slug>/
        ├── clip.mp4
        ├── clip.en.srt
        ├── clip.zh.srt
        ├── clip.hardsub.mp4
        └── metadata.txt
```

## 🔧 选段规则

**优选：**
- 20秒 - 3分钟，一个清晰的观点
- 前 3 秒内有强有力的开场
- 自包含（不需要额外上下文）
- 信息密集、观点鲜明、反直觉、有记忆点

**排除：**
- 寒暄、赞助商口播、长篇铺垫
- 依赖前文语境才能理解的片段
- 思绪未完整表达就中断的片段

## 🌐 翻译规则

- 翻译为自然口语化的简体中文
- 保留时间戳，仅在必要时微调
- 准确保留人名、数字、产品名、引述
- 宁可字幕稍多，不可过度压缩

## 📄 License

MIT