# Watchlist scan monitor

## Purpose

Reads the watchlist file, performs lightweight checks on each tracked ticker (price movement, entry condition status, material news, upcoming catalysts), and writes a scan summary. This is a lighter-weight check than portfolio review: the goal is to flag when it's time to enter a position, not to track an existing one.

## Input

Reads from: `~/notes/watchlist/watchlist.yaml`

## watchlist.yaml schema

```yaml
# Watchlist - tickers being tracked for potential entry
# Lighter than holdings: no position yet, just watching for conditions

tickers:
  - ticker: NVDA
    market: US
    added_date: 2024-02-01
    added_price: 680.00        # price when added to watchlist
    entry_condition: "Buy on pullback to 50 SMA or breakout above $750 with volume"
    catalyst_date: 2024-05-22  # optional: earnings date, event date
    catalyst: "Q1 earnings - data center revenue guidance"
    notes: "AI capex cycle beneficiary, want to own but waiting for better entry"

  - ticker: "7113"
    market: Bursa
    added_date: 2024-01-15
    added_price: 1.50
    entry_condition: "Buy if breaks above RM1.80 with volume >5M shares"
    notes: "Turnaround play, waiting for revenue inflection confirmation"

  - ticker: SOL/USD
    market: Crypto
    added_date: 2024-03-01
    added_price: 120.00
    entry_condition: "Buy on retest of $100 support or breakout above $150"
    catalyst_date: 2024-06-01
    catalyst: "Firedancer validator client launch"
    notes: "High-performance L1, DePIN narrative tailwind"

  - ticker: AMZN
    market: US
    added_date: 2024-02-20
    added_price: 170.00
    entry_condition: "Buy below $160 or on AWS re-acceleration signal"
    notes: "Retail margin expansion + AWS growth"
```

### Schema fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| ticker | string | yes | Asset ticker |
| market | string | yes | US, Bursa, or Crypto |
| added_date | date | yes | When added to watchlist (YYYY-MM-DD) |
| added_price | number | yes | Price at time of addition (reference point) |
| entry_condition | string | yes | Free-text description of when to buy |
| catalyst_date | date | no | Upcoming event date |
| catalyst | string | no | Description of upcoming catalyst |
| notes | string | no | Additional context |

## Pipeline steps

1. Read `~/notes/watchlist/watchlist.yaml`
2. For each ticker:
   a. Fetch current price (use yahoo_cache or agent tools)
   b. Calculate % change since added to watchlist
   c. Evaluate entry condition against current data (agent interprets free-text condition)
   d. Check if catalyst_date is within 7 days (flag as imminent)
   e. Quick news check (web search for material changes, optional)
3. Sort results: conditions-met first, then catalysts-imminent, then by % change
4. Write scan summary

## Output format

Write to: `~/notes/watchlist/scans/YYYY-MM/YYYY-MM-DD-watchlist-scan.md`

```markdown
# Watchlist Scan

Date: YYYY-MM-DD
Tickers tracked: X

## Entry conditions met

- NVDA: Current $745, +9.6% since added. Approaching $750 breakout level. WATCH CLOSELY for volume confirmation.
- SOL/USD: Current $98, retesting $100 support zone. Entry condition approaching.

## Catalysts imminent (within 7 days)

- NVDA: Q1 earnings on 2024-05-22 (3 days away). Consider pre-earnings entry or wait for reaction.

## Watchlist overview

| Ticker | Market | Added | Added Price | Current | Change | Entry Condition Status |
|--------|--------|-------|-------------|---------|--------|----------------------|
| NVDA | US | 2024-02-01 | $680.00 | $745.00 | +9.6% | approaching |
| 7113 | Bursa | 2024-01-15 | RM1.50 | RM1.65 | +10.0% | not met |
| SOL/USD | Crypto | 2024-03-01 | $120.00 | $98.00 | -18.3% | approaching |
| AMZN | US | 2024-02-20 | $170.00 | $182.00 | +7.1% | not met |

## Entry condition status key

- **met** - condition is satisfied, consider entering
- **approaching** - close to being met (within 5% of trigger level or condition partially satisfied)
- **not met** - condition not close to being satisfied
- **invalidated** - setup has changed, condition may no longer be relevant

## Ticker details

### NVDA (US)

- Current: $745.00 (+9.6% since added)
- Entry condition: "Buy on pullback to 50 SMA or breakout above $750 with volume"
- Assessment: Price at $745, 50 SMA at $690. Breakout level ($750) is 0.7% away. Watch for volume surge.
- Catalyst: Q1 earnings on 2024-05-22
- Action: Monitor closely for breakout confirmation

### ... (repeat for each)

## Removed / graduated

<tickers removed from watchlist since last scan, if any>
```

## Output path

`~/notes/watchlist/scans/YYYY-MM/YYYY-MM-DD-watchlist-scan.md`

## Entry condition evaluation

The agent interprets free-text entry conditions by:

1. Parsing the condition for price levels, indicator references, or event triggers
2. Fetching relevant data (current price, 50 SMA from price-history, volume)
3. Comparing current state against the condition
4. Classifying as: met, approaching, not met, or invalidated

Common condition patterns and how to evaluate:

| Pattern | How to check |
|---------|-------------|
| "Buy below $X" | Compare current price to $X |
| "Buy on breakout above $X" | Check if price > $X |
| "Buy on breakout above $X with volume" | Check price > $X AND volume > 1.5x average |
| "Buy on pullback to 50 SMA" | Check if price is within 2% of 50 SMA |
| "Buy if RSI < 30" | Check RSI from price-history |
| "Buy on retest of $X support" | Check if price touched $X and bounced |

For complex conditions, use best judgment and explain the assessment.

## Error handling

- If `watchlist.yaml` does not exist, create a template file and instruct the user to populate it.
- If a ticker's price cannot be fetched, note "price unavailable" and skip that ticker's evaluation.
- If entry condition is too vague to evaluate programmatically, note "condition requires manual assessment" and provide current price context.
- Partial scan is acceptable. Evaluate what you can.

## Dependencies

- `data/price-history` - for current price and indicator data
- `utility/web-search` - for catalyst news and material changes
- `utility/report-writer` - for output path conventions
