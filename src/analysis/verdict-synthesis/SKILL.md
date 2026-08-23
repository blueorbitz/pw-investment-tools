# Verdict synthesis

## Purpose

Reads all analysis scratch outputs for a ticker and produces the final Buy/Sell/Hold verdict. This is the last analysis step before the report is written. It weighs valuation, technical, sentiment, macro, and market-specific factors using market-aware weighting, then outputs a structured verdict with conviction level, target price, timeframe, stop loss, thesis, and position sizing guidance.

The output structure is universal across all markets. The weighting of inputs varies by market.

## Input

Reads all available analysis scratch files from: `~/notes/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/`

Expected files (not all required):
- `us-valuation.md` or `bursa-valuation.md` or `crypto-valuation.md`
- `us-technical.md` or `bursa-technical.md` or `crypto-technical.md`
- `macro-context.md`
- `us-sentiment.md` or `bursa-sentiment.md` or `crypto-sentiment.md`
- `crypto-onchain-analysis.md` (crypto only)

The skill must function with partial inputs. At minimum, it needs valuation + technical to produce a verdict. If only one is available, it can still produce a low-confidence verdict.

## Output format

Write to scratch at: `~/notes/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/verdict-synthesis.md`

```markdown
---
ticker: MSFT
skill: verdict-synthesis
date: 2024-03-15
status: complete | partial
market: US | Bursa | Crypto
inputs_available: [us-valuation, us-technical, macro-context, us-sentiment]
inputs_missing: []
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

| Factor | Signal | Weight | Contribution |
|--------|--------|--------|--------------|
| Valuation | cheap / fair / expensive | XX% | bullish / bearish / neutral |
| Technical | bullish / bearish / neutral | XX% | bullish / bearish / neutral |
| Macro | bullish / bearish / neutral | XX% | bullish / bearish / neutral |
| Sentiment | bullish / bearish / neutral | XX% | bullish / bearish / neutral |
| On-chain (crypto only) | accumulation / distribution | XX% | bullish / bearish / neutral |

Net signal: X bullish, Y bearish, Z neutral

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

## Conviction level rules

**High conviction** (all must be true):
- At least 3 factors align in the same direction
- No major factor is strongly contradictory
- Data quality is good (most inputs available, status: complete)

**Medium conviction** (typical case):
- 2 factors align, others neutral or missing
- One factor may mildly disagree
- Some data gaps but core thesis is supported

**Low conviction** (any of these):
- Factors are split (bullish valuation but bearish technical, or vice versa)
- Key data is missing (only 1 analysis available)
- Macro headwinds contradict stock-level signals
- High uncertainty in the market regime

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
- Never produce a High conviction verdict when any critical factor contradicts the thesis. Acknowledge the disagreement and cap at Medium.

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
