# Crypto macro data

## Purpose

Fetches macro indicators that drive the crypto market as a whole: dollar strength, stablecoin supply growth, BTC ETF flows, and Fed net liquidity. Crypto is a high-beta liquidity play, so these macro factors often matter more than individual token fundamentals.

This skill fetches and structures. It never interprets or judges the data.

## Input

None required. This skill always fetches the current crypto macro state.

## Output format

Write to scratch at: `~/notes/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/crypto-macro.md`

When invoked as part of a ticker research flow, use that ticker's scratch directory. When invoked standalone, use `CRYPTO-MACRO` as the ticker placeholder.

```markdown
---
ticker: <TICKER or CRYPTO-MACRO>
skill: crypto-macro
date: 2024-03-15
status: complete | partial | unavailable
---

## Dollar strength

- DXY (US Dollar Index): XXX.XX
- DXY 30-day change: +/-X.X%
- DXY trend: rising | falling | sideways
- Impact: rising DXY = headwind for crypto, falling = tailwind

## Stablecoin supply

- USDT market cap: $XXX.XB
- USDC market cap: $XX.XB
- Total stablecoin supply: $XXX.XB
- 30-day change: +/-$X.XB (+/-X.X%)
- Trend: growing | shrinking | flat
- Impact: growing stablecoin supply = new capital entering crypto ecosystem

## BTC ETF flows (if available)

- Net flow (today): +/-$XXX.XM
- Net flow (7d): +/-$X.XB
- Net flow (30d): +/-$X.XB
- Trend: consistent inflows | consistent outflows | mixed
- Impact: sustained inflows = institutional accumulation

## Fed net liquidity

- Fed balance sheet: $X,XXX.XB
- Reverse repo (RRP): $XXX.XB
- Treasury General Account (TGA): $XXX.XB
- Net liquidity (Fed BS - RRP - TGA): $X,XXX.XB
- Net liquidity 30-day change: +/-$XXX.XB
- Trend: expanding | contracting | flat
- Impact: expanding liquidity is the strongest macro tailwind for crypto

## BTC dominance

- BTC dominance: XX.X%
- 30-day change: +/-X.X%
- Trend: rising | falling | stable
- Impact: rising BTC.D = risk-off within crypto (prefer BTC over alts), falling = alt season signal

## Fear and Greed Index

- Current value: XX/100
- Classification: Extreme Fear | Fear | Neutral | Greed | Extreme Greed
- 7-day average: XX
- Contrarian signal: extreme fear = potential accumulation zone, extreme greed = potential distribution

## Data gaps

<list what could not be fetched>
```

## Data sources

| Source | Data provided | Access |
|--------|--------------|--------|
| Yahoo Finance | DXY (^DXY or DX-Y.NYB) | Free via yahoo_cache |
| DeFiLlama | Stablecoin supply (USDT, USDC, total) | Free, no key |
| FRED API | Fed balance sheet, RRP, TGA | Free with FRED_API_KEY |
| ETF flow trackers | BTC ETF net flows | Web search (no free API) |
| Alternative.me | Crypto Fear & Greed Index | Free API |
| CoinGecko | BTC dominance | Free tier |

### DeFiLlama stablecoin endpoint

- `/stablecoins` - all stablecoin market caps and supply

### Alternative.me Fear & Greed

- `https://api.alternative.me/fng/` - current and historical values

### BTC ETF flows

No single reliable free API. Sources:
- SoSoValue (web search)
- BitMEX Research (web search)
- Financial news aggregation

### Environment variables

- `FRED_API_KEY` - for Fed liquidity data (shared with data/us-macro)

If `FRED_API_KEY` is not set, skip the Fed liquidity section and note it as a gap. DXY can still be fetched from Yahoo Finance without a key.

## Error handling

1. DXY from Yahoo Finance is highly reliable. If it fails, this is unusual, retry once.
2. Stablecoin data from DeFiLlama is generally reliable. If down, use CoinGecko market cap data for USDT/USDC as fallback.
3. BTC ETF flow data depends on web search quality. If unavailable, skip and note it. This alone should not block the pipeline.
4. Fed liquidity requires FRED_API_KEY. If not set, note the gap but continue. The `data/us-macro` skill may have already fetched this data into its own scratch.
5. Fear & Greed Index is nice-to-have. If API is down, skip it.
6. Partial data is normal for this skill. Many metrics have different refresh cadences (ETF flows daily, stablecoin supply daily, FRED weekly).

## Dependencies

- `utility/shared-lib` - `yahoo_cache.py` for DXY price fetching
- `utility/report-writer` - for scratch path conventions
- `utility/web-search` - for BTC ETF flow data
