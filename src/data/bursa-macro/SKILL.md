# Bursa macro data

## Purpose

Fetches macroeconomic indicators that drive the Malaysian equity market: BNM policy rate, USD/MYR exchange rate, palm oil futures, commodity indices, and ASEAN fund flow data. Malaysia's market is heavily influenced by commodity prices, foreign fund flows, and regional dynamics.

This skill fetches and structures. It never interprets or judges the data.

## Input

None required. This skill always fetches the current Bursa macro state.

## Output format

Write to scratch at: `~/notes/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/bursa-macro.md`

When invoked as part of a ticker research flow, use that ticker's scratch directory. When invoked standalone, use `BURSA-MACRO` as the ticker placeholder.

```markdown
---
ticker: <TICKER or BURSA-MACRO>
skill: bursa-macro
date: 2024-03-15
status: complete | partial | unavailable
---

## Monetary policy

| Indicator | Current | Trend | Date |
|-----------|---------|-------|------|
| BNM OPR (Overnight Policy Rate) | X.XX% | holding | YYYY-MM-DD |
| BNM SRR | X.XX% | — | YYYY-MM-DD |

## Currency

| Indicator | Current | Trend | Date |
|-----------|---------|-------|------|
| USD/MYR | X.XXXX | strengthening / weakening | YYYY-MM-DD |
| USD/MYR 30-day change | +/-X.X% | — | — |
| MYR direction | strengthening / weakening / stable | — | — |

## Commodities

| Indicator | Current | Trend | Date |
|-----------|---------|-------|------|
| CPO (Crude Palm Oil) 3rd month | RM X,XXX/tonne | rising / falling | YYYY-MM-DD |
| Brent Crude | $XX.XX/bbl | rising / falling | YYYY-MM-DD |
| Rubber (SMR20) | XXX sen/kg | — | YYYY-MM-DD |

## Fund flows

| Indicator | Value | Period |
|-----------|-------|--------|
| Foreign net (weekly) | +/- RM XXXM | week ending YYYY-MM-DD |
| Foreign net (MTD) | +/- RM X.XB | YYYY-MM |
| Foreign net (YTD) | +/- RM X.XB | YYYY |
| Flow trend | net buying / net selling / mixed | last 4 weeks |

## Market overview

- KLCI level: X,XXX.XX
- KLCI 30-day change: +/-X.X%
- Market breadth: advancers vs decliners ratio
- Sector rotation: <which sectors seeing inflows>

## Data gaps

<list what could not be fetched>
```

## Data sources

| Source | Data provided | Access |
|--------|--------------|--------|
| BNM (Bank Negara Malaysia) | OPR, SRR | BNM website / web search |
| Yahoo Finance | USD/MYR (MYRUSD=X), KLCI (^KLSE) | Free via yahoo_cache |
| TradingView / Bursa | CPO futures, fund flow | Via `bursa_flows.py` or web search |
| Web search | Commodity prices, fund flow summaries | Fallback |

### Scripts

Scripts referenced from `data/bursa-fundamentals/scripts/`:

- `bursa_flows.py` - fetches market overview data including top stocks by market cap, can be used to get flow direction signals.

### Yahoo Finance tickers for Bursa macro

- `MYRUSD=X` or `MYR=X` - USD/MYR rate
- `^KLSE` - KLCI index
- `FCPO` - Palm oil futures (may not be available on Yahoo, use web search)

### BNM data

BNM publishes OPR decisions on their website. No free API, so:
- Agent checks BNM website via web tools for latest OPR
- OPR changes are infrequent (4-6 times per year), so web search is sufficient

## Error handling

1. USD/MYR from Yahoo Finance is reliable. If it fails, this is unusual.
2. Commodity prices (palm oil) may not have a clean API. Web search for "CPO futures price today" is acceptable.
3. Fund flow data is the hardest to source. MIDF, CGS-CIMB publish weekly reports. Web search for "Bursa foreign fund flow this week" is the pragmatic approach.
4. BNM OPR changes rarely. Once fetched, it stays valid for weeks. If web search can't find it, use the last known value and note "may not reflect latest MPC decision."
5. Partial data is normal for Bursa macro. MYR + OPR + approximate CPO is sufficient for a useful assessment.

## Dependencies

- `utility/shared-lib` - `yahoo_cache.py` for MYR and KLCI fetching
- `utility/report-writer` - for scratch path conventions
- `utility/web-search` - for BNM OPR, CPO prices, fund flow data
