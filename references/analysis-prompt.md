# Analysis Prompts

## Stage 1 — Candidate Selection

Scan the full transcript for self-contained moments. For each candidate:

1. **Identify the stretch**: Find a coherent span (20-180s) with a clear arc.
2. **Check independence**: Can someone understand this without watching the full video?
3. **Check opening**: Does the first spoken line hook attention within 3 seconds?
4. **Check ending**: Does the segment end on a completed thought, not mid-sentence?
5. **Clean boundaries**: Extend by a few seconds if needed for context or resolution.

Favor:
- Sharp claims, surprising turns, concise explanations
- Emotionally memorable lines
- Counterintuitive or contrarian takes
- Actionable advice or frameworks

Reject:
- Filler, greetings, sponsor reads
- Context-heavy references requiring prior segments
- Segments that are mostly Q&A preamble without substance
- Long technical explanations with no payoff

**Count guidance:**
- < 20 min video → 5-8 candidates
- 20-60 min → 8-12 candidates
- > 60 min → 10-15 candidates

When in doubt, include more rather than fewer. The user will prune.

## Stage 2 — Review Formatting

For each candidate, present:
- **ID**: `clip-01`, `clip-02`, etc.
- **Time range**: `00:12:03 → 00:13:22` (HH:MM:SS)
- **Duration**: `1m 19s`
- **Title**: One provocative Chinese title (under 15 chars)
- **Summary**: Exactly two sentences in Chinese
  - Sentence 1: what is being discussed
  - Sentence 2: why it matters / what is the takeaway

## Translation Notes

- Translate into natural spoken Simplified Chinese
- Preserve timestamps exactly; only rebalance cues for readability
- Keep named entities, numbers, product names, quoted phrases accurate
- Prefer concise Chinese lines fitting short-form video pacing
- If an English sentence spans multiple cues, rebalance text between neighbors while preserving order
- Do not collapse cue-dense SRT into a tiny summary
- Default: slightly too many cues, not far too few
- If source is already Chinese, keep it and only clean obvious auto-caption duplication

## Title & Description Generation

**Title** (per clip):
- Short, sharp, clickable
- Under 15 Chinese characters for clean overlay
- May be provocative or contrarian but must be faithful
- Should create curiosity or tension

**Description** (under 140 Chinese characters):
- Who is speaking
- What show / interview / podcast this is from
- Topic being discussed
- Key claim or takeaway