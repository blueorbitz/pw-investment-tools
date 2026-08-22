# 0011: Deep-research orchestrator

**What to build:** `orchestrator/deep-research/SKILL.md` that runs the full research pipeline. Given a ticker: (1) determines market, (2) fetches ALL data skills for that market in parallel, (3) runs ALL analysis skills in parallel (respecting their data dependencies), (4) runs verdict synthesis, (5) calls report-writer to produce a complete polished report with all template sections. Contains the full decision tree for all three markets.

**Blocked by:** 0009 (quick-look, proves the pipeline pattern works), 0010 (US sentiment completes US coverage), 0007 (macro context).

**Status:** ready-for-agent

- [ ] `orchestrator/deep-research/SKILL.md` exists with sections: Purpose, Input (ticker, optional market override), Full Pipeline Steps, Decision Tree (all 3 markets), Output, Error Handling, Dependencies
- [ ] Decision tree covers all three markets with correct sub-skill selection per market
- [ ] Pipeline documents the full parallel/sequential execution plan
- [ ] Running deep-research on a US ticker produces `~/notes/YYYY-MM/YYYY-MM-DD-<TICKER>-deep-research.md` with all report sections: Verdict, Thesis, Fundamentals, Technical Setup, Sentiment & News, Macro Context, Risks, Position Sizing
- [ ] Scratch directory preserved with one file per sub-skill invoked
- [ ] Error handling: partial data flows through, gaps noted in report
