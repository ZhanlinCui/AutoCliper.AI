# Content Analysis Playbook

## Stage 1 - Candidate Mining

Scan the full transcript for self-contained moments. For each candidate:

1. Identify a coherent span (20-180s) with a clear idea arc.
2. Check independence: understandable without prior context.
3. Check opening: hook appears in first 3 seconds.
4. Check ending: complete thought, no mid-sentence cut.
5. Clean boundaries: extend a little when needed for payoff.

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

Count guidance:
- < 20 min video → 5-8 candidates
- 20-60 min → 8-12 candidates
- > 60 min → 10-15 candidates

When in doubt, include more rather than fewer. The user will prune.

## Stage 2 - Score and Rank

Score each candidate 1-5:
- `hook`: opening pull in first 3s
- `clarity`: single idea, low ambiguity
- `standalone`: low dependency on prior context
- `payoff`: useful, memorable, share-worthy ending

Default ranking formula:
`total = hook*0.35 + clarity*0.25 + standalone*0.2 + payoff*0.2`

Use total score to rank candidates before user review.

## Stage 3 - Review Formatting

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

## Title and Description Generation

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

## Candidate Board Template

Use this format in `candidate-board.md`:

```text
| ID | Time | Duration | Title | Hook/Clarity/Standalone/Payoff | Summary |
|----|------|----------|-------|---------------------------------|---------|
| clip-01 | 00:12:03→00:13:22 | 79s | ... | 4/5/4/5 | ... |
```
