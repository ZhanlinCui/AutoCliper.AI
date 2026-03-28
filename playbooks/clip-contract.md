# Clip Contract (AutoCliper.AI)

This document defines the exact JSON schema for `selected_clips.json`. Any agent writing this file must follow this contract precisely.

---

## Schema

`selected_clips.json` must be a JSON array of objects. Each object represents one clip candidate.

```json
[
  {
    "id": "clip-01",
    "start": "00:12:03,000",
    "end": "00:13:22,500",
    "start_seconds": 723.0,
    "end_seconds": 802.5,
    "duration_seconds": 79.5,
    "title": "AI三年内取代人类？",
    "summary": [
      "Sam Altman 谈到 AGI 可能在三年内实现。",
      "他认为大多数人严重低估了 AI 的发展速度。"
    ],
    "reason": "强钩子 + 反直觉观点 + 完整收尾，适合引发讨论",
    "score": {
      "hook": 5,
      "clarity": 4,
      "standalone": 5,
      "payoff": 4
    }
  }
]
```

---

## Field Definitions

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| `id` | string | yes | Unique, stable, zero-padded. Format: `clip-01`, `clip-02`, ... `clip-15`. |
| `start` | string | yes | SRT timestamp format: `HH:MM:SS,mmm`. Must match the source SRT cue boundary. |
| `end` | string | yes | SRT timestamp format: `HH:MM:SS,mmm`. Must land AFTER the speaker finishes the last word. |
| `start_seconds` | float | yes | Decimal seconds corresponding to `start`. Used by `corekit.cut_video`. |
| `end_seconds` | float | yes | Decimal seconds corresponding to `end`. Used by `corekit.cut_video`. |
| `duration_seconds` | float | yes | `end_seconds - start_seconds`. Must be between 20 and 180. Stretch to 180+ only with explicit justification in `reason`. |
| `title` | string | yes | Chinese. **Target ≤ 12 characters** (hard max 15). This becomes the on-screen overlay. |
| `summary` | array of 2 strings | yes | Exactly two sentences in Chinese. Sentence 1: what is discussed. Sentence 2: why it matters. |
| `reason` | string | yes | Brief internal justification for why this clip was selected. Not shown to the end viewer. |
| `score` | object | yes | Four integer fields (1–5): `hook`, `clarity`, `standalone`, `payoff`. |

---

## Scoring Rubric

| Dimension | What it measures | 1 | 3 | 5 |
|-----------|-----------------|---|---|---|
| `hook` | Does the opening grab attention? | Bland, confusing, or requires context | Clear start but not gripping | Immediate "wait, what?" reaction |
| `clarity` | Is it one clean idea? | Multiple tangled topics | One idea with minor tangents | Laser-focused single idea |
| `standalone` | Can it stand alone? | Needs the previous 5 minutes | Mostly self-contained | Fully independent |
| `payoff` | Does the ending deliver? | Trails off or ends mid-thought | Reasonable conclusion | Memorable, quotable, or actionable |

**Ranking formula**: `total = hook × 0.35 + clarity × 0.25 + standalone × 0.2 + payoff × 0.2`

---

## Quality Gates

Every clip in `selected_clips.json` must pass ALL of these gates:

1. **Opening hooks within 3 seconds** — if the first cue is filler, the clip start is wrong.
2. **Ending completes a thought** — re-read the last 3 cues; the speaker must be done.
3. **Understandable without context** — a viewer who opens this clip cold must not be confused.
4. **Not filler** — greetings, sponsor reads, "let me think," extended silences, and Q&A preambles are rejected.
5. **Duration in range** — 20–180 seconds. If > 180, the `reason` field must explicitly justify it.

---

## Edge Cases

### Clip boundaries near a topic transition
If the speaker transitions between topics mid-sentence, end the clip BEFORE the transition. Do not include the start of the next topic.

### Two speakers overlapping
If an interviewer asks a short question and the guest gives a compelling answer, you MAY include both in one clip as long as the question provides context (not just "So what do you think?"). Start the clip at the question if it adds value; otherwise start at the answer.

### Speaker says something wrong or controversial
Include it if it's genuinely what they said and it makes a compelling clip. The `reason` field should note that this is a strong claim. Do not censor — but also do not misrepresent through selective truncation.

### Very long monologue (5+ minutes) with no natural break
Look for micro-conclusions within the monologue — moments where the speaker pauses, summarizes, or delivers a punchline. Cut at those moments. You may extract multiple clips from one long monologue.

### Clip would be perfect at 200 seconds
If a clip genuinely needs 200 seconds to land its payoff, include it. Set `duration_seconds` to the actual value and explain in `reason` why truncating at 180 would ruin it. The pipeline will not reject it — the 180s limit is a preference, not a hard error.

---

## Complete Example

```json
[
  {
    "id": "clip-01",
    "start": "00:12:03,000",
    "end": "00:13:22,500",
    "start_seconds": 723.0,
    "end_seconds": 802.5,
    "duration_seconds": 79.5,
    "title": "AI三年内取代人类？",
    "summary": [
      "Sam Altman 谈到 AGI 可能在三年内实现。",
      "他认为大多数人严重低估了 AI 的发展速度。"
    ],
    "reason": "强钩子开场（'Most people have no idea what's coming'），观点反直觉，结尾完整",
    "score": {
      "hook": 5,
      "clarity": 4,
      "standalone": 5,
      "payoff": 4
    }
  },
  {
    "id": "clip-02",
    "start": "00:25:41,200",
    "end": "00:26:55,800",
    "start_seconds": 1541.2,
    "end_seconds": 1615.8,
    "duration_seconds": 74.6,
    "title": "创业最大的敌人是时机",
    "summary": [
      "他指出 90% 的创业者在错误的时机做了正确的事。",
      "时机比想法更重要，但几乎没人愿意承认这一点。"
    ],
    "reason": "可执行洞察，对创业受众有强吸引力，开场直接进入论点",
    "score": {
      "hook": 4,
      "clarity": 5,
      "standalone": 4,
      "payoff": 5
    }
  }
]
```
