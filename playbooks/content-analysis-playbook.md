# Content Analysis Playbook

This playbook defines how to analyze a transcript and produce clip candidates. Follow it step by step — do not shortcut the multi-pass process.

---

## Stage 1 — Candidate Mining (Pass 1 + 2)

### Pass 1: Skim and Flag

Read through the full `transcript.json` (produced by `corekit.subtitle_to_json`). You are looking for **stretches** of consecutive cues that contain:

- Sharp claims or surprising assertions
- Counterintuitive or contrarian takes
- Emotionally memorable lines — anger, excitement, disbelief, humor
- Concise explanations of complex ideas
- Actionable advice, frameworks, or mental models
- Quotable one-liners or punchlines
- Confessional or vulnerable moments
- Strong disagreements between speakers

Flag each stretch with approximate start/end cue indices. Be generous — flag anything that might work. You will refine later.

**How many to flag**: For a 1-hour interview, you should flag **at least 15–20 raw stretches** before filtering. If you only found 5, you are being too conservative. Go back and look again.

### Pass 2: Boundary Refinement

For each flagged stretch:

1. **Read 5–10 cues before** the flagged start. Does the speaker need any of this context for the clip to make sense? If yes, extend the start backward.

2. **Read 5–10 cues after** the flagged end. Does the thought trail off? Is there a punchline or conclusion coming? If yes, extend the end forward.

3. **Check the opening cue**: The first line of the clip must work as a hook. If the first cue is filler ("So, you know, like..."), shift the start to the next substantive line.

4. **Check the closing cue**: The last line must resolve the thought. Read the final cue out loud in your head — does it feel like an ending? If it ends mid-sentence or mid-thought, extend until the thought completes.

5. **Record exact timestamps**: Use the `start_seconds` and `end_seconds` from the JSON cues. The clip boundaries are the `start_seconds` of the first included cue and the `end_seconds` of the last included cue.

---

## Stage 2 — Completeness Check (Pass 3)

For each candidate from Stage 1, verify ALL of the following. If any check fails, fix it or drop the candidate.

- [ ] **Duration**: 20–180 seconds. Can stretch to 3 minutes only if the payoff genuinely requires it.
- [ ] **One idea**: The clip conveys exactly one core idea, not two interleaved topics.
- [ ] **Hook in 3 seconds**: A viewer who sees only the first 3 seconds would want to keep watching.
- [ ] **Complete thought**: The clip ends on a resolved thought, not a cliffhanger that requires the next segment.
- [ ] **Standalone**: A viewer who has NOT seen the full interview can understand this clip without confusion.
- [ ] **Not filler**: This is NOT a greeting, sponsor read, Q&A preamble, "let me think about that," long pause, or digression that goes nowhere.
- [ ] **Not a fragment**: This is a complete argument or story, not just a strong sentence surrounded by weak context.
- [ ] **End timestamp check**: Re-read the last 3 cues. Is the speaker actually done talking? Does the timestamp land AFTER the final word, not in the middle of it?

---

## Stage 3 — Score and Rank (Pass 4)

Score each surviving candidate on four dimensions, 1–5:

| Dimension | 1 (weak) | 3 (acceptable) | 5 (strong) |
|-----------|----------|-----------------|------------|
| `hook` | Opening is bland or confusing | Opening is clear but not gripping | Opening creates immediate curiosity or tension |
| `clarity` | Multiple topics jumbled | One main idea but some tangents | One razor-sharp idea, no ambiguity |
| `standalone` | Requires prior context to understand | Mostly self-contained with minor gaps | Fully understandable in isolation |
| `payoff` | Ends weakly or mid-thought | Ends with a reasonable conclusion | Ends with a memorable, quotable, or actionable takeaway |

**Ranking formula**:

```
total = hook × 0.35 + clarity × 0.25 + standalone × 0.2 + payoff × 0.2
```

Sort candidates by `total` descending. This ranking determines the default export order if the user says "auto-pick."

---

## Stage 4 — Write Outputs

### selected_clips.json

Write to `studio/<slug>/intel/selected_clips.json`. Must follow the schema in [clip-contract.md](clip-contract.md) exactly. Include ALL candidates that passed Stage 2, not just the top few — the user decides which to export.

### candidate-board.md

Write to `studio/<slug>/intel/candidate-board.md` using this format:

```markdown
# Candidate Board

| ID | Time | Duration | Score | Title | Summary |
|----|------|----------|-------|-------|---------|
| clip-01 | 00:12:03 → 00:13:22 | 1m 19s | 4.3 | AI终将取代一切？ | Sam Altman 认为 AGI 三年内到来。大多数人严重低估了 AI 的发展速度。 |
| clip-02 | 00:25:41 → 00:26:55 | 1m 14s | 4.1 | 创业者最大的错误 | 他指出 90% 的创业者在错误的时机做了正确的事。时机比想法更重要。 |
```

Each row must have:
- **ID**: `clip-XX` (zero-padded)
- **Time**: `HH:MM:SS → HH:MM:SS`
- **Duration**: human-readable (e.g., `1m 19s`, `45s`, `2m 30s`)
- **Score**: weighted total to one decimal place
- **Title**: one provocative Chinese title, **≤ 12 characters**
- **Summary**: exactly **two sentences** in Chinese
  - Sentence 1: what is being discussed in this clip
  - Sentence 2: why it matters, what the takeaway is, or why it's worth watching

---

## Handling Auto-Generated (Noisy) Subtitles

YouTube auto-captions are often noisy. Apply these rules:

1. **Repeated fragments**: Auto-captions frequently repeat the same phrase across consecutive cues (e.g., cue 42: "I think the", cue 43: "I think the problem is"). When determining clip text, treat the last occurrence as authoritative.

2. **Missing punctuation**: Auto-captions rarely have periods or commas. Use content and pauses (gaps between cues) to infer sentence boundaries.

3. **Misheard words**: Names, technical terms, and numbers are often wrong in auto-captions. If you can confidently infer the correct word from context, use it. If you cannot, preserve the auto-caption text and note the uncertainty.

4. **Filler words**: Auto-captions capture every "um," "uh," "you know," "like." Ignore these when evaluating clip quality, but they will naturally be cleaned during Chinese translation.

5. **Do not invent**: If the auto-caption is genuinely unclear and you cannot infer the meaning, do not fabricate content. Skip the candidate or note the quality issue.

---

## Translation Guide

When translating `clip.src.srt` → `clip.zh.srt`:

### Core Principles

1. **Sound like speech, not writing**. The output will be displayed as video subtitles for a Chinese audience watching short-form content. Use spoken Chinese phrasing.

2. **Faithfulness over fluency**. If there is a conflict between sounding natural and preserving the speaker's meaning, preserve the meaning.

3. **Preserve the original cadence**. If the English SRT has 30 cues, the Chinese SRT should have roughly 25–35 cues. Do not collapse 30 English cues into 5 Chinese cues.

### Specific Rules

| Rule | Do | Don't |
|------|----|-------|
| Timestamps | Keep them exactly as in the source SRT | Shift timestamps arbitrarily |
| Named entities | "Sam Altman" stays "Sam Altman" | Transliterate to "萨姆·奥特曼" unless the name is widely known in Chinese by its Chinese form |
| Numbers | "3 billion" → "30亿" | "30亿" → "三十亿" (use digits for impact) |
| Cue merging | Merge two cues only if the English text is a broken fragment that makes no sense alone | Merge because you want fewer lines |
| Duplicate fragments | Drop the earlier duplicate, keep the later one | Keep both duplicates |
| Long English cue | Split into two Chinese cues at a natural pause point | Leave as one cue that scrolls too fast |
| Already Chinese source | Clean obvious noise only | Re-translate from Chinese to Chinese |

### Quality Check

After translation, verify:
- [ ] Cue count is within 80–120% of the source cue count
- [ ] No timestamps were accidentally shifted
- [ ] Named entities are preserved correctly
- [ ] The first cue in Chinese still works as a hook
- [ ] The last cue in Chinese still resolves the thought

---

## Title and Description Generation

### Title (per clip)

- **Target: ≤ 12 Chinese characters** — this is the hard constraint for the first-second overlay. At font size 48 on a 1280×720 frame, 12 characters fit cleanly on one line. 15 characters is the absolute maximum.
- Must be clickable and opinionated
- May be provocative, contrarian, or tension-creating
- Must be faithful to the speaker's actual meaning — do not misrepresent
- Should create curiosity ("what did they say?") or tension ("that can't be right")

Good examples:
- `AI三年内取代人类？` (10 chars)
- `创业最大的敌人是时机` (9 chars)
- `别再学编程了` (6 chars)
- `马斯克错了` (5 chars)

Bad examples:
- `关于人工智能未来发展的一些看法` (14 chars — too long, too bland)
- `很有意思的观点` (7 chars — says nothing)
- `Sam讨论AI` (7 chars — not Chinese-audience-friendly)

### Description (per clip)

- ≤ 140 Chinese characters
- Must include:
  - Who is speaking (e.g., "Sam Altman")
  - What show/interview this is from (e.g., "Lex Fridman 播客")
  - What topic is discussed (e.g., "AGI 的时间表")
  - What the key claim or takeaway is (e.g., "大多数人严重低估了 AI 的发展速度")

Example:
> Sam Altman 在 Lex Fridman 播客中谈到 AGI 的时间表——他认为大多数人严重低估了 AI 的发展速度，未来三年将改变一切。

---

## Candidate Board Template (copy-paste ready)

```markdown
# Candidate Board — <video title>

**Source**: <YouTube URL>
**Duration**: <total video duration>
**Subtitle language**: <en / zh-Hans / etc.>
**Candidates**: <count>

| ID | Time | Duration | Score | Title | Summary |
|----|------|----------|-------|-------|---------|
| clip-01 | HH:MM:SS → HH:MM:SS | Xm Xs | X.X | ≤12字标题 | 句1：在讲什么。句2：为什么值得看。 |
```
