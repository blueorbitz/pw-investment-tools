---
name: portfolio-review
description: Fetches current prices for portfolio positions, compares against thesis/targets/stops, calculates P&L, and flags positions needing action.
---

## Input

Reads from: `$ISK_NOTES/portfolio/holdings.yaml`

## holdings.yaml schema

```yaml
# Portfolio holdings - git-tracked, machine-parseable
# All prices in local currency (USD for US, RM for Bursa, USD for crypto)

positions:
  - ticker: MSFT
    market: US
    account: ibkr          # optional, for multi-broker tracking
    entry_date: 2024-01-15
    entry_price: 380.50
    shares: 50
    target: 450.00
    stop: 340.00
    thesis: "Cloud growth re-acceleration + AI monetization in Azure"

  - ticker: "1155"
    market: Bursa
    account: mplus
    entry_date: 2024-02-01
    entry_price: 9.20
    shares: 5000
    target: 11.00
    stop: 8.00
    thesis: "Dividend yield 6%+ with stable ROE, MYR strengthening tailwind"

  - ticker: BTC/USD
    market: Crypto
    account: binance
    entry_date: 2024-03-01
    entry_price: 62000
    shares: 0.5            # fractional for crypto
    target: 100000
    stop: 52000
    thesis: "Halving cycle + ETF inflows + liquidity expansion"

  - ticker: ETH/USD
    market: Crypto
    account: binance
    entry_date: 2024-02-15
    entry_price: 3200
    shares: 5
    target: 5000
    stop: 2600
    thesis: "ETH ETF approval + deflationary supply post-merge"
    alert_conditions:      # optional, used by alert-checker
      - "alert if RSI > 75"
      - "alert if price drops below 200 SMA"
```

### Schema fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| ticker | string | yes | Asset ticker |
| market | string | yes | US, Bursa, or Crypto |
| account | string | no | Broker/exchange name for multi-account tracking |
| entry_date | date | yes | When position was opened (YYYY-MM-DD) |
| entry_price | number | yes | Average entry price |
| shares | number | yes | Number of shares/units (fractional OK) |
| target | number | yes | Target price for profit taking |
| stop | number | yes | Stop loss level |
| thesis | string | yes | One-line investment thesis |
| alert_conditions | list | no | Custom alert rules (used by alert-checker skill) |

## Pipeline steps

1. Read `$ISK_NOTES/portfolio/holdings.yaml`
2. For each position:
   a. Fetch current price (use `data/price-history` scripts or Yahoo Finance directly)
   b. Calculate: P&L %, distance to target, distance to stop
   c. Check: is stop breached? Is target reached? Is thesis still valid (based on simple checks)?
3. Compile results into a review report
4. Flag action items (positions needing attention)
5. Write output

## Output format

Write to: `$ISK_NOTES/portfolio/reviews/YYYY-MM/YYYY-MM-DD-portfolio-review.md`

```markdown
# Portfolio Review

Date: YYYY-MM-DD
Positions: X active
Accounts: ibkr, mplus, binance

## Action items

- STOP BREACHED: <TICKER> at $XX.XX (stop: $XX.XX) - REVIEW IMMEDIATELY
- TARGET REACHED: <TICKER> at $XX.XX (target: $XX.XX) - consider taking profit
- THESIS CHECK: <TICKER> - <reason thesis may be invalidated>

## Portfolio summary

| Ticker | Market | Account | Entry | Current | P&L% | vs Target | vs Stop | Status |
|--------|--------|---------|-------|---------|------|-----------|---------|--------|
| MSFT | US | ibkr | $380.50 | $415.20 | +9.1% | -7.7% away | +22.1% above | OK |
| 1155 | Bursa | mplus | RM9.20 | RM8.50 | -7.6% | -22.7% away | +6.3% above | WATCH |
| BTC/USD | Crypto | binance | $62,000 | $67,500 | +8.9% | -32.5% away | +29.8% above | OK |

## Position details

### MSFT (US, ibkr)

- Entry: $380.50 on 2024-01-15 (XX days held)
- Current: $415.20
- P&L: +$1,735.00 (+9.1%)
- Target: $450.00 (8.4% upside remaining)
- Stop: $340.00 (18.1% below current)
- Risk/reward from here: 1:1.0
- Thesis: "Cloud growth re-acceleration + AI monetization in Azure"
- Thesis status: intact | weakening | invalidated

### ... (repeat for each position)

## Account breakdown

| Account | Positions | Total P&L% (weighted) |
|---------|-----------|----------------------|
| ibkr | 1 | +9.1% |
| mplus | 1 | -7.6% |
| binance | 2 | +8.9% |
```

## Output path

`$ISK_NOTES/portfolio/reviews/YYYY-MM/YYYY-MM-DD-portfolio-review.md`

## Scheduling

Triggered directly by a scheduler / agent harness (e.g. a Hermes cron entry
configured to run the `monitor/portfolio-review` skill). There is no wrapper script:
the scheduler invokes the skill, and step 1 of the pipeline reads `holdings.yaml` and
handles the missing-file case. A weekly cadence suits most portfolios; run more often
if crypto-heavy. Configure the schedule in your harness, not here.

## Error handling

- If `holdings.yaml` does not exist, create a template file and instruct the user to populate it.
- If a ticker's price cannot be fetched, note "price unavailable" for that position and continue with others.
- If holdings.yaml has malformed entries, skip them with a warning in the output and process valid entries.
- Network errors should not abort the entire review. Fetch what you can and note failures.

## Dependencies

- `data/price-history` - for current price fetching (uses yahoo_cache)
- `utility/report-writer` - for output path conventions
