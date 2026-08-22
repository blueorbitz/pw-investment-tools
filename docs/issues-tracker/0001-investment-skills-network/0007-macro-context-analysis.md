# 0007: Macro context analysis skill

**What to build:** `analysis/macro-context/SKILL.md` that synthesizes macro data into a market-level opinion (bullish/bearish/neutral) for the target market. This is a shared skill: it reads from whichever macro data skill matches the market (us-macro, bursa-macro, or crypto-macro). Outputs a concise macro backdrop assessment that the verdict synthesis can weigh.

**Blocked by:** 0004 (US macro data skill provides the first testable input).

**Status:** ready-for-agent

- [ ] `analysis/macro-context/SKILL.md` exists with sections: Purpose, Input (reads scratch from the relevant market's macro data skill), Output Format, Analysis Framework, Error Handling, Dependencies
- [ ] Skill documents market-specific logic: for US, weigh Fed stance + yield curve + liquidity; for Bursa, weigh BNM OPR + MYR + commodity cycle; for crypto, weigh Fed liquidity + DXY + stablecoin supply
- [ ] Output is: macro stance (bullish/bearish/neutral), confidence, key drivers (2-3 bullet points), headwinds, tailwinds
- [ ] Dependencies lists all three macro data skills as conditional (market-dependent)
