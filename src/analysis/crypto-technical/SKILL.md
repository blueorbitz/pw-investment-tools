# Crypto technical analysis

## Purpose

Takes the computed indicators from `data/price-history` and derivatives data from `data/crypto-derivatives` to produce a technical assessment for crypto assets. Accounts for crypto-specific factors: 24/7 markets, funding rate context, liquidation zone awareness, BTC correlation, and wider volatility bands.

This skill interprets. It never fetches raw data itself.

## Input

Reads from scratch:
- `$ISK_NOTES/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/price-history.md` (required)
- `$ISK_NOTES/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/crypto-derivatives.md` (optional, enriches analysis)

## Output format

Write to scratch at: `$ISK_NOTES/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/crypto-technical.md`

```markdown
---
ticker: ETH
skill: crypto-technical
date: 2024-03-15
status: complete | partial | unavailable
---

## Technical verdict

**Trend: bullish | bearish | neutral**

<one paragraph summarizing the technical picture with crypto-specific context>

## Trend and structure

- Current stage: <Weinstein stage or crypto-adapted equivalent>
- Primary trend (daily): uptrend | downtrend | range-bound
- Higher timeframe context (weekly): <confirming or diverging from daily>
- BTC correlation (30d): X.XX (1.0 = moves lockstep with BTC)
- BTC correlation interpretation: <high-beta BTC play / diverging / independent>
- BTC dominance context: <rising BTC.D = headwind for alts / falling = tailwind>

## Key levels

| Level | Price | Type | Reasoning |
|-------|-------|------|-----------|
| Resistance 1 | $X,XXX | Near-term | <why> |
| Resistance 2 | $X,XXX | Major | <why> |
| Support 1 | $X,XXX | Near-term | <why> |
| Support 2 | $X,XXX | Major | <why> |
| Liquidation cluster (longs) | $X,XXX | Magnet | <estimated from derivatives> |
| Liquidation cluster (shorts) | $X,XXX | Magnet | <estimated from derivatives> |

### Crypto-specific level considerations

- Liquidation clusters act as price magnets. Large long liquidation below = potential stop hunt zone.
- Round numbers matter more in crypto ($50K, $100K for BTC; $1K, $2K for ETH).
- Prior cycle highs/lows remain relevant S/R for years.

## Funding rate context

- Current funding: +/-0.XXXX%
- Funding trend: <persistently positive / negative / neutral>
- Position imbalance signal: <crowded longs / crowded shorts / balanced>
- Tactical implication: <contrarian opportunity / trend confirmation / no signal>

## Liquidation zone awareness

- Estimated long liquidation cluster: $X,XXX (XX% below current)
- Estimated short liquidation cluster: $X,XXX (XX% above current)
- Risk of liquidation cascade: low | medium | high
- Current OI level: <elevated / normal / low>

## Momentum and indicators

- RSI (14): XX.X - <overbought/oversold/neutral>
- MACD: <bullish/bearish crossover or divergence>
- ADX: XX.X - <trending/ranging>
- Volume profile: <above/below average, confirming or diverging>
- Bollinger position: X.XX

## Entry and exit zones

### Suggested entry zone

- Aggressive: $X,XXX - $X,XXX (<reasoning>)
- Conservative: $X,XXX - $X,XXX (<reasoning>)

### Stop loss zone

- Tight stop: $X,XXX (<reasoning, wider than equities, account for crypto volatility>)
- Wide stop: $X,XXX (<reasoning>)
- Invalidation level: $X,XXX (below this, thesis is wrong)

### Crypto stop loss notes

- Crypto requires wider stops than equities (10-20% typical vs 5-10% for stocks)
- Avoid placing stops at obvious liquidation levels (they get hunted)
- Consider using daily close below level rather than intraday wick

## Active signals

<list from price-history signals, with crypto-specific interpretation>

## Data gaps

<what could not be assessed>
```

## Analysis framework

1. **24/7 market handling.** Crypto never closes. This means: no gap risk, but also no "overnight" resets. Weekly candles are more meaningful than daily for trend direction. Wicks matter less because there's no opening/closing imbalance.

2. **Funding rate interpretation.** Persistently positive funding (>0.03% per 8h) means longs are paying to hold. If price stalls while funding is high, a long squeeze is likely. Persistently negative funding during a selloff = shorts are crowded and a squeeze upward becomes probable.

3. **Liquidation zone awareness.** Market makers and algorithms hunt liquidation clusters. If a large cluster sits 5-10% below current price, expect a wick to that level. Place stops below the cluster, not at it. Similarly, short liquidation clusters above price can act as targets for a squeeze.

4. **BTC correlation.** Most altcoins have 0.6-0.9 correlation to BTC. If you're bullish on an alt, check that BTC isn't at a major resistance or in Stage 4. A bearish BTC outlook caps altcoin upside regardless of individual merit.

5. **BTC dominance.** Rising BTC.D means capital is flowing from alts to BTC (risk-off within crypto). Falling BTC.D = alt season conditions. This affects conviction: bullish alt thesis during rising BTC.D should be lower conviction.

6. **Wider stops.** Crypto volatility is 2-3x equities. A "tight" stop in crypto is 10-15% vs 3-7% in equities. If the thesis requires a stop tighter than 10%, the entry timing is probably wrong.

## Error handling

- If price-history scratch is `unavailable`, write `status: unavailable`.
- If crypto-derivatives scratch is missing, produce analysis without funding/liquidation context. Mark these sections as "derivatives data unavailable" and note it reduces conviction.
- If the token has very low derivatives volume, note this: "thin derivatives market, funding/liquidation signals less reliable."
- For tokens without perpetual futures (small caps), skip derivatives sections entirely.

## Dependencies

- `data/price-history` - provides price and indicator data (required)
- `data/crypto-derivatives` - provides funding, OI, liquidation data (optional, enriches analysis)
