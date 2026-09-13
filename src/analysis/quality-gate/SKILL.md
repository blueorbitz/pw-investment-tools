---
name: quality-gate
description: Cheap quality gate run after the shared data fetch and before deep factor work. Dispatch A screens candidates with the buffett quick-screen checklist plus scripted thresholds. Dispatch B produces the deep US valuation factor (moat, management, intrinsic value) from the vendored buffett references. Output tiers: quality-pass, speculative, reject.
---

The gate sits between the cheap data fetch (fundamentals + price history) and
the expensive factor-specific research. A candidate that cannot pass a cheap
check does not earn expensive research. It follows the buffett dispatch model:
a quick screen (A) routes the candidate, deep analysis (B) does the valuation
work that verdict-synthesis consumes as the US valuation factor.

## Scope

- **US equities**: dispatch A always; dispatch B on gate-pass and speculative candidates.
- **Bursa / Crypto**: dispatch A screening only. Bursa and crypto valuation
  stay with `bursa-valuation` and `crypto-valuation`.

## Input

The shared data fetch already wrote `fundamentals.md` and `price-history.md`
to the ticker's scratch directory, and `quote_fetch.py` produced multiples.
No new data fetch happens here — the gate reuses what quick-look-grade data
already costs.

## Dispatch A: quick screen (cheap path)

Two halves, both required.

### 1. Scripted thresholds

Pull the numbers from the fundamentals/quote scratch and run:

```bash
python <ISK_ROOT>/analysis/quality-gate/scripts/gate_checks.py \
  --roe 18 --net-margin 15 --debt-to-ebitda 1.5 \
  --cash-conversion 95 --dividend-years 12 --eps-trend up
```

Omit a metric when the data is unavailable — it is reported `unknown` and
degrades the tier rather than failing it. The output tier is one of
`quality-pass`, `speculative`, `reject`.

### 2. Quick-screen checklist (judgment)

Answer the buffett quick-screen questions from the scratch in hand; one-line
answers, no research:

1. Can you describe how the business makes money in two sentences?
2. Would customers largely stay if the company raised prices 10%?
3. Has the moat widened or narrowed over the last five years?
4. Is management's capital-allocation record value-creating (10-year view)?
5. Any earnings-quality red flags (receivables/inventory outgrowing revenue,
   adjusted earnings divergence, auditor churn)?
6. Is the debt load survivable if revenue falls 30%?
7. Is the business in your circle of competence?
8. Is the current price plausibly below a rough intrinsic-value estimate?

Q5 (red flags) and Q6 (debt survivability) are integrity checks: a clear fail
on either caps the outcome at speculative no matter how good the numbers look.

### Dispatch A outcome

| Scripted tier | Checklist | Outcome |
|---------------|-----------|---------|
| quality-pass | no clear fails | **quality-pass** |
| quality-pass / speculative | one integrity fail | **speculative** |
| speculative | no integrity fails | **speculative** |
| reject | any | **reject** |
| any | ≥ 3 checklist fails | **reject** |

## Dispatch B: deep analysis (US valuation factor)

Runs for US candidates after dispatch A returns quality-pass or speculative —
never for reject. Read the vendored references in order:

1. `references/03-business-moat.md` - classify the moat type, strength, and trend
2. `references/04-management-governance.md` - integrity, capital allocation, owner mentality
3. `references/05-financial-metrics.md` - owner earnings, ROIC/ROE quality, cash conversion
4. `references/06-valuation-capital.md` - valuation methods, margin of safety tiers

Then set the intrinsic-value anchor with `analysis/valuation-baseline` instead
of reference 06's static multiple table — it computes the fair PE range from
the stock's quote, the current risk-free rate, the growth estimate, and your
moat judgment:

```bash
python <ISK_ROOT>/analysis/valuation-baseline/scripts/baseline_calc.py \
  --price 495.63 --forward-pe 21.0 --trailing-pe 27.6 \
  --risk-free 4.2 --growth 10 --moat wide --fcf-yield 0.45
```

Copy its `fair_pe_range`, `fair_value`, `margin_of_safety_pct`, `verdict`, and
`notes` verbatim into the dispatch B output. Apply the margin-of-safety tiers
from reference 06 on top (20–50% discount by uncertainty): the baseline gives
fair value, reference 06 gives how big a discount fair value requires.

Produce a judgment with the buffett output shape, compressed to the factor
verdict-synthesis needs:

- **Moat**: type, wide/narrow, widening/narrowing, evidence (margins, share, NRR)
- **Management**: rating on the three dimensions, one red flag or green flag each
- **Earnings quality**: owner-earnings estimate vs reported net income; red flags found
- **Intrinsic value**: method used, estimate range, margin of safety at current price
- **Verdict line**: the valuation factor strength label (rubric words: strong/mild
  bullish, neutral, mild/strong bearish) with one-line rationale

Write to scratch at `$ISK_NOTES/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/us-valuation.md`
with the standard scratch header (`skill: quality-gate`). This file is the US
valuation factor that verdict-synthesis consumes — it replaces the old
`analysis/us-valuation` skill.

## Output tiers and what happens next

| Tier | Meaning | Deep-research behavior |
|------|---------|------------------------|
| quality-pass | Buffet-grade quality screen cleared | full pipeline, normal conviction |
| speculative | quality concerns, worth researching | proceeds; conviction capped at Medium; report leads with the gate verdict |
| reject | fails the cheap screen | proceeds only on the capped speculative track; report leads with "Quality gate: REJECT" and the reasons |

A FAIL never hard-stops deep-research — runs work headless. The cap is
mechanical: verdict-synthesis passes `--cap Medium` to verdict_math.py.

Write the gate result to scratch at
`$ISK_NOTES/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/quality-gate.md` with the
tier, the scripted-check table, the checklist answers, and (if run) the
dispatch B judgment.

## Dependencies

- `data/fundamentals` scratch - statements and dividend history (upstream, already written)
- `data/fundamentals/scripts/quote_fetch.py` - multiples for the intrinsic-value check
- `analysis/valuation-baseline` scripts - `baseline_calc.py`, quote-aware fair multiple for dispatch B
- `utility/shared-lib/verdict_rubric.md` - strength labels for the factor verdict
- `analysis/verdict-synthesis` - consumes dispatch B's us-valuation.md scratch
