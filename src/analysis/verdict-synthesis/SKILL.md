---
name: verdict-synthesis
description: Reads all analysis outputs for a ticker and produces the final Buy/Sell/Hold verdict with conviction level, target price, stop loss, thesis, and position sizing.
---

The output structure is universal across all markets. The weighting of inputs varies by market.

## Input

Reads all available analysis scratch files from: `$ISK_NOTES/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/`

Expected files (not all required):
- `us-valuation.md` or `bursa-valuation.md` or `crypto-valuation.md`
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
weights_applied: { valuation: 30, technical: 30, macro: 20, sentiment: 20 }
weights_baseline: { valuation: 30, technical: 30, macro: 20, sentiment: 20 }
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

Each factor carries a **strength label**, not just a direction. Use the labels
below (they map to an internal -2..+2 score used only for the composite math —
never print the numbers, always print the words):

| Label | Internal score | Meaning |
|-------|:--:|---------|
| Strong bullish | +2 | Signal is at an extreme in your favor (e.g. >30% below fair value, breakout on 5x+ volume, heavy insider cluster-buying) |
| Mild bullish | +1 | Modestly favorable |
| Neutral | 0 | Fair / no clear tilt |
| Mild bearish | -1 | Modestly unfavorable |
| Strong bearish | -2 | Signal is at an extreme against (e.g. >30% above fair value, stretched, distribution) |

| Factor | Signal | Strength | Weight | Contribution |
|--------|--------|----------|--------|--------------|
| Valuation | cheap / fair / expensive | strong/mild bullish · neutral · mild/strong bearish | XX% | bullish / bearish / neutral |
| Technical | bullish / bearish / neutral | strong/mild bullish · neutral · mild/strong bearish | XX% | bullish / bearish / neutral |
| Macro | bullish / bearish / neutral | strong/mild bullish · neutral · mild/strong bearish | XX% | bullish / bearish / neutral |
| Sentiment | bullish / bearish / neutral | strong/mild bullish · neutral · mild/strong bearish | XX% | bullish / bearish / neutral |
| On-chain (crypto only) | accumulation / distribution | strong/mild bullish · neutral · mild/strong bearish | XX% | bullish / bearish / neutral |

Net signal: X bullish, Y bearish, Z neutral
Composite score: <weighted sum of factor scores, e.g. +1.35> (label: <e.g. strong bullish>)

## Target price rationale

- Method: <how target was derived, e.g., "sector median PE applied to forward earnings" or "prior resistance level">
- Upside to target: +XX%
- Assumption: <key assumption behind the target>

## Stop loss rationale

- Level: $XXX.XX
- Method: <e.g., "below 200 SMA" or "below major support at $XX">
- Downside risk to stop: -XX%
- Risk/reward ratio: X:1

## Position sizing

Suggested allocation: X-Y% of portfolio
Rationale: <based on conviction and volatility>

| Conviction | Typical allocation |
|------------|-------------------|
| High | 3-5% |
| Medium | 1-3% |
| Low | 0.5-1% |

Volatility adjustment: <if stock is highly volatile, reduce toward lower end of range>

Note: This is an assessment framework, not financial advice. Position sizing depends on total portfolio size, diversification, and individual risk tolerance.

## Gaps and caveats

- <what analysis was missing and how it affected confidence>
- <any assumptions made to fill gaps>
```

## Weighting framework

The per-market tables below are the **regime-neutral baseline**. They encode durable
market-structure priors (Bursa's income-investor culture, crypto's liquidity
sensitivity) and stay human-editable. On top of the baseline, apply a **bounded
regime multiplier** (see "Regime-adaptive weighting") so the verdict reflects the
current market environment rather than a fixed rulebook. Baseline first, then adjust.

### US equities (default weights)

| Factor | Weight | Rationale |
|--------|--------|-----------|
| Valuation | 30% | Core driver of long-term returns |
| Technical | 30% | Timing and trend confirmation |
| Macro context | 20% | Rising tide lifts/sinks all boats |
| Sentiment | 20% | Contrarian signal + momentum |

### Bursa Malaysia equities

| Factor | Weight | Rationale |
|--------|--------|-----------|
| Valuation | 35% | Dividend yield weighted higher for income market |
| Technical | 25% | Lower weight due to low liquidity (more false signals) |
| Macro context | 25% | MYR and commodity cycle heavily impact Bursa |
| Sentiment | 15% | Fewer institutional players, sentiment data less reliable |

Bursa-specific adjustments:
- Dividend yield above 5% with stable payout adds conviction.
- Volume confirmation is required for any bullish technical signal. Without it, downgrade technical contribution to neutral.
- Foreign fund flow direction overrides other sentiment signals.

### Crypto

| Factor | Weight | Rationale |
|--------|--------|-----------|
| Technical | 25% | Important but noisy in 24/7 market |
| On-chain | 25% | Unique to crypto, strong signal |
| Macro/liquidity | 25% | Crypto is a liquidity barometer |
| Valuation (tokenomics) | 15% | Less mature frameworks than equities |
| Sentiment | 10% | Very noisy, useful only as contrarian |

Crypto-specific adjustments:
- On-chain accumulation by whales during price drawdowns is a strong bullish signal.
- Funding rates persistently negative with price holding = contrarian bullish.
- Token unlock within 30 days automatically lowers conviction by one level.
- BTC dominance rising = prefer BTC over alts.

## Regime-adaptive weighting

The baseline weights are a starting point, not the final word. The macro-context
scratch already produces a market-level read; use it to classify the current
**regime** and shift weight toward whichever factor matters most right now. This
trades a little reproducibility for adaptiveness — which is acceptable because every
run logs its regime signal and resulting weights, so any verdict stays explainable
after the fact.

### Step 1: Classify the regime

Read the macro-context scratch (and technical scratch for volatility) and pick one
label per axis. If macro-context is missing, use regime `neutral` and note it in
Gaps.

| Axis | Labels | Signal source |
|------|--------|---------------|
| Risk | risk-on / neutral / risk-off | macro-context stance (liquidity, rates, breadth) |
| Volatility | high-vol / normal | technical scratch (ATR/Bollinger width, ADX) |
| Driver | macro-driven / stock-driven | is the asset moving with its market or on its own catalysts |

### Step 2: Apply bounded multipliers

Adjust the baseline weights per the regime, then renormalize so weights sum to 100%.
**No single factor's weight may move more than ±10 percentage points from its
baseline** (the bound that keeps the system stable and auditable).

| Regime condition | Weight shift | Rationale |
|------------------|-------------|-----------|
| macro-driven | +up to 10pp to Macro, taken proportionally from the rest | when the market drives the asset, macro dominates |
| stock-driven | +up to 10pp to Valuation (equities) / On-chain (crypto) | idiosyncratic moves reward bottom-up factors |
| high-vol | +up to 10pp to Technical, -from Sentiment | in volatile tape, price structure leads, mood is noise |
| risk-off | +up to 5pp to Macro, cap conviction more readily | downside regimes punish ignoring the backdrop |
| risk-on + confirmed trend | +up to 5pp to Technical | momentum is more trustworthy in risk-on |

Multiple conditions can stack, but the ±10pp per-factor bound is absolute after
stacking. Sentiment is never raised by a regime shift (it is the noisiest input).

### Step 3: Log the applied weights

The verdict scratch MUST record the regime and the actual weights used, so the run
is reproducible-in-spirit even though weights vary. Add these to the YAML header and
show the adjusted weights in the factor summary table's Weight column.

```yaml
regime:
  risk: risk-on | neutral | risk-off
  volatility: high-vol | normal
  driver: macro-driven | stock-driven
weights_applied: { valuation: XX, technical: XX, macro: XX, sentiment: XX }
weights_baseline: { valuation: XX, technical: XX, macro: XX, sentiment: XX }
```

If the regime signal is weak or macro-context is unavailable, default to the baseline
weights, set `regime` fields to `neutral`/`unknown`, and say so in Gaps. Never let an
uncertain regime read swing weights — bounded and logged, or not at all.

## Conviction level rules

Conviction is gated on **signal magnitude**, not just how many factors agree. This
keeps most verdicts appropriately conservative while ensuring that a genuinely
strong signal produces a decisive, credible call. A wall of "mild bullish" factors
is NOT the same as a cluster of "strong bullish" factors, and the two must not
resolve to the same conviction.

First compute the **composite score**: the weighted sum of each factor's internal
score (-2..+2) using the market weights above. Then apply:

**High conviction** (decisive Buy/Sell — all must be true):
- Composite score magnitude is large: `|composite| >= HIGH_THRESHOLD` (default **1.2**)
- At least 3 factors point the same direction as the composite
- No factor sits at the opposite extreme (no "strong bearish" against a Buy, or "strong bullish" against a Sell)
- Data quality is good (most inputs available, status: complete)

**Medium conviction** (typical case):
- Composite magnitude is moderate: `0.5 <= |composite| < HIGH_THRESHOLD`, OR
- Strong direction but one factor mildly contradicts, OR
- Core thesis supported but some data gaps

**Low conviction** (any of these):
- Composite magnitude is small: `|composite| < 0.5` (mild-everything → resolves toward Hold)
- Factors are genuinely split (strong bullish valuation vs strong bearish technical)
- Key data is missing (only 1 analysis available)
- Macro headwinds contradict stock-level signals
- High uncertainty in the market regime

### Single-factor conviction override

A single dominant factor at **strong bullish** or **strong bearish**, backed by
good data quality, may escalate conviction by one level even when other factors are
neutral. This is the "one thing is screamingly obvious" case (deep undervaluation,
confirmed breakout on huge volume, whale cluster-accumulation). It prevents a lone
mild blemish elsewhere from muzzling a real standout.

Override eligibility is restricted to high signal-to-noise factors:
- **Equities (US/Bursa):** valuation extremes, and technical breakouts *with volume confirmation*.
- **Crypto:** on-chain whale accumulation/distribution, and derivatives extremes.
- **Sentiment may NEVER escalate on its own** — it is the noisiest input and is only ever corroborating.

The override can lift Low→Medium or Medium→High, but the "no opposite extreme" and
data-quality requirements for High still apply. It cannot manufacture a High
conviction verdict when a strong contradicting factor exists.

### Tunable knobs

These two encode risk appetite and should be set deliberately:
- `HIGH_THRESHOLD` (default **1.2** on the -2..+2 scale): lower → more decisive calls, more false-strong risk; higher → rarer, higher-quality strong calls.
- **Override-eligible factors**: which single factors may escalate alone (list above). Sentiment is deliberately excluded.

### Worked examples

- **Mild-everything ticker:** valuation mild bullish (+1), technical mild bullish (+1), macro neutral (0), sentiment mild bullish (+1). US weights → composite ≈ +0.7. Below 1.2 → **Medium** (or a modest Buy at Medium). Correctly NOT a strong call.
- **Deep-value + breakout ticker:** valuation strong bullish (+2), technical strong bullish (+2, volume-confirmed), macro neutral (0), sentiment mild bullish (+1). US weights → composite ≈ +1.4, three aligned, no opposite extreme → **High**. This is the clear signal that should punch through.
- **Standout single factor:** valuation strong bullish (+2), everything else neutral. Composite ≈ +0.6 → normally Medium, but valuation is override-eligible → escalate to **High** provided data quality is good and nothing sits at the opposite extreme.

## Handling partial inputs

When analysis skills are missing:

| Missing input | Impact |
|---------------|--------|
| Valuation only available | Can produce verdict but cap conviction at Medium |
| Technical only available | Can produce verdict but cap conviction at Medium |
| Neither valuation nor technical | Write `status: partial`, verdict is Hold with Low conviction |
| Macro missing | Reduce macro weight to 0, redistribute to others proportionally |
| Sentiment missing | Reduce sentiment weight to 0, redistribute proportionally |
| On-chain missing (crypto) | Redistribute to technical and macro |

Always note missing inputs in the "Gaps and caveats" section.

## Error handling

- If no analysis scratch files exist for the ticker, write `status: unavailable` with reason "no analysis data found."
- If all available analyses are themselves `unavailable`, produce a Hold verdict with Low conviction and explain why.
- Never produce a High conviction verdict when a factor sits at the *opposite extreme* (strong bearish against a Buy, or strong bullish against a Sell). Acknowledge the disagreement and cap at Medium. A merely *mild* contradiction does not block High on its own — magnitude and the composite score decide (see Conviction level rules).

## Dependencies

All analysis skills are conditional inputs (used when available):
- `analysis/us-valuation` (US market)
- `analysis/us-technical` (US market)
- `analysis/us-sentiment` (US market)
- `analysis/bursa-valuation` (Bursa market)
- `analysis/bursa-technical` (Bursa market)
- `analysis/bursa-sentiment` (Bursa market)
- `analysis/crypto-valuation` (Crypto market)
- `analysis/crypto-technical` (Crypto market)
- `analysis/crypto-sentiment` (Crypto market)
- `analysis/crypto-onchain-analysis` (Crypto market)
- `analysis/macro-context` (all markets)
