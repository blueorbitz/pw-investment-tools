---
name: us-valuation
description: Takes structured financial data from the fundamentals skill and produces a valuation judgment for US equities relative to growth, quality, and sector peers.
---

## Input

Reads from scratch: `$ISK_NOTES/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/fundamentals.md`

The fundamentals scratch file must contain (at minimum):
- Revenue and earnings history (3-5 years)
- Current valuation multiples (PE, PEG, FCF yield)
- Margin data (operating, net)
- Dividend history (if applicable)

If any input is marked `status: unavailable`, this skill adjusts its confidence and notes what it could not assess.

## Output format

Write to scratch at: `$ISK_NOTES/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/us-valuation.md`

```markdown
---
ticker: MSFT
skill: us-valuation
date: 2024-03-15
status: complete | partial | unavailable
---

## Valuation verdict

**Assessment: cheap | fair | expensive**

<one paragraph explaining the reasoning, referencing specific numbers>

## Multiples analysis

- PE (trailing): XX.X vs sector median XX.X
- PE (forward, if available): XX.X
- PEG ratio: X.X (interpretation: attractive < 1.5, fair 1.5-2.5, expensive > 2.5)
- FCF yield: X.X% (interpretation: attractive > 5%, fair 3-5%, expensive < 3%)
- EV/Revenue (if high-growth): X.X

## Growth-adjusted assessment

- Revenue CAGR (3Y): X%
- Earnings growth rate: X%
- Is current PE justified by growth? <yes/no with brief reasoning>
- PEG context: growing at X% with PE of XX implies PEG of X.X

## Quality scoring

- Operating margin: XX% (trend: expanding | stable | compressing)
- Net margin: XX% (trend)
- FCF conversion: XX% of net income converts to FCF (healthy > 80%)
- Revenue quality: recurring vs one-time mix (if discernible)
- Buyback signal: shares outstanding declining? (indicates capital return)

## Earnings momentum

- Latest quarter EPS vs estimate (beat/miss/in-line)
- Revenue surprise direction
- EPS revision trend (if available): upgrades outpacing downgrades?
- Consecutive beat streak (if discernible from data)

## DCF sanity check

Not a full model. A quick reasonableness test:
- If FCF grows at X% for 5 years and you apply a XX PE terminal multiple, what's the implied value vs current price?
- Is the market pricing in more or less growth than history supports?

## Key risks to valuation

- <specific risk that could compress multiples>
- <specific risk to growth assumptions>

## Data gaps

<list anything that could not be assessed and why>
```

## Analysis framework

Apply these checks in order:

1. **Multiples vs sector.** Compare PE and FCF yield against the stock's sector median. A stock at 2x sector PE needs 2x sector growth to justify it.

2. **PEG interpretation.** PEG below 1.0 is classically "cheap for growth." PEG 1.0-1.5 is reasonable. PEG above 2.5 means the market is pricing in acceleration or a premium moat. Flag which.

3. **Margin quality.** Expanding margins with growing revenue is the best signal. Compressing margins despite revenue growth suggests pricing pressure or cost bloat.

4. **Earnings momentum.** Recent EPS beats with upward revisions suggest the street is behind the curve (bullish). Misses with downward revisions suggest deterioration not yet priced in.

5. **DCF sanity.** Not a precise model. Just check: "If I assume X% growth (conservative, based on history), does the current price imply that or much more?" If the market is pricing 30% growth but history shows 15%, that's expensive regardless of narrative.

6. **Buyback check.** Declining share count means management is returning capital. Combined with low FCF yield, it suggests the company itself thinks it's cheap (or lacks reinvestment opportunities, flag both readings).

## Error handling

- If fundamentals scratch is `unavailable`, write `status: unavailable` with reason "no fundamentals data to analyze."
- If fundamentals scratch is `partial` (e.g., missing FCF or margins), do what you can and mark `status: partial`. Skip the sections that need missing data.
- Never invent numbers. If a metric is not in the scratch data, say "not available" rather than estimating.

## Dependencies

- `data/fundamentals` - provides the input data (reads its scratch output)
