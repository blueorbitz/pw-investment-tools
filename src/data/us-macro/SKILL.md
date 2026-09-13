---
name: us-macro
description: Fetches current US macroeconomic indicators covering monetary policy, inflation, growth, and liquidity conditions. Fetches and formats only, never interprets.
---

## Input

None required. This skill always fetches the current macro state. No ticker needed.

Optional:
- `focus` - narrow the fetch to a subset: `liquidity`, `rates`, `growth`, or `all` (default: `all`)

## Output format

Write to scratch at: `$ISK_NOTES/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/us-macro.md`

When invoked as part of a ticker research flow, use that ticker's scratch directory. When invoked standalone, use `US-MACRO` as the ticker placeholder.

```markdown
---
ticker: <TICKER or US-MACRO>
skill: us-macro
date: 2024-03-15
status: complete | partial | unavailable
---

## Monetary policy

| Indicator | Current | Trend | Date |
|-----------|---------|-------|------|
| Fed funds rate | X.XX% | holding | YYYY-MM-DD |
| 10Y Treasury yield | X.XX% | rising | YYYY-MM-DD |
| 2Y Treasury yield | X.XX% | falling | YYYY-MM-DD |
| 10Y-2Y spread | +XXX bps | steepening | YYYY-MM-DD |
| 10Y-3M spread | +XXX bps | — | YYYY-MM-DD |

## Inflation

| Indicator | Current | Trend | Date |
|-----------|---------|-------|------|
| CPI YoY | X.X% | declining | YYYY-MM-DD |
| Core CPI YoY | X.X% | sticky | YYYY-MM-DD |
| PCE YoY | X.X% | declining | YYYY-MM-DD |
| Core PCE YoY | X.X% | — | YYYY-MM-DD |

## Growth

| Indicator | Current | Trend | Date |
|-----------|---------|-------|------|
| ISM Manufacturing | XX.X | contracting (<50) | YYYY-MM-DD |
| ISM Services | XX.X | expanding (>50) | YYYY-MM-DD |

## Liquidity plumbing

| Indicator | Value ($B) | WoW change | Date |
|-----------|-----------|------------|------|
| Fed balance sheet | $X,XXX.XB | -$XX.XB | YYYY-MM-DD |
| Reverse repo (ON RRP) | $XXX.XB | -$XX.XB | YYYY-MM-DD |
| Treasury General Account | $XXX.XB | +$XX.XB | YYYY-MM-DD |
| Reserve balances | $X,XXX.XB | +$XX.XB | YYYY-MM-DD |

Net liquidity estimate: $X,XXX.XB (Fed assets - RRP - TGA)
Net liquidity WoW change: +/- $XX.XB

## Yield curve assessment

<one-line signal: deeply inverted / partially inverted / flat / normal / steep>

## Data gaps

<list any indicators that could not be fetched>
```

Trend column values: `rising`, `falling`, `holding`, `steepening`, `flattening`, `expanding`, `contracting`, `sticky`, or a blank dash if insufficient history.

## Data sources

**Primary:** FRED API (Federal Reserve Economic Data) - free with API key.

| FRED Series | Indicator |
|-------------|-----------|
| FEDFUNDS | Fed funds effective rate |
| DGS10 | 10-Year Treasury yield |
| DGS2 | 2-Year Treasury yield |
| DGS3MO | 3-Month Treasury yield |
| CPIAUCSL | CPI (compute YoY from monthly) |
| CPILFESL | Core CPI |
| PCEPI | PCE price index |
| PCEPILFE | Core PCE |
| MANEMP / ISM | ISM Manufacturing PMI |
| NMFBAI / ISM | ISM Services PMI |
| WALCL | Fed total assets (balance sheet) |
| RRPONTSYD | Overnight reverse repo |
| WTREGEN | Treasury General Account |
| WRESBAL | Reserve balances |

**Environment variable required:** `FRED_API_KEY`

Get a free key at: https://fred.stlouisfed.org/docs/api/api_key.html

## Scripts

Scripts live in `data/us-macro/scripts/`:

### fed_liquidity.py

Fetches Fed balance sheet, RRP, TGA, reserve balances. Computes net liquidity estimate. Outputs markdown table.

```bash
python scripts/fed_liquidity.py
```

Requires `FRED_API_KEY` env var. Uses the `requests` library.

### yield_curve.py

Fetches full Treasury yield curve (1M through 30Y), computes key spreads (10Y-2Y, 10Y-3M), classifies curve shape.

```bash
python scripts/yield_curve.py
```

Requires `FRED_API_KEY` env var. Uses the `requests` library.

## Error handling

1. If `FRED_API_KEY` is not set, report `status: unavailable` and instruct the user to set it.
2. If FRED API returns errors for some series, fetch what you can and note unavailable indicators in "Data gaps".
3. Partial data is acceptable. A macro snapshot with 7 out of 10 indicators is still useful.
4. If FRED is completely unreachable, try web search for the most critical numbers (Fed rate, 10Y yield, CPI) and mark `status: partial`.
5. ISM data is released monthly and may show the same value for weeks. That's normal, not an error.

## Dependencies

- `utility/report-writer` - for scratch path conventions
