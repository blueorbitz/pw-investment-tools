---
name: alert-checker
description: Reads holdings.yaml, evaluates custom alert conditions against current market data, and writes output only when conditions are breached.
---

When no conditions are breached, this skill writes nothing (silent success).

## Input

Reads from: `$ISK_NOTES/portfolio/holdings.yaml`

Specifically looks for positions that have the optional `alert_conditions` field.

## alert_conditions field in holdings.yaml

The `alert_conditions` field is an optional list of free-text rules on each position. The agent interprets and evaluates these against current data.

```yaml
positions:
  - ticker: MSFT
    market: US
    entry_date: 2024-01-15
    entry_price: 380.50
    shares: 50
    target: 450.00
    stop: 340.00
    thesis: "Cloud growth re-acceleration"
    alert_conditions:
      - "alert if RSI > 70"
      - "alert if price drops below 200 SMA"
      - "alert if earnings miss (next quarterly report)"

  - ticker: BTC/USD
    market: Crypto
    entry_date: 2024-03-01
    entry_price: 62000
    shares: 0.5
    target: 100000
    stop: 52000
    thesis: "Halving cycle + ETF inflows"
    alert_conditions:
      - "alert if funding rate > 0.05% for 3 consecutive days"
      - "alert if price drops below 21 EMA on daily"
      - "alert if DXY breaks above 107"

  - ticker: "1155"
    market: Bursa
    entry_date: 2024-02-01
    entry_price: 9.20
    shares: 5000
    target: 11.00
    stop: 8.00
    thesis: "Dividend yield play"
    alert_conditions:
      - "alert if dividend yield drops below 4%"
      - "alert if foreign fund selling >RM100M in a week"
```

### Supported condition patterns

The agent interprets these common patterns:

| Pattern | Data needed | How to check |
|---------|------------|--------------|
| "alert if RSI > X" or "< X" | price-history indicators | Run price_history.py, check RSI value |
| "alert if price drops below X SMA" | price-history MA levels | Compare price to MA value |
| "alert if price above/below $X" | current price | Simple price comparison |
| "alert if DY drops below X%" | fundamentals + price | Calculate yield from DPS/price |
| "alert if funding rate > X%" | crypto-derivatives | Check Binance funding rate |
| "alert if DXY breaks above X" | crypto-macro | Check DXY level |
| "alert if volume > Xx average" | price-history volume | Check volume ratio |
| "alert if earnings miss" | web search | Check recent earnings result |
| "alert if foreign fund selling" | web search / bursa data | Check fund flow reports |

For conditions the agent cannot evaluate programmatically, it notes "requires manual check" and does not fire the alert.

## Pipeline steps

1. Read `$ISK_NOTES/portfolio/holdings.yaml`
2. Filter to positions with `alert_conditions` field
3. For each position with alerts:
   a. Fetch required data (price, indicators, fundamentals as needed)
   b. Evaluate each condition
   c. Classify: breached | not breached | cannot evaluate
4. If ANY conditions are breached, write alert output
5. If NO conditions are breached, write nothing (silent success)

## Output format

Write ONLY when alerts fire, to: `$ISK_NOTES/portfolio/alerts/YYYY-MM/YYYY-MM-DD-alerts.md`

```markdown
# Alert Report

Date: YYYY-MM-DD HH:MM
Positions checked: X
Alerts fired: Y

## Fired alerts

### MSFT - RSI overbought

- Condition: "alert if RSI > 70"
- Current RSI: 74.3
- Status: BREACHED
- Implication: Stock is technically overbought. Consider tightening stop or taking partial profit.
- Action suggested: Review position, consider reducing if near target.

### BTC/USD - Funding rate elevated

- Condition: "alert if funding rate > 0.05% for 3 consecutive days"
- Current funding: 0.062% (3-day avg: 0.058%)
- Status: BREACHED
- Implication: Longs are crowded and paying heavily. Potential long squeeze setup.
- Action suggested: Consider tightening stop. Do not add to position at current funding levels.

## Conditions checked (not breached)

| Ticker | Condition | Current value | Status |
|--------|-----------|---------------|--------|
| MSFT | price below 200 SMA | Price $415 > 200 SMA $385 | OK |
| BTC/USD | price below 21 EMA | Price $67,500 > 21 EMA $65,200 | OK |
| BTC/USD | DXY above 107 | DXY 104.2 | OK |
| 1155 | DY below 4% | DY 5.8% | OK |

## Could not evaluate

| Ticker | Condition | Reason |
|--------|-----------|--------|
| MSFT | earnings miss | No recent earnings report found |
| 1155 | foreign fund selling | Fund flow data unavailable today |
```

## Output path

`$ISK_NOTES/portfolio/alerts/YYYY-MM/YYYY-MM-DD-alerts.md`

Only written when at least one alert fires. If nothing fires, no file is created.

## Silent success behavior

When no conditions are breached:
- No file is written
- This is the expected outcome most days
- The absence of an alert file means "all conditions OK"

The first pipeline step is a deterministic precondition check: if `holdings.yaml`
is missing or has no `alert_conditions`, stop immediately and write nothing.

## Scheduling

This skill is meant to be triggered directly by a scheduler / agent harness (e.g. a
Hermes cron entry configured to run the `monitor/alert-checker` skill). There is no
wrapper script — the scheduler invokes the skill, and the skill does its own
precondition checks as step 1. Configure the schedule in your harness, not here.

| Market focus | Suggested frequency | Rationale |
|--------------|--------------------|-----------| 
| US equities only | Daily (pre-market) | Markets move only during hours |
| Crypto positions | Every 4-6 hours | 24/7 market, faster moves |
| Mixed portfolio | Daily minimum, 4h if crypto-heavy | Balance coverage vs API load |

## Error handling

- If `holdings.yaml` does not exist or has no `alert_conditions`, exit silently (no error, no output).
- If price data cannot be fetched for a position, mark its conditions as "cannot evaluate" and continue checking other positions.
- If an alert condition is too ambiguous to evaluate, note it in "Could not evaluate" section. Do not fire a false alert.
- Network errors should not generate false alerts. When in doubt, classify as "cannot evaluate" rather than "breached."
- Partial evaluation is acceptable. Check what you can.

## Dependencies

- `data/price-history` - for price, indicators, MA levels
- `data/crypto-derivatives` - for funding rate conditions (crypto only)
- `utility/web-search` - for news-based conditions (earnings, fund flows)
- `utility/report-writer` - for output path conventions
- `monitor/portfolio-review` - shares the holdings.yaml schema
