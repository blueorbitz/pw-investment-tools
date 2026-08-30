---
name: crypto-onchain
description: Fetches on-chain metrics for crypto assets including exchange flows, whale wallet behavior, active addresses, and staking ratios.
---

## Input

- `ticker` - crypto asset (e.g., BTC, ETH, SOL)
- `lookback` (optional) - period for trend data. Default: 30 days.

## Output format

Write to scratch at: `$ISK_NOTES/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/crypto-onchain.md`

```markdown
---
ticker: BTC
skill: crypto-onchain
date: 2024-03-15
status: complete | partial | unavailable
---

## Exchange flows

- Exchange balance (total across major exchanges): XXX,XXX BTC
- 7-day net flow: +/-XXX BTC (positive = inflows = potential selling pressure)
- 30-day net flow: +/-X,XXX BTC
- Exchange balance trend (30d): increasing | decreasing | flat
- Interpretation hint: decreasing exchange balance = accumulation signal

## Whale wallets

- Wallets holding >1000 BTC: X,XXX (trend: increasing | decreasing)
- Whale accumulation (30d): net +/-XXX BTC
- Top wallet activity: <any notable large transfers in last 7 days>
- Dormant supply reactivation: <any old coins moving, signals long-term holder distribution>

## Network activity

- Daily active addresses (7d avg): XXX,XXX
- Active address trend (30d): rising | falling | flat
- Transaction count (7d avg): XXX,XXX
- Average transaction value: $XX,XXX
- New addresses (7d avg): XX,XXX (network growth signal)

## Staking (if applicable)

- Total staked: XXX,XXX,XXX tokens (XX% of circulating)
- Staking trend (30d): increasing | decreasing | flat
- Staking APR: X.X%
- Net staking flow (30d): +/-XXX,XXX tokens
- Interpretation hint: increasing stake ratio = reduced circulating supply = supply squeeze

## Supply distribution

- Top 10 holders: XX% of supply
- Top 100 holders: XX% of supply
- Concentration trend: increasing | decreasing | stable

## Data gaps

<list what could not be fetched>
```

## Data sources

| Source | Data provided | Access |
|--------|--------------|--------|
| Glassnode (free tier) | Exchange flows, active addresses (BTC/ETH only) | Limited free endpoints |
| CryptoQuant (free tier) | Exchange flows, whale alerts | Limited free access |
| Blockchain explorers | Whale wallets, staking data | Direct API calls |
| DeFiLlama | Staking data for PoS chains | Free, no key |

### Coverage limitations

Free tiers of Glassnode and CryptoQuant cover BTC and ETH well. For altcoins (SOL, AVAX, etc.), on-chain data is harder to source for free:
- Use blockchain-specific explorers (Solscan, Snowtrace)
- DeFiLlama for staking data
- Web search for whale tracking services

### Environment variables

No API keys strictly required for basic access, but having them improves data quality:

| Env var | Source | Benefit |
|---------|--------|---------|
| `GLASSNODE_API_KEY` | Glassnode | More endpoints, longer history |
| `CRYPTOQUANT_API_KEY` | CryptoQuant | Real-time exchange flows |

These are optional. The skill functions without them using free tier endpoints and web search fallback.

## Error handling

1. Free tier rate limits: if hit, note which metrics are unavailable. Partial on-chain data is still useful.
2. BTC and ETH have best coverage. For other tokens, expect `status: partial` with some sections empty.
3. If no on-chain source is available for a token, try web search for recent whale tracking reports and note the lower confidence.
4. Exchange flow data may lag by hours. Note the timestamp of the most recent data point.
5. If all sources fail, write `status: unavailable`. On-chain is valuable but the pipeline can continue without it.

## Dependencies

- `utility/report-writer` - for scratch path conventions
- `utility/web-search` - fallback for altcoin on-chain data
