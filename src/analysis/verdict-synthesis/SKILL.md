---
name: verdict-synthesis
description: Reads all analysis outputs for a ticker and produces the final Buy/Sell/Hold verdict with conviction level, target price, stop loss, and thesis. All scoring math is delegated to verdict_math.py.
---

The output structure is universal across all markets. The weighting of inputs
varies by market. The scoring rules (strength labels, per-market baseline
weights, regime multipliers, conviction thresholds) live in
`utility/shared-lib/verdict_rubric.md` — read that file, never re-derive them.

The LLM judges; the script computes. Your job is the factor strength labels,
the thesis, the target, and the stop. `verdict_math.py` produces the composite
score, the conviction level, and the applied weights. Never do the arithmetic
yourself.

## Input

Reads all available analysis scratch files from: `$ISK_NOTES/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/`

Expected files (not all required):
- `us-valuation.md` (written by the quality gate's dispatch B) or `bursa-valuation.md` or `crypto-valuation.md`
- `us-technical.md` or `bursa-technical.md` or `crypto-technical.md`
- `macro-context.md`
- `us-sentiment.md` or `bursa-sentiment.md` or `crypto-sentiment.md`
- `crypto-onchain-analysis.md` (crypto only)

The skill must function with partial inputs. At minimum, it needs valuation + technical to produce a verdict. If only one is available, it can still produce a low-confidence verdict.

## Output format

Write to scratch at: `$ISK_NOTES/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/verdict-synthesis.md`

```markdown
---
ticker: MSFT
skill: verdict-synthesis
date: 2024-03-15
status: complete | partial
market: US | Bursa | Crypto
inputs_available: [us-valuation, us-technical, macro-context, us-sentiment]
inputs_missing: []
regime:
  risk: risk-on | neutral | risk-off
  volatility: high-vol | normal
  driver: macro-driven | stock-driven
weights_applied: { from verdict_math.py output }
weights_baseline: { from verdict_math.py output }
---

## Verdict

Action: Buy | Sell | Hold
Conviction: High | Medium | Low
Target Price: $XXX.XX
Timeframe: X months
Stop Loss: $XXX.XX
Thesis: <one sentence capturing the core reason>

## Thesis (expanded)

<one paragraph expanding on the verdict. Why this action, why this conviction level, what's the path to target, what invalidates the thesis>

## Factor summary

Label each factor with a strength label from the rubric's -2..+2 table. Print
the label words, never the numbers.

| Factor | Signal | Strength | Weight |
|--------|--------|----------|--------|
| Valuation | cheap / fair / expensive | strong/mild bullish · neutral · mild/strong bearish | from verdict_math.py |
| Technical | bullish / bearish / neutral | <label words> | from verdict_math.py |
| Macro | bullish / bearish / neutral | <label words> | from verdict_math.py |
| Sentiment | bullish / bearish / neutral | <label words> | from verdict_math.py |
| On-chain (crypto only) | accumulation / distribution | <label words> | from verdict_math.py |

Net signal: X bullish, Y bearish, Z neutral
Composite score: <from verdict_math.py, e.g. "+1.4, strong bullish">

## Target price rationale

- Method: <how target was derived, e.g., "sector median PE applied to forward earnings" or "prior resistance level">
- Upside to target: +XX%
- Assumption: <key assumption behind the target>

## Stop loss rationale

- Level: $XXX.XX
- Method: <e.g., "below 200 SMA" or "below major support at $XX">
- Downside risk to stop: -XX%
- Risk/reward ratio: X:1

## Gaps and caveats

- <what analysis was missing and how it affected confidence>
- <any assumptions made to fill gaps>
```

## Workflow

1. Classify the regime from macro-context and technical scratch using the
   rubric's three axes (risk, volatility, driver). If macro-context is
   missing, leave the regime unclassified — verdict_math then applies
   baseline weights.
2. Assign each available factor a strength label from the rubric's table.
3. Run the math:

```bash
python <ISK_ROOT>/utility/shared-lib/scripts/verdict_math.py \
  --market US \
  --label valuation=2 --label technical=1 --label macro=0 --label sentiment=1 \
  --regime-risk neutral --volatility high-vol --driver stock-driven \
  --missing macro \
  --data-quality complete \
  --volume-confirmed
```

4. Copy `weights_applied`, `weights_baseline`, `composite_score`, and
   `conviction` from the output into the scratch header and factor summary
   table. Carry any `notes` (single-factor override, redistribution,
   conviction cap) into Gaps so the run stays auditable.
5. Write the thesis, target rationale, and stop rationale — the judgment
   sections no script can produce.

Gate-FAIL runs arrive on a capped speculative track: pass `--cap Medium` to
verdict_math so the conviction ceiling is enforced mechanically, and state the
gate verdict up front in the report (deep-research handles the framing).

Market-specific adjustments (Bursa dividend/volume/flow rules, crypto
unlock/funding/dominance rules) are in the rubric — apply them when choosing
labels, and pass `--volume-confirmed` when a technical breakout has volume
confirmation so the single-factor override can fire.

## Handling partial inputs

Pass missing factors via `--missing` — verdict_math redistributes their weight
proportionally. Conviction caps:

| Situation | Result |
|-----------|--------|
| Only valuation available | capped at Medium (pass `--data-quality partial`) |
| Only technical available | capped at Medium |
| Neither valuation nor technical | write `status: partial`, Hold with Low conviction |
| Macro or sentiment missing | pass via `--missing`; weight redistributed |
| On-chain missing (crypto) | pass via `--missing`; redistributed |

Always note missing inputs in the "Gaps and caveats" section.

## Error handling

- If no analysis scratch files exist for the ticker, write `status: unavailable` with reason "no analysis data found."
- If all available analyses are themselves `unavailable`, produce a Hold verdict with Low conviction and explain why.
- Never print internal -2..+2 scores — rubric rule, labels only.

## Dependencies

All analysis skills are conditional inputs (used when available):
- `analysis/quality-gate` (US market: supplies the valuation factor via dispatch B)
- `analysis/bursa-valuation` | `analysis/crypto-valuation` (their markets)
- `analysis/us-technical` | `analysis/bursa-technical` | `analysis/crypto-technical`
- `analysis/us-sentiment` | `analysis/bursa-sentiment` | `analysis/crypto-sentiment`
- `analysis/crypto-onchain-analysis` (Crypto only)
- `analysis/macro-context` (all markets)

Shared files (not skills):
- `utility/shared-lib/verdict_rubric.md` - scoring rules
- `utility/shared-lib/scripts/verdict_math.py` - composite, conviction, weights
