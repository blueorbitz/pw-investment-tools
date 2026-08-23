# Macro context analysis

## Purpose

Synthesizes macro data into a market-level opinion (bullish/bearish/neutral) for the target asset's market. This is a shared skill that routes internally by market: it reads from whichever macro data skill matches the ticker's market (US, Bursa, or Crypto). Produces a concise macro backdrop assessment that the verdict synthesis skill can weigh against stock-specific factors.

This skill interprets macro data. It never fetches raw data itself.

## Input

- `market` - which market to assess: `US`, `Bursa`, or `Crypto`

Reads from the corresponding macro data scratch file:
- US: `~/notes/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/us-macro.md`
- Bursa: `~/notes/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/bursa-macro.md`
- Crypto: `~/notes/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/crypto-macro.md`

## Output format

Write to scratch at: `~/notes/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/macro-context.md`

```markdown
---
ticker: <TICKER>
skill: macro-context
date: 2024-03-15
status: complete | partial | unavailable
market: US | Bursa | Crypto
---

## Macro stance

**Assessment: bullish | bearish | neutral**
**Confidence: high | medium | low**

## Key drivers

- <driver 1: specific indicator and its implication>
- <driver 2>
- <driver 3>

## Tailwinds

- <factor supporting risk assets in this market>
- <factor 2>

## Headwinds

- <factor working against risk assets>
- <factor 2>

## Regime context

<one paragraph describing the current macro regime and where we are in the cycle>

## Impact on individual stocks

<how this macro backdrop should influence position sizing and conviction for stock-level decisions>
```

## Analysis framework

### US market

Weigh these factors (roughly in priority order):

1. **Fed stance and trajectory.** Hiking = headwind. Holding at peak = transition. Cutting = tailwind. The direction matters more than the level.

2. **Yield curve shape.** Deeply inverted = recession warning (bearish equities 6-18 months out). Un-inverting after inversion = recession may be imminent. Steep = growth recovery.

3. **Net liquidity.** Fed balance sheet minus RRP minus TGA. Rising net liquidity is bullish for risk assets. Falling is bearish. This is the single best leading indicator for US equity direction.

4. **Inflation trajectory.** Falling CPI/PCE toward target = Fed can ease = bullish. Sticky/reaccelerating inflation = higher-for-longer = headwind.

5. **Growth indicators.** ISM above 50 = expansion. Below 50 = contraction. The trend matters: ISM rising from 45 to 48 is bullish (improving) even though still below 50.

**Scoring:**
- Bullish: liquidity rising + Fed easing/pausing + curve normalizing + growth improving
- Bearish: liquidity falling + Fed tightening + curve inverting + growth deteriorating
- Neutral: mixed signals or transition period

### Bursa Malaysia market

Weigh these factors:

1. **BNM OPR (Overnight Policy Rate).** Cutting = stimulative = bullish for rate-sensitive stocks (banks, property). Hiking = headwind.

2. **USD/MYR exchange rate.** Strengthening MYR = foreign fund inflow = bullish for KLCI. Weakening MYR = capital outflow pressure.

3. **Commodity cycle.** Palm oil (FCPO) and petrochemicals drive a large chunk of Bursa earnings. Rising commodity prices = bullish for plantation and energy sectors.

4. **ASEAN fund flows.** Is foreign money entering or leaving Malaysian equities? Net foreign buying = bullish backdrop.

5. **China/ASEAN growth linkage.** Malaysia is trade-dependent. Strong China demand = positive spillover.

**Scoring:**
- Bullish: MYR strengthening + foreign buying + commodity prices rising + OPR stable/cutting
- Bearish: MYR weakening + foreign selling + commodities declining + OPR hiking
- Neutral: mixed signals

### Crypto market

Weigh these factors:

1. **Fed net liquidity.** Same as US. Crypto is a high-beta liquidity play. Rising liquidity is the strongest bullish signal for crypto.

2. **DXY (US Dollar Index).** Falling DXY = bullish crypto. Rising DXY = headwind. Crypto trades inversely to dollar strength.

3. **Stablecoin total supply.** Rising stablecoin supply (USDT + USDC) = new money entering crypto ecosystem = bullish. Declining = redemptions = bearish.

4. **BTC ETF net flows (if available).** Net inflows = institutional demand = bullish. Net outflows = distribution.

5. **Risk appetite proxy.** If US equities are rallying and VIX is low, crypto tends to perform. Risk-off environments (VIX spikes, equity selloffs) hit crypto harder.

**Scoring:**
- Bullish: liquidity rising + DXY falling + stablecoin supply growing + ETF inflows
- Bearish: liquidity falling + DXY rising + stablecoin supply shrinking + ETF outflows
- Neutral: mixed signals or liquidity flat

## Error handling

- If the macro data scratch is `unavailable`, write `status: unavailable` with reason "no macro data to interpret."
- If the macro data is `partial`, assess what you can and mark `status: partial`. State which factors could not be evaluated.
- For Bursa and Crypto markets where macro data skills may not yet exist, note this and provide a best-effort assessment using whatever data is available (possibly from web search via the orchestrator).
- Never fabricate macro data. If an indicator is missing, skip it in the analysis and lower confidence.

## Dependencies

Conditional by market:
- `data/us-macro` - when market is US
- `data/bursa-macro` - when market is Bursa
- `data/crypto-macro` - when market is Crypto
