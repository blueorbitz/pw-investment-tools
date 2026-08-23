# 0006: US technical analysis skill

**What to build:** `analysis/us-technical/SKILL.md` that takes the output of `data/us-price-history` and produces a technical assessment. Covers: trend stage (Weinstein or similar), relative strength vs SPY, key support/resistance levels, moving average structure, entry/exit zones with reasoning. Outputs structured analysis to scratch.

**Blocked by:** 0003 (shared price history data skill).

**Status:** done

- [x] `analysis/us-technical/SKILL.md` exists with sections: Purpose, Input (reads scratch from data/price-history), Output Format, Analysis Framework, Error Handling, Dependencies
- [x] Skill documents: stage identification, RS vs SPY interpretation, S/R level methodology, MA structure (golden/death cross, slope), volume context
- [x] Output includes: current stage, trend direction, key levels (support 1/2, resistance 1/2), suggested entry zone, stop loss zone
- [x] Dependencies section lists `data/price-history` by path
