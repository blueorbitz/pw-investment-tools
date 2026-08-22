# 0016: Portfolio review monitor

**What to build:** `monitor/portfolio-review/SKILL.md` plus the holdings.yaml schema and a helper script for cron invocation. The skill reads `~/notes/portfolio/holdings.yaml`, fetches current prices for each holding, compares against thesis/targets/stops, calculates P&L, flags breaches, and writes a weekly review summary to `~/notes/portfolio/reviews/YYYY-MM/`.

Also define the holdings.yaml schema: ticker, market, account (optional), entry_date, entry_price, shares, target, stop, thesis (one-line summary).

Include `monitor/portfolio-review/scripts/run-review.sh` (or .ps1) as the cron target.

**Blocked by:** 0001 (report-writer for output formatting).

**Status:** ready-for-agent

- [ ] `monitor/portfolio-review/SKILL.md` exists with sections: Purpose, Input (reads holdings.yaml), Pipeline Steps, Output Format, Output Path, Error Handling, Dependencies
- [ ] holdings.yaml schema documented with example showing multi-account, multi-market positions
- [ ] Skill checks each position: current price vs entry (P&L%), current vs target (progress), current vs stop (breach?)
- [ ] Output flags positions needing action: stop breaches, target reached, thesis invalidated
- [ ] Helper script exists in `scripts/` that can be called by external cron
- [ ] Output writes to `~/notes/portfolio/reviews/YYYY-MM/YYYY-MM-DD-portfolio-review.md`
