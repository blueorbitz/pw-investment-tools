# US technical analysis

## Purpose

Takes the computed indicators produced by `data/price-history` and produces a technical assessment for US equities. Identifies trend stage, relative strength vs SPY, key support/resistance levels, moving average structure, and suggests entry/exit zones with reasoning.

This skill interprets. It never fetches price data itself.

## Input

Reads from scratch: `$ISK_NOTES/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/price-history.md`

The price-history scratch file must contain:
- Price summary (current price, trend, stage, 52wk range)
- Moving average levels and distances
- Indicators (RSI, MACD, ADX, OBV, Bollinger)
- Volume data (current vs average, ratio)
- Signals detected
- Relative strength vs SPY
- Weekly OHLCV (last 12 weeks)

## Output format

Write to scratch at: `$ISK_NOTES/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/us-technical.md`

```markdown
---
ticker: MSFT
skill: us-technical
date: 2024-03-15
status: complete | partial | unavailable
---

## Technical verdict

**Trend: bullish | bearish | neutral**

<one paragraph summarizing the technical picture>

## Stage identification

- Current stage: Stage 2 (Advancing) | Stage 1 (Basing) | Stage 3 (Topping) | Stage 4 (Declining)
- Stage confidence: high | medium | low
- Stage reasoning: <what confirms this reading>

## Relative strength vs SPY

- RS excess return (6mo): +X.X%
- RS trend (20-day): improving | deteriorating | flat
- Interpretation: <outperforming/underperforming the broad market, what this implies>

## Key levels

| Level | Price | Type | Reasoning |
|-------|-------|------|-----------|
| Resistance 1 | $XXX.XX | Near-term | <why this level matters> |
| Resistance 2 | $XXX.XX | Major | <why> |
| Support 1 | $XXX.XX | Near-term | <why> |
| Support 2 | $XXX.XX | Major | <why> |

### How levels are identified

- 52-week high/low
- Key moving averages (50 SMA, 200 SMA) when price is near them
- Recent swing highs/lows from weekly OHLCV
- Round numbers near current price (psychological levels)
- Bollinger band extremes during squeeze conditions

## Moving average structure

- 21 EMA vs 50 SMA: <above/below, recently crossed?>
- 50 SMA vs 200 SMA: <golden cross / death cross / converging / diverging>
- 50 SMA slope: <rising / flat / falling>
- Price position: <above all MAs / between MAs / below all MAs>
- Assessment: <what this structure means for trend health>

## Volume context

- Volume ratio (current vs 50-day avg): X.Xx
- OBV trend: <rising/falling/flat>
- Interpretation: <is volume confirming or diverging from price action?>
- Notable signals: <volume surge, dry-up, etc.>

## Momentum indicators

- RSI (14): XX.X - <overbought >70 / oversold <30 / neutral>
- MACD: <bullish crossover / bearish crossover / converging / diverging>
- ADX: XX.X - <strong trend >25 / weak trend <20 / no trend <15>
- Bollinger position: X.XX - <near upper / middle / near lower / outside bands>

## Entry and exit zones

### Suggested entry zone

- Aggressive entry: $XXX.XX - $XXX.XX (<reasoning, e.g., pullback to 21 EMA>)
- Conservative entry: $XXX.XX - $XXX.XX (<reasoning, e.g., breakout above resistance with volume>)

### Stop loss zone

- Tight stop: $XXX.XX (<reasoning, e.g., below recent swing low>)
- Wide stop: $XXX.XX (<reasoning, e.g., below 200 SMA or major support>)

### Context for stops

- ATR-based volatility: typical daily range is $X.XX (X.X%)
- Stop should accommodate normal volatility without triggering on noise

## Active signals

<list from the detected signals in price-history, with interpretation of each>

## Data gaps

<anything that could not be assessed>
```

## Analysis framework

Apply in this order:

1. **Stage identification.** Use Weinstein stage from price-history data. Cross-reference with MA structure and slope. Stage 2 with rising 150 SMA is the ideal long setup. Stage 4 with falling 150 SMA is avoid/short territory.

2. **Relative strength vs SPY.** A stock in Stage 2 that also shows improving RS vs SPY is a high-conviction long. A stock in Stage 2 but with deteriorating RS may be a laggard riding a broad market tide.

3. **Support/resistance methodology.** Identify levels from:
   - Prior swing highs/lows in weekly data
   - Key MAs that price has respected
   - 52-week high (breakout level)
   - Round numbers within 5% of current price

4. **MA structure reading.** The "stacking" of MAs matters:
   - Bullish: Price > 21 EMA > 50 SMA > 200 SMA, all rising
   - Bearish: Price < 21 EMA < 50 SMA < 200 SMA, all falling
   - Transitional: MAs converging, price whipsawing around them

5. **Volume confirmation.** Price moves on above-average volume carry more weight. Breakouts without volume are suspect. Pullbacks on declining volume are healthy.

6. **Entry zone logic.**
   - Aggressive: buy on pullback to a rising 21 EMA or support level, if trend is confirmed
   - Conservative: buy on breakout above resistance with volume confirmation (ratio > 1.5x)
   - Never suggest entry in Stage 4 or when RS is deteriorating and ADX is low

7. **Stop loss logic.**
   - Tight stop: below the most recent swing low or below a key MA the stock should hold if thesis is correct
   - Wide stop: below major support (200 SMA or major prior low). Used for position trades with longer timeframe
   - Stops should be 1-2 ATR below the level to avoid noise stops

## Error handling

- If price-history scratch is `unavailable`, write `status: unavailable` with reason.
- If price-history is `partial` (e.g., insufficient data for 200 MA or stage), assess what you can and mark `status: partial`.
- If RS data is missing (benchmark fetch failed), skip the RS section and note it.
- Never fabricate levels. If weekly data is insufficient to identify S/R, say so.

## Dependencies

- `data/price-history` - provides all input data (reads its scratch output)
