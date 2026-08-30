---
name: crypto-derivatives
description: Fetches derivatives market data for crypto assets including perpetual funding rates, open interest, and liquidation levels.
---

## Input

- `ticker` - crypto asset (e.g., BTC, ETH, SOL)
- Derivatives data is primarily from Binance Futures (largest perp venue). Can extend to aggregate sources.

## Output format

Write to scratch at: `$ISK_NOTES/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/crypto-derivatives.md`

```markdown
---
ticker: BTC
skill: crypto-derivatives
date: 2024-03-15
status: complete | partial | unavailable
---

## Funding rates

- Current funding rate (8h): +/-0.XXXX% (positive = longs pay shorts)
- Annualized funding: +/-XX.X%
- 7-day average funding: +/-0.XXXX%
- 30-day average funding: +/-0.XXXX%
- Funding trend: persistently positive | persistently negative | oscillating neutral
- Interpretation hint:
  - Persistently positive (>0.03%) = crowded long, potential long squeeze
  - Persistently negative (<-0.01%) = crowded short, potential short squeeze
  - Neutral (around 0.01%) = balanced market

## Open interest

- Total OI (USD): $XX.XB
- OI change (24h): +/-X.X%
- OI change (7d): +/-X.X%
- OI / market cap ratio: X.X% (higher = more leveraged speculation)
- OI trend (30d): rising | falling | flat
- Interpretation hint:
  - Rising OI + rising price = new longs entering (trend confirmation)
  - Rising OI + falling price = new shorts entering (bearish pressure)
  - Falling OI + rising price = short covering (may not sustain)
  - Falling OI + falling price = long liquidation (capitulation)

## Liquidation levels

- Estimated long liquidation clusters: $XX,XXX - $XX,XXX (major)
- Estimated short liquidation clusters: $XX,XXX - $XX,XXX (major)
- 24h liquidations (total): $XXX.XM
- 24h long liquidations: $XXX.XM
- 24h short liquidations: $XXX.XM
- Largest single liquidation (24h): $X.XM at $XX,XXX

## Long/short ratio

- Top trader long/short ratio: X.XX (>1 = net long, <1 = net short)
- Account-based long/short ratio: X.XX
- Trend (7d): shifting long | shifting short | neutral

## Data gaps

<list what could not be fetched>
```

## Data sources

| Source | Data provided | Access |
|--------|--------------|--------|
| Binance Futures API | Funding rates, OI, long/short ratio | Free, no key |
| Coinglass (web) | Aggregated OI, liquidation heatmap | Web search fallback |
| CoinGecko derivatives | Multi-exchange OI aggregation | Free tier |

### Binance Futures endpoints

- `/fapi/v1/fundingRate` - historical funding rates
- `/fapi/v1/openInterest` - current OI for a symbol
- `/futures/data/openInterestHist` - OI history
- `/futures/data/topLongShortPositionRatio` - long/short ratio
- `/futures/data/globalLongShortAccountRatio` - account-based ratio

Symbol format: `BTCUSDT`, `ETHUSDT`, `SOLUSDT`

### Liquidation data

Exact liquidation levels are not published by exchanges. Estimates come from:
- Coinglass liquidation heatmap (via web search)
- Calculated from known leverage tiers and current OI distribution
- Recent liquidation events from exchange data

## Error handling

1. Binance API is free and generally reliable. If it fails, try CoinGecko derivatives endpoint as fallback.
2. Liquidation level data is always an estimate. Mark it clearly as estimated, not precise.
3. For tokens not listed on Binance Futures, try alternate venues or note "derivatives data unavailable for this token."
4. If the token has low derivatives volume (thin OI), note this as it reduces signal reliability.
5. Funding rate history is straightforward to fetch. If only funding is available (no liquidation data), that's still useful as `status: partial`.

## Dependencies

- `utility/report-writer` - for scratch path conventions
- `utility/web-search` - fallback for liquidation heatmap data
