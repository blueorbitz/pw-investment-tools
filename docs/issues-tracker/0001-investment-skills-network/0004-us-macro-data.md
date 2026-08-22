# 0004: US macro data skill

**What to build:** `data/us-macro/SKILL.md` that instructs the agent to fetch US macroeconomic indicators: Fed funds rate, CPI/PCE latest readings, 10Y/2Y yields and spread, ISM Manufacturing/Services, Fed balance sheet size, RRP facility balance, TGA balance. Sources: FRED API (free), Treasury.gov. Writes structured output to scratch.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] `data/us-macro/SKILL.md` exists with sections: Purpose, Input (none required, fetches current state), Output Format, Data Sources, Error Handling, Dependencies
- [ ] Skill documents all indicators: Fed rate, CPI, PCE, 10Y yield, 2Y yield, yield curve spread, ISM, Fed balance sheet, RRP, TGA
- [ ] Skill specifies FRED as primary source with API key env var documented
- [ ] Output is a structured snapshot with current value + recent trend direction for each indicator
- [ ] Error handling: partial data acceptable, note which indicators unavailable
