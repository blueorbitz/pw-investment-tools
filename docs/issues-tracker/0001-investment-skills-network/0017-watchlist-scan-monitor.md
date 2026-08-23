# 0017: Watchlist scan monitor

**What to build:** `monitor/watchlist-scan/SKILL.md` plus the watchlist.yaml schema and helper script. The skill reads `~/notes/watchlist/watchlist.yaml`, does lightweight checks on each tracked ticker (price movement, whether entry conditions are met, material news), and writes a scan summary to `~/notes/watchlist/scans/YYYY-MM/`.

Watchlist.yaml schema: ticker, market, entry_condition (text describing when to buy), catalyst_date (optional), notes.

**Blocked by:** 0001 (report-writer for output formatting).

**Status:** done

- [x] `monitor/watchlist-scan/SKILL.md` exists with sections: Purpose, Input (reads watchlist.yaml), Pipeline Steps, Output Format, Output Path, Error Handling, Dependencies
- [x] watchlist.yaml schema documented with example entries across all three markets
- [x] Skill performs lighter checks than portfolio-review: current price, % change since added, entry condition status, upcoming catalysts
- [x] Output highlights tickers where entry conditions appear met or catalysts are imminent
- [x] Helper script in `scripts/` for cron invocation
- [x] Output writes to `~/notes/watchlist/scans/YYYY-MM/YYYY-MM-DD-watchlist-scan.md`
