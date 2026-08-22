# 0008: Verdict synthesis skill

**What to build:** `analysis/verdict-synthesis/SKILL.md` that reads all analysis scratch outputs and produces the final Buy/Sell/Hold verdict. Market-aware weighting: crypto weights on-chain more, Bursa weights dividend yield more, but the output structure is universal. Includes conviction level (High/Medium/Low), target price, timeframe, stop loss, one-paragraph thesis, and position sizing guidance (allocation % range).

**Blocked by:** 0005 (US valuation), 0006 (US technical), 0007 (macro context). Needs at least valuation + technical to produce a meaningful verdict.

**Status:** ready-for-agent

- [ ] `analysis/verdict-synthesis/SKILL.md` exists with sections: Purpose, Input (reads all analysis scratch files for the ticker), Output Format, Weighting Framework, Error Handling, Dependencies
- [ ] Skill documents the verdict block format: Action (Buy/Sell/Hold), Conviction (High/Medium/Low), Target Price, Timeframe, Stop Loss, Thesis (one paragraph)
- [ ] Skill documents position sizing: suggest allocation % range (e.g., "1-3%") based on conviction and volatility, clearly labeled as assessment not advice
- [ ] Skill documents market-specific weighting adjustments
- [ ] Skill handles partial inputs: if some analysis is missing, adjust confidence downward and note gaps
- [ ] Dependencies lists all analysis skills as conditional inputs
