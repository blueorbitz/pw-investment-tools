---
name: business-profile
description: Builds the company business profile for equities: what it sells, segment mix, customers, pricing power evidence, competitors, and moat inputs. Required upstream for quality-gate dispatch B and bursa-valuation.
---

Data skill: fetches and normalizes, never judges. The moat verdict stays with
quality-gate dispatch B (US) and bursa-valuation (Bursa). This skill supplies
the facts those judgments cite.

## Scope

US and Bursa equities only. Crypto is out of scope — tokenomics use
`crypto-fundamentals`.

## Input

- `ticker` - US symbol (e.g. `MSFT`) or Bursa code (e.g. `1155`, `1155.KL`)

## Output format

Write to scratch at: `$ISK_NOTES/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/business-profile.md`

```markdown
---
ticker: MSFT
skill: business-profile
date: 2024-03-15
status: complete | partial | unavailable
---

## What it sells

- <2-3 sentences: core products/services, how it makes money>
- Revenue mix: <segment split with % from latest 10-K / annual report>
- Customer type: <enterprise | consumer | government | mix, concentration if disclosed>

## Unit economics

- Gross margin (5Y trend): <numbers + direction>
- ROIC or ROE (5Y trend): <numbers + direction>
- Pricing evidence: <price increases taken, NRR/churn if SaaS, same-store sales if retail>

## Competitive position

- Top 3 competitors: <names + share where available>
- Market share trend: <gaining | stable | losing + evidence>
- Share-shift driver: <why share moved, one line>

## Moat inputs (facts only, no verdict)

- Switching costs: <NRR, retention, contract length>
- Scale/cost: <relative scale, margin gap vs peers>
- Intangibles: <brands, patents, licenses with expiry where known>
- What would kill it: <one line, biggest structural threat>

## Sources

- <10-K Item 1 / annual report page, MD&A note, investor day, etc.>

## Data gaps

<what could not be sourced, with reason>
```

## Data sources

### US

1. Latest 10-K Item 1 (business) and Item 7 (MD&A) via SEC EDGAR.
   Requires `SEC_EDGAR_USER_AGENT`. Segment revenue split and customer
   concentration come from here, nowhere else.
2. Investor relations / earnings slides for segment mix when the 10-K is stale.
3. `utility/web-search` for competitor share and NRR/churn only when filings
   do not disclose them. Mark each such fact `[web]`.

### Bursa

1. Latest annual report (business review + segmental note to the accounts).
   Bursa announcements page or company IR site.
2. Latest quarterly report for segment revenue when the annual is stale.
3. `data/bursa-announcements` scratch for corporate actions affecting mix.
4. `utility/web-search` for competitor share. Mark each such fact `[web]`.

## Rules

- Every number carries a source: filing page/note, or `[web]` with outlet.
- Segment mix must sum to ~100%. If segments are undisclosed, say so and fall
  back to product-line revenue from MD&A.
- No moat verdict here. Words like wide/narrow belong to dispatch B and
  bursa-valuation, which cite this file.
- 5Y margin/ROIC trends reuse `fundamentals.md` scratch when present; do not
  re-fetch statements.

## Error handling

1. If EDGAR / annual report is unreachable, try web search for segment mix.
   Still mark `status: partial`.
2. If only headline revenue exists (no segment split), write what you have,
   mark `status: partial`, and name the gap. Dispatch B caps moat at narrow
   on a partial profile.
3. If all sources fail, write `status: unavailable` with reason.

## Dependencies

- `data/fundamentals` scratch - headline statements for trend cross-check (upstream, already written)
- `data/us-filings` (US) - shares the EDGAR access pattern and user-agent requirement
- `data/bursa-announcements` (Bursa) - corporate actions affecting mix
- `utility/web-search` - competitor share and undisclosed metrics fallback
- `utility/report-writer` - for scratch path conventions
