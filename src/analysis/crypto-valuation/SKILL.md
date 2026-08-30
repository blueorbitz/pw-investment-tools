---
name: crypto-valuation
description: Evaluates crypto token valuation using supply dynamics, protocol revenue, TVL trends, competitive position, and FDV-relative metrics.
---

## Input

Reads from scratch: `$ISK_NOTES/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/crypto-fundamentals.md`

## Output format

Write to scratch at: `$ISK_NOTES/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/crypto-valuation.md`

```markdown
---
ticker: ETH
skill: crypto-valuation
date: 2024-03-15
status: complete | partial | unavailable
---

## Valuation verdict

**Assessment: cheap | fair | expensive**

<one paragraph reasoning>

## Tokenomics scoring

- Supply inflation (annual): X.X% - <good (<5%) | concerning (5-15%) | dilutive (>15%)>
- Market cap / FDV ratio: X.XX - <fully circulating (>0.9) | moderate unlock ahead (0.5-0.9) | heavy dilution ahead (<0.5)>
- Upcoming unlocks (12mo): X.X% of circulating - <negligible (<5%) | moderate (5-15%) | severe pressure (>15%)>
- Token utility: <staking/governance/fee payment/gas/speculative only>
- Value accrual mechanism: <fees burned / distributed to stakers / treasury / none>

## Revenue quality (if applicable)

- Protocol revenue (annualized): $XXX.XM
- Revenue / FDV ratio: X.XX% - <attractive (>1%) | fair (0.3-1%) | expensive (<0.3%) | N/A>
- Revenue trend (30d): growing | declining | flat
- Revenue sustainability: <organic usage vs incentivized / one-time events>
- Fee distribution: <how value flows to token holders>

## TVL assessment (if applicable)

- TVL: $XX.XB
- TVL trend (30d): +X% | -X%
- TVL / FDV ratio: X.XX - <capital efficient (>1.0) | fair (0.5-1.0) | speculative (<0.5)>
- TVL composition: <sticky protocol-owned vs mercenary liquidity>
- TVL growth driver: <organic adoption vs token incentives>

## Competitive position

- Category: <L1, L2, DEX, Lending, etc.>
- Rank by TVL: #X of Y in category
- Rank by market cap: #X of Y
- Market cap premium/discount vs peers: <overvalued / in-line / undervalued relative to TVL and revenue>
- Moat assessment: <network effects / switching costs / brand / none>

## Supply risk assessment

- Unlock calendar risk: <next major unlock date and size>
- Whale concentration: top 10 hold XX% - <concentrated risk / well distributed>
- Exchange supply trend: <rising (sell pressure) / falling (accumulation)>

## Key risks to valuation

- <specific tokenomics risk>
- <competitive risk>
- <regulatory risk if relevant>

## Data gaps

<what could not be assessed>
```

## Analysis framework

1. **No-PE framework.** Crypto tokens cannot be valued like equities. Instead, use relative metrics within the token's category. Compare revenue/FDV, TVL/FDV, and market cap rank against peers in the same category (L1 vs L1, DEX vs DEX).

2. **Tokenomics scoring.** A good token has: low inflation, high circulating/total ratio, clear value accrual (burns or staking yield from real revenue), and no imminent large unlocks. A bad token has: high inflation, low float with cliffs ahead, no revenue sharing, and insider-heavy unlock schedule.

3. **TVL trend interpretation.** Rising TVL with flat/declining token incentives = organic growth (bullish). Rising TVL only because of high emissions = unsustainable. Declining TVL despite incentives = loss of confidence.

4. **Revenue quality.** Revenue from real user activity (trading fees, borrowing interest) is high quality. Revenue from token emissions given back as "yield" is circular and low quality. Look for revenue that would persist even if the token price dropped 50%.

5. **Competitive comparison.** A token ranked #3 in TVL but #7 in market cap may be undervalued relative to peers. A token ranked #2 in market cap but #8 in TVL may be riding narrative without substance.

6. **Unlock pressure.** If >10% of circulating supply unlocks in the next 3 months, this creates structural selling pressure regardless of fundamentals. Factor this into timing, not long-term thesis.

## Error handling

- If crypto-fundamentals scratch is `unavailable`, write `status: unavailable`.
- If key metrics are missing (no TVL for non-DeFi token like BTC), skip those sections and adjust framework. For BTC, focus on supply dynamics and network effects.
- If revenue data is not applicable (BTC, meme coins), note "not applicable" and focus on supply and demand dynamics.
- Never invent metrics. If data is missing, say so.

## Dependencies

- `data/crypto-fundamentals` - provides input data (reads its scratch)
