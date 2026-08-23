# Bursa fundamentals data (market overview)

## Purpose

Provides Bursa Malaysia market-level context: top stocks by market cap, sector breakdown, and foreign fund flow direction signals. Wraps the existing `bursa_flows.py` script which fetches market overview data from TradingView's Malaysia scanner.

This complements the shared `data/fundamentals` skill (which handles individual stock financials via KLSE Screener). This skill provides the market-wide context that helps with peer comparison and flow analysis.

This skill fetches and structures. It never interprets or judges the data.

## Input

- `scope` (optional) - what to fetch: `overview` (default), `sector`, or `both`

No ticker required. This is a market-level data skill.

## Output format

Write to scratch at: `~/notes/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/bursa-fundamentals.md`

When used as part of a ticker analysis, the data provides peer comparison context. When standalone, use `BURSA-OVERVIEW` as ticker placeholder.

```markdown
---
ticker: <TICKER or BURSA-OVERVIEW>
skill: bursa-fundamentals
date: 2024-03-15
status: complete | partial | unavailable
---

## Market overview (top stocks by market cap)

| Stock | Code | Price (RM) | Market Cap (RM B) | PE | DY% | 30d Chg% |
|-------|------|-----------|-------------------|-----|------|----------|
| MAYBANK | 1155 | 9.50 | 107.5 | 12.3 | 5.8 | +2.1 |
| CIMB | 1023 | 6.80 | 72.3 | 10.1 | 5.2 | +1.5 |
| ... | | | | | | |

## Sector performance

| Sector | 30d Return | Relative to KLCI |
|--------|-----------|-----------------|
| Financials | +X.X% | outperforming |
| Plantations | +X.X% | underperforming |
| Technology | +X.X% | outperforming |
| ... | | |

## Foreign flow signals

- Direction: net buying | net selling | mixed
- Magnitude: heavy | moderate | light
- Target sectors: <which sectors foreigners are buying/selling>
- Source: <weekly flow reports>

## Data gaps

<list what could not be fetched>
```

## Data sources

### Scripts

Scripts live in `data/bursa-fundamentals/scripts/`:

- `bursa_flows.py` - fetches market overview data from TradingView Malaysia scanner. Returns top Bursa stocks by market cap with key metrics (PE, DY, price change).

Usage:
```bash
python scripts/bursa_flows.py
```

### Supplementary sources

- Yahoo Finance (`^KLSE`) for KLCI index level
- Web search for sector performance summaries (The Edge, i3investor)
- Web search for foreign flow reports (MIDF, CGS-CIMB weekly)

## Error handling

1. If `bursa_flows.py` fails (TradingView blocks request), fall back to web search for "KLCI top stocks" or "Bursa market cap rankings."
2. Sector performance may not be available from a single source. Best-effort via web search.
3. Foreign flow data depends on weekly broker reports. If unavailable, note it and mark `status: partial`.
4. This skill provides context, not critical path data. If it fails entirely, the analysis pipeline continues with individual stock fundamentals from the shared `data/fundamentals` skill.

## Dependencies

- `utility/report-writer` - for scratch path conventions
- `utility/web-search` - fallback for market overview data
