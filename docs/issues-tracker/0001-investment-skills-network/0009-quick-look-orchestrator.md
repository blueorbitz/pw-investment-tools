# 0009: Quick-look orchestrator

**What to build:** `orchestrator/quick-look/SKILL.md` that ties together the fast-filter pipeline end-to-end. Given a ticker, it: (1) determines market type, (2) fetches fundamentals + price history in parallel, (3) runs valuation + technical analysis in parallel, (4) runs verdict synthesis, (5) calls report-writer to produce a quick-look report. Contains a decision tree for market branching. This is the first end-to-end demoable slice.

**Blocked by:** 0001 (report-writer), 0005 (US valuation), 0006 (US technical), 0008 (verdict synthesis).

**Status:** done

- [x] `orchestrator/quick-look/SKILL.md` exists with sections: Purpose, Input (ticker, optional market override), Pipeline Steps, Decision Tree, Output, Error Handling, Dependencies
- [x] Decision tree documents market detection logic and which sub-skills to invoke per market
- [x] Pipeline documents parallel vs sequential steps with clear ordering
- [x] Skill references report-writer for final output formatting
- [x] Running quick-look on a US ticker produces a file at `~/notes/YYYY-MM/YYYY-MM-DD-<TICKER>-quick-look.md` with Verdict + Fundamentals + Technical sections
- [x] Error handling: continues with partial data, notes gaps
