---
name: us-filings
description: Fetches SEC filing data for US equities including insider transactions (Form 4), institutional holdings changes (13F), and recent 10-K/10-Q highlights.
---

## Input

- `ticker` - US equity ticker (e.g., MSFT, AAPL, NVDA)
- `lookback` (optional) - how far back to search for filings. Default: 90 days for Form 4, latest quarter for 13F, most recent for 10-K/10-Q.

## Output format

Write to scratch at: `$ISK_NOTES/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/us-filings.md`

```markdown
---
ticker: MSFT
skill: us-filings
date: 2024-03-15
status: complete | partial | unavailable
---

## Insider transactions (Form 4, last 90 days)

| Date | Insider | Title | Type | Shares | Price | Value |
|------|---------|-------|------|--------|-------|-------|
| 2024-03-10 | John Smith | CFO | Buy | 5,000 | $410.50 | $2.05M |
| 2024-02-28 | Jane Doe | CEO | Sell | 10,000 | $405.00 | $4.05M |

### Insider summary

- Net insider activity (90 days): net buyer | net seller | mixed
- Notable transactions: <any unusually large buys/sells or cluster buying>
- Officer vs director breakdown: <who is buying/selling>

## Institutional holdings (13F, latest quarter)

- Top new positions: <notable institutions initiating positions>
- Top exits: <notable institutions closing positions>
- Net institutional sentiment: increasing | decreasing | stable

## Recent filings summary

### Latest 10-K/10-Q highlights

- Filing date: YYYY-MM-DD
- Revenue guidance (if provided): <any forward guidance>
- Risk factors flagged: <new or notable risk disclosures>
- Key operational metrics: <anything material that stands out>
- Management commentary highlights: <tone and forward outlook>

## Options flow (if available)

- Unusual options activity: <large block trades, notable put/call imbalance>
- Put/call ratio context: <elevated puts or calls relative to normal>

## Data gaps

<list what could not be fetched>
```

## Data sources

### SEC EDGAR

- **Form 4 (insider transactions):** SEC EDGAR full-text search or structured RSS feed
  - Endpoint: `https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=<ticker>&type=4&dateb=&owner=include&count=40`
  - Requires `SEC_EDGAR_USER_AGENT` env var (format: "YourName your@email.com")
- **13F (institutional holdings):** Quarterly filings, look for recent changes
- **10-K/10-Q:** Most recent annual/quarterly report

### Scripts

Scripts live in `data/us-filings/scripts/`:

- `sec_filings.py` - fetches recent SEC filings by type. Handles EDGAR rate limiting and user-agent requirements.
- `options_flow.py` - unusual options activity. Commands: `scan <TICKER> [expiry]`, `sentiment <TICKER>`, `multi <T1,T2,...>`. Uses Yahoo cookie/crumb auth; when auth fails, mark options flow `unavailable` and continue (the rest of us-filings does not depend on it).

**Environment variable required:** `SEC_EDGAR_USER_AGENT`

Set to your name and email (SEC requires identification): `"John Doe john@example.com"`

### Fallback: Web search

If EDGAR API is unavailable or rate-limited, use `utility/web-search` to find recent insider transaction summaries from financial news sites (OpenInsider, SEC.report, etc.).

## Error handling

1. If `SEC_EDGAR_USER_AGENT` is not set, attempt web search as fallback for insider data. Note the limitation.
2. If EDGAR rate-limits the request (HTTP 429), back off and note "rate limited, partial data."
3. Form 4 data is the highest priority. If only Form 4 is available, that's still useful.
4. 13F data is quarterly and may be stale. Note the quarter date so the analysis skill knows how fresh it is.
5. 10-K/10-Q summaries are best-effort. If the filing is too long to parse meaningfully, extract just the "Risk Factors" updates and management guidance.
6. If all sources fail, write `status: unavailable` with reason.

## Dependencies

- `utility/web-search` - fallback when EDGAR is unavailable
- `utility/report-writer` - for scratch path conventions
