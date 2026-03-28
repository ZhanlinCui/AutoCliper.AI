# Clip Contract (AutoCliper.AI)

`selected_clips.json` must be an array of objects:

```json
[
  {
    "id": "clip-01",
    "start": "00:12:03,000",
    "end": "00:13:22,500",
    "start_seconds": 723.0,
    "end_seconds": 802.5,
    "duration_seconds": 79.5,
    "title": "一句能钩住人的工作标题",
    "summary": [
      "第一句说明这段在讲什么。",
      "第二句说明为什么值得切出来。"
    ],
    "reason": "为什么它适合做短视频分发",
    "score": {
      "hook": 4,
      "clarity": 5,
      "standalone": 4,
      "payoff": 5
    }
  }
]
```

Rules:
- `id`: unique, stable, zero-padded (e.g. `clip-01`)
- `summary`: exactly two sentences
- `start` / `end`: SRT timestamp format `HH:MM:SS,mmm`
- `start_seconds` / `end_seconds`: float
- `duration_seconds`: float, prefer 20-180 (hard cap 180 unless explicitly approved)
- `title`: Chinese, under 15 characters
- `reason`: brief internal justification (not shown to end viewer)
- `score.hook|clarity|standalone|payoff`: integer 1-5

Quality gates:
- Opening must hook within first 3 seconds
- Ending must complete a thought
- Segment must be understandable without missing context
