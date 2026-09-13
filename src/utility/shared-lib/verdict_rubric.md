# Verdict rubric

Shared scoring rubric for quick-look and verdict-synthesis. The LLM labels each
factor with a strength; `utility/shared-lib/scripts/verdict_math.py` computes
the composite score, conviction, and applied weights from those labels. Labels
in, math out — the LLM never does arithmetic.

## Strength labels (-2..+2)

| Label | Internal score | Meaning |
|-------|:--:|---------|
| Strong bullish | +2 | Signal is at an extreme in your favor (e.g. >30% below fair value, breakout on 5x+ volume, heavy insider cluster-buying) |
| Mild bullish | +1 | Modestly favorable |
| Neutral | 0 | Fair / no clear tilt |
| Mild bearish | -1 | Modestly unfavorable |
| Strong bearish | -2 | Signal is at an extreme against (e.g. >30% above fair value, stretched, distribution) |

Never print the numbers. Always print the words.

## Per-market baseline weights

Regime-neutral baselines. They encode durable market-structure priors and stay
human-editable here, not in prompts.

### US equities

| Factor | Weight |
|--------|-------:|
| Valuation | 30% |
| Technical | 30% |
| Macro | 20% |
| Sentiment | 20% |

### Bursa Malaysia equities

| Factor | Weight |
|--------|-------:|
| Valuation | 35% |
| Technical | 25% |
| Macro | 25% |
| Sentiment | 15% |

Adjustments: dividend yield above 5% with stable payout adds conviction;
volume confirmation is required for any bullish technical signal (otherwise
downgrade technical to neutral); foreign fund flow direction overrides other
sentiment signals.

### Crypto

| Factor | Weight |
|--------|-------:|
| Technical | 25% |
| On-chain | 25% |
| Macro/liquidity | 25% |
| Valuation (tokenomics) | 15% |
| Sentiment | 10% |

Adjustments: whale accumulation during drawdowns is strongly bullish;
persistently negative funding with price holding is contrarian bullish; a
token unlock within 30 days lowers conviction by one level; rising BTC
dominance means prefer BTC over alts.

## Regime multipliers (bounded)

Classify the regime from macro-context and technical scratch: risk
(risk-on/neutral/risk-off), volatility (high-vol/normal), driver
(macro-driven/stock-driven). Then shift baseline weights:

| Condition | Shift |
|-----------|-------|
| macro-driven | +10pp to Macro |
| stock-driven | +10pp to Valuation (equities) / On-chain (crypto) |
| high-vol | +10pp to Technical, taken from Sentiment |
| risk-off | +5pp to Macro |
| risk-on + confirmed trend | +5pp to Technical |

Absolute bound: no single factor moves more than ±10pp from baseline, after
stacking. Sentiment is never raised by a regime shift. Weights are then
renormalized to 100%. `verdict_math.py` enforces all of this — pass the regime,
do not adjust weights by hand.

## Conviction thresholds

Composite = weighted sum of factor scores using applied weights.

- **High** (all required): |composite| >= 1.2; at least 3 factors point the
  same direction; no factor at the opposite extreme; data quality good.
- **Medium**: 0.5 <= |composite| < 1.2, or strong direction with one mild
  contradiction, or core thesis supported but data gaps.
- **Low**: |composite| < 0.5, or genuinely split factors, or key data missing
  (only one analysis available), or macro contradicting stock signals.

### Single-factor override

One dominant override-eligible factor at strong bullish/bearish, with good
data quality and nothing at the opposite extreme, escalates conviction one
level (Low→Medium, Medium→High).

- Equities: valuation extremes; technical breakouts **with volume confirmation**.
- Crypto: on-chain whale accumulation/distribution; derivatives extremes.
- Sentiment may never escalate on its own. Ever.

## Partial inputs

Missing factor: its weight drops to 0 and is redistributed proportionally to
the remaining factors. Only valuation or only technical available: conviction
caps at Medium. Neither: Hold at Low. Note every missing input in Gaps.
