# 0014: Bursa-specific data skills

**What to build:** Two Bursa-specific data skills. Price history and fundamentals are handled by the shared skills (tickets 0002, 0003) which already route .KL tickers correctly. This ticket covers what's unique to Bursa:

1. `data/bursa-announcements/SKILL.md` - Corporate actions, quarterly results, dividend declarations, share buybacks, insider transactions. Sources: BursaWhale API (insider data via `bursawhale_api.py`), Bursa website, i3investor. Existing script handles insider transaction fetching.
2. `data/bursa-macro/SKILL.md` - BNM OPR, USD/MYR rate, palm oil futures (FCPO), commodity indices, ASEAN fund flow data. Sources: BNM API, Yahoo Finance for MYR, TradingView scanner for market overview (existing `bursa_flows.py`), web search for commodity prices.

Also: `data/bursa-fundamentals/SKILL.md` wraps the market overview + fund flow script (`bursa_flows.py`) that fetches top Bursa stocks by market cap and directs agent to check foreign flow sources.

**Blocked by:** None (can start immediately, but logically last due to data source difficulty).

**Status:** done

- [x] `data/bursa-announcements/SKILL.md` exists with: Purpose, Input, Output Format, Data Sources (BursaWhale API + Bursa website), Error Handling, Dependencies
- [x] Skill references existing `bursawhale_api.py` for insider transaction data
- [x] `data/bursa-macro/SKILL.md` exists with: Purpose, Input, Output Format, Data Sources (BNM, Yahoo, TradingView), Error Handling, Dependencies
- [x] `data/bursa-fundamentals/SKILL.md` exists wrapping `bursa_flows.py` for market overview + fund flow guidance
- [x] Error handling is lenient: "unavailable" is acceptable given source fragility
- [x] Required env vars documented: BURSAWHALE_CLIENT_ID, BURSAWHALE_CLIENT_SECRET
