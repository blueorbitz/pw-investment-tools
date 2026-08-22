# 0005: US valuation analysis skill

**What to build:** `analysis/us-valuation/SKILL.md` that takes the output of `data/us-fundamentals` and produces a valuation judgment. Covers: DCF framing (is growth priced in?), sector multiples comparison, growth-adjusted metrics (PEG context), peer ranking, quality assessment. Outputs a structured analysis to scratch with a valuation verdict (cheap/fair/expensive) and key reasoning.

**Blocked by:** 0002 (shared fundamentals data skill).

**Status:** ready-for-agent

- [ ] `analysis/us-valuation/SKILL.md` exists with sections: Purpose, Input (reads scratch from data/fundamentals), Output Format, Analysis Framework, Error Handling, Dependencies
- [ ] Skill documents the analysis framework: DCF sanity check, multiples vs sector, PEG interpretation, margin quality, earnings momentum
- [ ] Output includes a clear valuation verdict (cheap/fair/expensive) with one-paragraph reasoning
- [ ] Dependencies section lists `data/fundamentals` by path
- [ ] Skill never fetches data itself, only interprets what's in scratch
