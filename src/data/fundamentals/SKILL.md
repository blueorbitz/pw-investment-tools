# Fundamentals data

## Purpose

Fetches financial statement data and key valuation metrics for any ticker. Routes internally by market: US tickers go to Yahoo Finance timeseries API, Bursa tickers (numeric codes or .KL suffix) go to KLSE Screener. Outputs structured financial data to scratch for analysis skills to interpret.

This skill fetches and normalizes. It never interprets or judges the numbers.

## Input

- `ticker` - the asset ticker. Market is auto-detected:
  - Numeric code (e.g., `1155`) or `.KL` suffix → Bursa Malaysia
  - Standard alphabetic (e.g., `MSFT`, `GOOG`) → US market
- `period` (optional) - how many years of history to fetch. Default: 5 years.

## Output format

Write to scratch at: `$ISK_NOTES/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/fundamentals.md`

```markdown
---
ticker: MSFT
skill: fundamentals
date: 2024-03-15
status: complete | partial | unavailable
market: US | Bursa
---

## Financial statements (annual)

| Year | Revenue | Operating Income | Net Income | FCF |
|------|---------|-----------------|------------|-----|
| 2023 | $211.9B | $88.5B | $72.4B | $59.5B |
| ... | | | | |

## Growth rates

- Revenue CAGR (3Y): X%
- Revenue YoY (latest): X%
- Net income YoY (latest): X%
- FCF YoY (latest): X%

## Valuation metrics

<market-specific, see below>

## Dividend history

| Year | DPS | YoY Growth |
|------|-----|------------|
| 2023 | $2.72 | +10% |
| ... | | |

## Data gaps

<list any metrics that could not be fetched, with reason>
```

### US-specific metrics

- PE ratio (trailing and forward if available)
- PEG ratio
- FCF yield (FCF / market cap)
- Operating margin and net margin
- EPS (trailing) and EPS revision direction (if available via web search)
- Share buyback signal (shares outstanding trend declining = buyback active)

### Bursa-specific metrics

- PE ratio
- PB ratio
- Dividend yield (trailing)
- ROE
- Revenue growth (3Y CAGR)
- Cash and debt levels (net cash/debt position)
- Major shareholding changes (if available from KLSE Screener)

## Data sources

### US market

- **Primary:** Yahoo Finance timeseries API via `financials_fetch.py`
  - Fetches: annual revenue, operating income, FCF, net income
- **Dividend:** Yahoo Finance chart API with dividend events via `dividend_fetch.py`
  - Fetches: annual DPS history
- **Valuation multiples:** Agent fetches from Yahoo Finance quote endpoint (PE, PEG, market cap) directly using web tools. No script needed for these point-in-time values.

### Bursa market

- **Primary:** KLSE Screener via `financials_fetch.py`
  - Scrapes quarterly reports, aggregates to annual revenue and net income
- **Dividend:** KLSE Screener dividend table via `dividend_fetch.py`
  - Scrapes annual DPS history
- **Valuation multiples:** Agent fetches from KLSE Screener stock page (PE, PB, DY, ROE). No script needed.

## Scripts

Both scripts live in `data/fundamentals/scripts/`:

- `financials_fetch.py` - call with ticker argument. Prints JSON with `revenue`, `operating_income`, `fcf`, `net_income` arrays. Routes internally (Yahoo for US, KLSE Screener for Bursa).
- `dividend_fetch.py` - importable module. Call `fetch_dividend_history(ticker)` to get `{"dps_annual": [...]}`.

Usage:
```bash
python scripts/financials_fetch.py MSFT
python scripts/financials_fetch.py 1155
```

The scripts use `ISK_ROOT` to resolve imports from `utility/shared-lib/scripts/`. If unset, they fall back to `__file__`-relative paths.

## Error handling

1. If the primary API (Yahoo/KLSE Screener) fails, note which data is unavailable in the output.
2. For US tickers: if Yahoo timeseries fails, try fetching basic data via the agent's web tools from Yahoo Finance website directly.
3. For Bursa tickers: if KLSE Screener fails, try Yahoo Finance with `.KL` suffix as fallback (less data but some coverage).
4. If all sources fail, write scratch with `status: unavailable` and a clear reason.
5. Partial data is acceptable. Write what you have and note gaps in the "Data gaps" section.

## Dependencies

- `utility/shared-lib` - `yahoo_cache.py` used by the scripts for cached HTTP fetching
- `utility/report-writer` - for scratch path conventions
