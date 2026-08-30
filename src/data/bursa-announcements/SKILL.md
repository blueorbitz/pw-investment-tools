---
name: bursa-announcements
description: Fetches Bursa Malaysia corporate announcements and insider transaction data including corporate actions, quarterly results, dividends, and share buybacks.
---

## Input

- `ticker` - Bursa stock code (e.g., `1155`, `5180`, `1155.KL`)
- `lookback` (optional) - how far back to search. Default: 30 days for insider transactions.

## Output format

Write to scratch at: `$ISK_NOTES/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/bursa-announcements.md`

```markdown
---
ticker: 1155
skill: bursa-announcements
date: 2024-03-15
status: complete | partial | unavailable
---

## Insider transactions (last 30 days)

| Date | Holder | Type | Shares | Price | Value (RM) |
|------|--------|------|--------|-------|------------|
| 2024-03-10 | Tan Sri X | Acquired | 500,000 | 9.50 | 4,750,000 |
| 2024-03-05 | Dato' Y | Disposed | 200,000 | 9.60 | 1,920,000 |

### Insider summary

- Net activity (30d): net buying | net selling | mixed | quiet
- Total acquired value: RM X.XM
- Total disposed value: RM X.XM
- Net value: +/- RM X.XM
- Notable: <any unusually large transactions or cluster activity>
- Institutional vs individual: <EPF/Persaraan patterns vs director personal trades>

## Recent corporate announcements

- Quarterly results: <latest QR summary if within 90 days>
- Dividend declarations: <recent ex-date, amount, payment date>
- Share buybacks: <any recent buyback activity>
- Corporate actions: <rights issues, bonus issues, share splits, etc.>
- Material announcements: <any other Bursa filings that matter>

## Fund flow context

- Foreign flow (if available): net buying | net selling | neutral
- Market overview signals: <from bursa_flows.py output>

## Data gaps

<list what could not be fetched>
```

## Data sources

### BursaWhale API (primary for insider transactions)

The existing `bursawhale_api.py` script handles OAuth authentication and fetches insider transaction data from the BursaWhale API.

**Environment variables required:**
- `BURSAWHALE_CLIENT_ID` - OAuth client ID
- `BURSAWHALE_CLIENT_SECRET` - OAuth client secret

Usage:
```bash
python scripts/bursawhale_api.py fetch '{"stockCode": "1155", "startDate": "2024-02-15", "endDate": "2024-03-15"}'
```

The script handles:
- OAuth token management (with local caching)
- Pagination for large result sets
- Aggregation by stock and by holder
- Institutional vs non-institutional classification

### Bursa Malaysia website

For corporate announcements (quarterly results, dividends, corporate actions):
- Agent uses web tools to check Bursa Malaysia announcement page
- No dedicated script (announcements are varied in format)

### Fallback: Web search

If BursaWhale API is unavailable:
- Search for insider transactions on i3investor, The Edge Markets
- Search for corporate announcements on Bursa website directly

## Scripts

Scripts live in `data/bursa-announcements/scripts/`:

- `bursawhale_api.py` - fetches insider transactions. Supports `fetch`, `aggregate_stock`, `aggregate_holder`, `get_dates` commands. Handles OAuth, pagination, institutional classification.

## Error handling

1. If `BURSAWHALE_CLIENT_ID` or `BURSAWHALE_CLIENT_SECRET` is not set, skip insider transaction data and note "BursaWhale credentials not configured."
2. If BursaWhale API is down or token refresh fails, try web search for recent insider transactions.
3. Corporate announcements are best-effort via web tools. If Bursa website is unreachable, note "corporate announcements unavailable."
4. Partial data is acceptable. Insider data alone (without corporate announcements) is still useful.
5. Error handling is lenient for Bursa data sources given their fragility. "Unavailable" is an acceptable status more often than for US data.

## Dependencies

- `utility/report-writer` - for scratch path conventions
- `utility/web-search` - fallback for announcements and insider data
