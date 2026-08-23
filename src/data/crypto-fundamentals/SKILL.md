# Crypto fundamentals data

## Purpose

Fetches tokenomics and protocol-level financial data for crypto assets. Covers market cap, fully diluted valuation, supply dynamics, TVL, protocol revenue, and token unlock schedules. This is the crypto equivalent of financial statements for equities.

This skill fetches and structures. It never interprets or judges the data.

## Input

- `ticker` - crypto asset (e.g., BTC/USD, ETH/USD, SOL/USD, or just BTC, ETH, SOL)
- The skill normalizes to CoinGecko token IDs internally (e.g., BTC → bitcoin, ETH → ethereum)

## Output format

Write to scratch at: `~/notes/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/crypto-fundamentals.md`

```markdown
---
ticker: ETH
skill: crypto-fundamentals
date: 2024-03-15
status: complete | partial | unavailable
---

## Market data

- Price: $X,XXX.XX
- Market cap: $XXX.XB
- Fully diluted valuation (FDV): $XXX.XB
- Market cap / FDV ratio: X.XX (1.0 = fully circulating)
- 24h volume: $X.XB
- Volume / market cap ratio: X.XX%

## Supply

- Circulating supply: XXX,XXX,XXX
- Total supply: XXX,XXX,XXX
- Max supply: XXX,XXX,XXX (or "unlimited" for inflationary tokens)
- Inflation rate (annual): X.X%
- Supply schedule: <brief description of emission curve>

## Token unlocks (next 12 months)

| Date | Amount | % of circulating | Category |
|------|--------|-----------------|----------|
| 2024-04-15 | 10,000,000 | 2.5% | Team vesting |
| 2024-07-01 | 5,000,000 | 1.2% | Ecosystem fund |

- Total upcoming unlock (12mo): XXX,XXX,XXX tokens (X.X% of current circulating)
- Next major unlock: <date and size>

## DeFi metrics (if applicable)

- Total Value Locked (TVL): $XX.XB
- TVL trend (30d): +X% | -X%
- TVL / FDV ratio: X.XX (higher = more capital efficiency)
- Protocol revenue (30d): $XX.XM
- Protocol fees (30d): $XX.XM
- Revenue annualized: $XXX.XM
- Revenue / FDV ratio (annualized): X.XX%
- Fee distribution: <where fees go: burned, treasury, stakers, LPs>

## Competitive position

- Category: <L1, L2, DeFi, etc.>
- Rank in category by TVL: #X of Y
- Rank in category by market cap: #X of Y

## Data gaps

<list metrics that could not be fetched>
```

## Data sources

| Source | Data provided | Access |
|--------|--------------|--------|
| CoinGecko API (free tier) | Market cap, FDV, supply, volume, price | No key needed (rate limited) |
| DeFiLlama API (free) | TVL, protocol revenue, fees | No key needed |
| TokenUnlocks / DeFiLlama unlocks | Vesting schedules | Free tier or web search |

### CoinGecko endpoints

- `/coins/{id}` - market data, supply, FDV
- `/coins/{id}/market_chart` - historical market cap for trend

### DeFiLlama endpoints

- `/protocol/{name}` - TVL history
- `/summary/fees/{name}` - fees and revenue

### Token unlock data

No single reliable free API. Use a combination of:
- DeFiLlama unlocks endpoint (covers major tokens)
- Web search fallback for specific unlock schedules
- Project documentation / tokenomics pages

## Error handling

1. CoinGecko rate limits (30 calls/min free tier): if hit, wait 60 seconds and retry once. If still failing, report partial data.
2. DeFiLlama has no rate limit for basic queries. If it's down, skip DeFi metrics and note "TVL/revenue unavailable."
3. Token unlock data is the hardest to source reliably. If unavailable, note it and mark as a gap. This alone should not make `status: unavailable`.
4. For BTC/ETH (no DeFi protocol revenue in traditional sense), skip DeFi metrics section and note "not applicable."
5. If CoinGecko cannot find the token ID, try web search to confirm the correct ID mapping.

## Dependencies

- `utility/report-writer` - for scratch path conventions
- `utility/web-search` - fallback for unlock schedules and token ID resolution
