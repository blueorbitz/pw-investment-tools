# 0002: Shared fundamentals data skill

**What to build:** `data/fundamentals/SKILL.md` that instructs the agent to fetch financial data for any market. The script routes internally: US tickers go to Yahoo Finance timeseries API, Bursa tickers (numeric codes or .KL suffix) go to KLSE Screener. The skill specifies which metrics to fetch per market and writes structured output to scratch.

Existing scripts: `financials_fetch.py` (revenue, operating income, FCF, net income) and `dividend_fetch.py` (annual DPS history) already handle this routing.

**Blocked by:** None (can start immediately). Scripts already working.

**Status:** done

- [x] `data/fundamentals/SKILL.md` exists with sections: Purpose, Input (ticker - auto-detects market), Output Format, Data Sources (Yahoo for US, KLSE Screener for Bursa), Error Handling, Dependencies
- [x] Skill documents per-market metrics: US (PE, PEG, FCF yield, margins, EPS revisions, buybacks), Bursa (PE, PB, DY, ROE, revenue growth, cash/debt, shareholdings)
- [x] Skill references both existing scripts: `financials_fetch.py` and `dividend_fetch.py`
- [x] Output writes to scratch path convention from report-writer
- [x] Error handling: if API fails, try fallback; if both fail, write "unavailable" with reason
