# 0010: US filings data + sentiment analysis

**What to build:** Two skills that complete the US market coverage. `data/us-filings/SKILL.md` fetches SEC filings: insider Form 4 transactions, 13F institutional holdings changes, 10-K/10-Q key highlights. `analysis/us-sentiment/SKILL.md` takes filings data plus web-search results and produces a sentiment assessment: EPS revision trend, analyst consensus direction, unusual options activity, news tone.

**Blocked by:** 0001 (web-search utility used by sentiment analysis).

**Status:** ready-for-agent

- [ ] `data/us-filings/SKILL.md` exists with sections: Purpose, Input (ticker), Output Format, Data Sources (SEC EDGAR, or equivalent), Error Handling, Dependencies
- [ ] US filings skill documents: Form 4 insider buys/sells, 13F changes, recent 10-K/10-Q summary extraction
- [ ] `analysis/us-sentiment/SKILL.md` exists with sections: Purpose, Input (reads us-filings scratch + invokes web-search), Output Format, Analysis Framework, Error Handling, Dependencies
- [ ] Sentiment output: overall sentiment (bullish/bearish/neutral), insider signal, institutional signal, analyst revision direction, key news items
- [ ] Dependencies correctly reference `data/us-filings` and `utility/web-search`
