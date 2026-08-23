# Price history data

## Purpose

Fetches OHLCV data and computes technical indicators for any ticker across all three markets. Routes internally via Yahoo Finance: US tickers as-is, Bursa (numeric codes become .KL), crypto (BTC/USD becomes BTC-USD). Outputs computed indicators rather than raw candles to keep token cost low.

This skill fetches and computes. It never interprets or judges the output.

## Input

- `ticker` - the asset ticker. Market auto-detected by format:
  - Numeric or `.KL` suffix → Bursa Malaysia
  - Contains `/` (e.g., BTC/USD, ETH/USD) → Crypto
  - Standard alphabetic (e.g., MSFT, AAPL) → US market
- `period` (optional) - lookback period. Defaults:
  - Equities (US + Bursa): `1y` (1 year daily)
  - Crypto: `6mo` (6 months daily)
- `benchmark` (optional) - for relative strength comparison. Defaults:
  - US: `SPY`
  - Bursa: `^KLSE`
  - Crypto: `BTC-USD` (for altcoins) or none (for BTC itself)

## Output format

Write to scratch at: `$ISK_NOTES/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/price-history.md`

```markdown
---
ticker: MSFT
skill: price-history
date: 2024-03-15
status: complete | partial | unavailable
market: US | Bursa | Crypto
---

## Price summary

- Current price: $XXX.XX
- 52-week high: $XXX.XX
- 52-week low: $XXX.XX
- % from 52-week high: -X.X%
- Trend: uptrend | downtrend | sideways
- Weinstein stage: Stage 2 (Advancing)

## Moving averages

| MA | Value | Distance from price |
|----|-------|-------------------|
| 21 EMA | $XXX.XX | +X.X% |
| 50 SMA | $XXX.XX | +X.X% |
| 150 SMA | $XXX.XX | +X.X% |
| 200 SMA | $XXX.XX | +X.X% |

## Indicators

- RSI (14): XX.X
- MACD: X.XXXX (signal: X.XXXX, histogram: X.XXXX)
- ADX (14): XX.X
- OBV trend (20-day): rising | falling | flat
- Bollinger position: 0.XXX (0 = lower band, 1 = upper band)

## Volume

- Current volume: X,XXX,XXX
- 50-day average: X,XXX,XXX
- Volume ratio: X.Xx (current / average)

## Signals detected

- <list of triggered signals, e.g., golden_cross_50_200, volume_surge, 52week_high_breakout>

## Relative strength

- Benchmark: SPY
- Ticker performance (period): +X.X%
- Benchmark performance (period): +X.X%
- RS vs benchmark: +X.X% (excess return)
- RS trend (20-day): improving | deteriorating | flat

## Weekly OHLCV (last 12 weeks)

| Week | Open | High | Low | Close | Volume |
|------|------|------|-----|-------|--------|
| 2024-W11 | ... | ... | ... | ... | ... |
```

## Data sources

- **Primary:** Yahoo Finance via `yahoo_cache.py` (shared cache layer)
- **Cache:** Local file cache at `~/.cache/ta_skills/`, invalidates daily after market close
- **Ticker normalization:** handled by `yahoo_cache.py` (`_normalize_ticker` function)

## Scripts

Both scripts live in `data/price-history/scripts/`:

### price_history.py

Full indicator suite. Run with ticker and optional period:

```bash
python scripts/price_history.py MSFT
python scripts/price_history.py MSFT 2y
python scripts/price_history.py 1155 1y
python scripts/price_history.py BTC-USD 6mo
```

Returns JSON with: summary (price, trend, stage, 52wk range), ma_levels, indicators (RSI, MACD, ADX, OBV, Bollinger), volume stats, detected signals, weekly OHLCV.

### sector_rs.py

Relative strength comparison against any benchmark:

```bash
python scripts/sector_rs.py MSFT SPY 6mo
python scripts/sector_rs.py MSFT,AAPL,GOOG SPY 1y
python scripts/sector_rs.py 1155 ^KLSE 6mo
```

Returns JSON with: per-ticker performance, RS vs benchmark, RS trend direction.

## Default timeframes

| Market | Default period | Rationale |
|--------|---------------|-----------|
| US equities | 1y daily | Full cycle view, enough for 200 MA |
| Bursa equities | 1y daily | Same as US |
| Crypto | 6mo daily | Higher volatility, older data less relevant |

Override with the `period` argument when you need longer history (e.g., `2y` for stage analysis on a stock that's been basing for months).

## Error handling

1. If Yahoo Finance returns an error or timeout, retry once after 3 seconds.
2. If data has fewer than 50 candles, report `status: partial` and note that long-period indicators (150/200 MA, stage) are unavailable.
3. If ticker is not found (invalid symbol), report `status: unavailable` with reason.
4. For crypto tickers: if the `/` format fails, try the `-` format automatically (BTC/USD → BTC-USD).
5. Relative strength comparison is optional. If benchmark fetch fails, skip the RS section and note it.

## Dependencies

- `utility/shared-lib` - `yahoo_cache.py` for cached Yahoo Finance fetching
- `utility/report-writer` - for scratch path conventions
