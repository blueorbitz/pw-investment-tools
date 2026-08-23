# 0018: Alert checker monitor

**What to build:** `monitor/alert-checker/SKILL.md` plus helper script. The skill reads holdings.yaml (which contains per-position custom alert conditions beyond just stop/target), evaluates each condition against current market data, and writes alert output when conditions are breached. Alert conditions are free-text in holdings.yaml (e.g., "alert if RSI > 70", "alert if DY drops below 4%") that the agent interprets and checks.

**Blocked by:** 0016 (portfolio review establishes holdings.yaml schema and proves the monitor pattern).

**Status:** done

- [x] `monitor/alert-checker/SKILL.md` exists with sections: Purpose, Input (reads holdings.yaml alert_conditions field), Pipeline Steps, Output Format, Output Path, Error Handling, Dependencies
- [x] holdings.yaml schema extended with optional `alert_conditions` field (list of free-text conditions)
- [x] Skill documents how the agent interprets and evaluates free-text conditions against current data
- [x] Output writes only when alerts fire, to `~/notes/portfolio/alerts/YYYY-MM/YYYY-MM-DD-alerts.md`
- [x] Helper script in `scripts/` for cron invocation (can run more frequently than weekly for crypto)
- [x] When no conditions are breached, skill writes nothing (silent success)
