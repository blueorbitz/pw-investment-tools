# Crypto on-chain analysis

## Purpose

Interprets on-chain data from `data/crypto-onchain` into actionable signals: accumulation vs distribution phases, whale behavior patterns, and network health assessment. On-chain analysis is unique to crypto and provides insight into what participants are doing with their actual tokens, not just price action.

This skill interprets. It never fetches raw data itself.

## Input

Reads from scratch: `$ISK_NOTES/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/crypto-onchain.md`

## Output format

Write to scratch at: `$ISK_NOTES/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/crypto-onchain-analysis.md`

```markdown
---
ticker: BTC
skill: crypto-onchain-analysis
date: 2024-03-15
status: complete | partial | unavailable
---

## On-chain verdict

**Phase: accumulation | distribution | neutral**
**Confidence: high | medium | low**

<one paragraph summarizing the on-chain picture>

## Accumulation/distribution framework

- Exchange balance trend: decreasing (accumulation) | increasing (distribution) | flat
- Net exchange flow (30d): <inflows = sell pressure / outflows = accumulation>
- Signal strength: strong | moderate | weak
- Context: <is this consistent with price action or diverging?>

### Divergence detection

- Price falling + exchange outflows = strong accumulation signal (smart money buying the dip)
- Price rising + exchange inflows = potential distribution (insiders selling into strength)
- Price rising + exchange outflows = healthy trend (supply shrinking while demand rises)
- Price falling + exchange inflows = capitulation (potential bottom if extreme)

## Whale behavior

- Whale wallet count trend (30d): increasing | decreasing | stable
- Whale accumulation signal: <net buying / selling / neutral>
- Notable activity: <any large transfers, new whale wallets, dormant supply reactivation>
- Dormant coin movement: <old coins waking up = potential distribution by early holders>
- Signal interpretation: <what whale behavior suggests about their outlook>

## Network health

- Active addresses trend: growing | declining | flat
- New address growth: <healthy network expansion or stagnation>
- Transaction activity: <increasing usage or declining interest>
- Health assessment: strong | stable | weakening | concerning

### Network health context

- Growing active addresses with rising price = organic demand growth
- Growing active addresses with falling price = adoption continuing despite price weakness (bullish divergence)
- Declining active addresses with rising price = speculative rally without fundamental backing (fragile)
- Declining active addresses with falling price = bear market, interest fading

## Supply dynamics

- Staking ratio trend: <increasing = supply squeeze / decreasing = unlocking for sale>
- Supply concentration: <getting more concentrated (risk) or dispersing (healthy)>
- Liquid supply assessment: <how much supply is realistically available to sell>
- Supply squeeze potential: <conditions present for supply-driven rally?>

## Composite signal

| Factor | Signal | Weight | Direction |
|--------|--------|--------|-----------|
| Exchange flows | outflow / inflow | 35% | bullish / bearish |
| Whale behavior | accumulating / distributing | 30% | bullish / bearish |
| Network health | growing / declining | 20% | bullish / bearish |
| Supply dynamics | tightening / loosening | 15% | bullish / bearish |

Net on-chain signal: bullish | bearish | neutral

## Key observations

- <most notable on-chain signal and what it implies>
- <second observation>
- <third observation>

## Data gaps

<what could not be assessed>
```

## Analysis framework

1. **Accumulation/distribution detection.** Exchange balance is the primary signal. When tokens flow off exchanges, someone is moving them to cold storage (accumulation). When they flow onto exchanges, someone is preparing to sell (distribution). The rate of change matters more than absolute levels.

2. **Whale signal interpretation.** Whales (large holders) tend to be better informed. Whale accumulation during drawdowns is one of the strongest bullish signals in crypto. Whale distribution during rallies signals smart money taking profit.

3. **Dormant supply reactivation.** When coins that haven't moved in years suddenly move, this often signals early holders (who bought much cheaper) are distributing. This is bearish if it happens at elevated prices and bullish context is lacking.

4. **Network health as trend confirmation.** On-chain activity should confirm price trends. A rally supported by growing active addresses and transaction counts is healthier than one driven purely by derivatives speculation.

5. **Supply squeeze conditions.** When staking ratios rise, exchange balances decline, and supply concentrates in long-term holders, the available sell-side supply shrinks. Any demand shock in this condition leads to outsized price moves upward.

## Error handling

- If crypto-onchain scratch is `unavailable`, write `status: unavailable` with reason.
- If only partial data (e.g., exchange flows but no whale data), assess what's available and mark `status: partial`.
- For altcoins with poor on-chain coverage, the analysis will be limited. Note which metrics are estimates vs confirmed data.
- If all data is "unavailable" in the input, state that clearly. The verdict synthesis skill will reduce on-chain weight to zero.

## Dependencies

- `data/crypto-onchain` - provides all input data (reads its scratch)
