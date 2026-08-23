# Gates: Investment Skills Network

Completion ledger. All gates passed.

## Ticket 0001: Utility foundation

| # | Gate | Status | Evidence |
|---|------|--------|----------|
| 1.1 | `utility/report-writer/SKILL.md` exists with sections: Purpose, Input, Output Format, Output Paths, Error Handling, Dependencies | done | File created with all sections |
| 1.2 | Report-writer documents verdict block format: Action, Conviction, Target Price, Timeframe, Stop Loss, one-line thesis | done | Verdict block format section in Output Format |
| 1.3 | Report-writer documents scratch note path: `~/notes/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/<skill-name>.md` | done | Output Paths section with examples |
| 1.4 | `utility/web-search/SKILL.md` exists with sections: Purpose, When to Use, Input, Output Format, Error Handling, Dependencies | done | File created with all sections |
| 1.5 | Web-search skill instructs agent to prefer structured APIs, use web search as fallback only | done | "When to use" and "Do not use" sections |

## Ticket 0002: Shared fundamentals data

| # | Gate | Status | Evidence |
|---|------|--------|----------|
| 2.1 | `data/fundamentals/SKILL.md` exists with sections: Purpose, Input, Output Format, Data Sources, Error Handling, Dependencies | done | File created with all sections |
| 2.2 | Skill documents per-market metrics: US (PE, PEG, FCF yield, margins, EPS revisions, buybacks), Bursa (PE, PB, DY, ROE, revenue growth, cash/debt, shareholdings) | done | US-specific and Bursa-specific sections |
| 2.3 | Skill references both scripts: `financials_fetch.py` and `dividend_fetch.py` | done | Scripts section with usage examples |
| 2.4 | Output writes to scratch path convention from report-writer | done | Output format section specifies path |
| 2.5 | Error handling: if API fails, try fallback; if both fail, write "unavailable" with reason | done | Error handling section with fallback chain |

## Ticket 0003: Shared price history data

| # | Gate | Status | Evidence |
|---|------|--------|----------|
| 3.1 | `data/price-history/SKILL.md` exists with sections: Purpose, Input, Output Format, Data Sources, Error Handling, Dependencies | done | File created with all sections |
| 3.2 | Skill documents all three markets via ticker format routing | done | Input section with market detection table |
| 3.3 | Skill documents computed output: 50/200 MA, RSI 14, MACD, ADX, OBV trend, Bollinger position, Weinstein stage, 52-week range, volume ratio | done | Output format section with all indicators |
| 3.4 | Skill references both scripts: `price_history.py` and `sector_rs.py` | done | Scripts section with usage |
| 3.5 | Default timeframes documented: 1Y daily equities, 6M daily crypto | done | Default timeframes table |
| 3.6 | Error handling documents fallback behavior | done | 5-point error handling section |

## Ticket 0004: US macro data

| # | Gate | Status | Evidence |
|---|------|--------|----------|
| 4.1 | `data/us-macro/SKILL.md` exists with sections: Purpose, Input, Output Format, Data Sources, Error Handling, Dependencies | done | File created with all sections |
| 4.2 | Skill documents all indicators: Fed rate, CPI, PCE, 10Y yield, 2Y yield, yield curve spread, ISM, Fed balance sheet, RRP, TGA | done | Output format with 4 category tables |
| 4.3 | Skill specifies FRED as primary source with API key env var documented | done | Data sources + FRED_API_KEY documented |
| 4.4 | Output is structured snapshot with current value + recent trend direction | done | Tables with Trend column |
| 4.5 | Error handling: partial data acceptable, note which indicators unavailable | done | Error handling section point 2-3 |

## Ticket 0005: US valuation analysis

| # | Gate | Status | Evidence |
|---|------|--------|----------|
| 5.1 | `analysis/us-valuation/SKILL.md` exists with sections: Purpose, Input, Output Format, Analysis Framework, Error Handling, Dependencies | done | File created with all sections |
| 5.2 | Skill documents framework: DCF sanity check, multiples vs sector, PEG interpretation, margin quality, earnings momentum | done | Analysis framework with 6 ordered checks |
| 5.3 | Output includes clear valuation verdict (cheap/fair/expensive) with one-paragraph reasoning | done | Valuation verdict section in output |
| 5.4 | Dependencies section lists `data/fundamentals` by path | done | Dependencies section |
| 5.5 | Skill never fetches data itself, only interprets scratch | done | "This skill interprets. It never fetches raw data itself." |

## Ticket 0006: US technical analysis

| # | Gate | Status | Evidence |
|---|------|--------|----------|
| 6.1 | `analysis/us-technical/SKILL.md` exists with sections: Purpose, Input, Output Format, Analysis Framework, Error Handling, Dependencies | done | File created with all sections |
| 6.2 | Skill documents: stage identification, RS vs SPY, S/R methodology, MA structure, volume context | done | Analysis framework with 7 ordered checks |
| 6.3 | Output includes: current stage, trend direction, key levels, suggested entry zone, stop loss zone | done | Output format sections for each |
| 6.4 | Dependencies section lists `data/price-history` by path | done | Dependencies section |

## Ticket 0007: Macro context analysis

| # | Gate | Status | Evidence |
|---|------|--------|----------|
| 7.1 | `analysis/macro-context/SKILL.md` exists with sections: Purpose, Input, Output Format, Analysis Framework, Error Handling, Dependencies | done | File created with all sections |
| 7.2 | Skill documents market-specific logic: US (Fed + yield curve + liquidity), Bursa (OPR + MYR + commodity), crypto (liquidity + DXY + stablecoin) | done | Three market-specific subsections with scoring |
| 7.3 | Output: macro stance, confidence, key drivers, headwinds, tailwinds | done | Output format template |
| 7.4 | Dependencies lists all three macro data skills as conditional | done | Dependencies section with conditional note |

## Ticket 0008: Verdict synthesis

| # | Gate | Status | Evidence |
|---|------|--------|----------|
| 8.1 | `analysis/verdict-synthesis/SKILL.md` exists with sections: Purpose, Input, Output Format, Weighting Framework, Error Handling, Dependencies | done | File created with all sections |
| 8.2 | Skill documents verdict block: Action, Conviction, Target Price, Timeframe, Stop Loss, Thesis | done | Verdict section in output format |
| 8.3 | Skill documents position sizing: allocation % range based on conviction and volatility | done | Position sizing section with table |
| 8.4 | Skill documents market-specific weighting adjustments | done | Three weighting tables (US/Bursa/Crypto) |
| 8.5 | Skill handles partial inputs: adjusts confidence downward, notes gaps | done | Handling partial inputs section with table |
| 8.6 | Dependencies lists all analysis skills as conditional inputs | done | Full dependency list |

## Ticket 0009: Quick-look orchestrator

| # | Gate | Status | Evidence |
|---|------|--------|----------|
| 9.1 | `orchestrator/quick-look/SKILL.md` exists with sections: Purpose, Input, Pipeline Steps, Decision Tree, Output, Error Handling, Dependencies | done | File created with all sections |
| 9.2 | Decision tree documents market detection logic and sub-skill selection per market | done | Decision tree section with ASCII diagram |
| 9.3 | Pipeline documents parallel vs sequential steps with clear ordering | done | Pipeline steps tables mark parallel vs sequential |
| 9.4 | Skill references report-writer for final output formatting | done | Step 5 and Dependencies |
| 9.5 | Output path: `~/notes/YYYY-MM/YYYY-MM-DD-<TICKER>-quick-look.md` | done | Output section |
| 9.6 | Error handling: continues with partial data, notes gaps | done | Error handling section |

## Ticket 0010: US filings + sentiment

| # | Gate | Status | Evidence |
|---|------|--------|----------|
| 10.1 | `data/us-filings/SKILL.md` exists with sections: Purpose, Input, Output Format, Data Sources, Error Handling, Dependencies | done | File created with all sections |
| 10.2 | US filings skill documents: Form 4 insider buys/sells, 13F changes, 10-K/10-Q summary | done | Output format with all three sections |
| 10.3 | `analysis/us-sentiment/SKILL.md` exists with sections: Purpose, Input, Output Format, Analysis Framework, Error Handling, Dependencies | done | File created with all sections |
| 10.4 | Sentiment output: overall sentiment, insider signal, institutional signal, analyst revision direction, key news | done | Output format sections |
| 10.5 | Dependencies correctly reference `data/us-filings` and `utility/web-search` | done | Dependencies section |

## Ticket 0011: Deep-research orchestrator

| # | Gate | Status | Evidence |
|---|------|--------|----------|
| 11.1 | `orchestrator/deep-research/SKILL.md` exists with sections: Purpose, Input, Full Pipeline Steps, Decision Tree, Output, Error Handling, Dependencies | done | File created with all sections |
| 11.2 | Decision tree covers all three markets with correct sub-skill selection | done | Full decision tree with US/Bursa/Crypto branches |
| 11.3 | Pipeline documents full parallel/sequential execution plan | done | Steps 2-5 with parallel/sequential labels |
| 11.4 | Output path: `~/notes/YYYY-MM/YYYY-MM-DD-<TICKER>-deep-research.md` with all report sections | done | Output section with full template |
| 11.5 | Scratch directory preserved with one file per sub-skill | done | Scratch file list in Output section |
| 11.6 | Error handling: partial data flows through, gaps noted | done | Error handling section |

## Ticket 0012: Crypto data skills

| # | Gate | Status | Evidence |
|---|------|--------|----------|
| 12.1 | `data/crypto-fundamentals/SKILL.md` exists with correct sections | done | File created |
| 12.2 | `data/crypto-onchain/SKILL.md` exists with correct sections | done | File created |
| 12.3 | `data/crypto-derivatives/SKILL.md` exists with correct sections | done | File created |
| 12.4 | `data/crypto-macro/SKILL.md` exists with correct sections | done | File created |
| 12.5 | crypto-fundamentals covers: market cap, FDV, supply breakdown, TVL, revenue, unlock schedule | done | Output format sections |
| 12.6 | crypto-onchain covers: exchange flows, whale wallets, active addresses, staking ratios | done | Output format sections |
| 12.7 | crypto-derivatives covers: funding rates, OI, liquidation levels | done | Output format sections |
| 12.8 | crypto-macro covers: DXY, stablecoin supply, ETF flows, liquidity proxy | done | Output format sections |
| 12.9 | Each documents primary source + env vars needed | done | Data sources tables in each |
| 12.10 | Note: crypto price history handled by shared `data/price-history` | done | Referenced in crypto-fundamentals Purpose |

## Ticket 0013: Crypto analysis skills

| # | Gate | Status | Evidence |
|---|------|--------|----------|
| 13.1 | `analysis/crypto-valuation/SKILL.md` exists with correct sections | done | File created |
| 13.2 | `analysis/crypto-technical/SKILL.md` exists with correct sections | done | File created |
| 13.3 | `analysis/crypto-onchain-analysis/SKILL.md` exists with correct sections | done | File created |
| 13.4 | `analysis/crypto-sentiment/SKILL.md` exists with correct sections | done | File created |
| 13.5 | crypto-valuation documents: no-PE framework, tokenomics, TVL trend, revenue quality | done | Analysis framework section |
| 13.6 | crypto-technical documents: 24/7 handling, funding rate, liquidation zones, BTC correlation | done | Framework sections |
| 13.7 | crypto-onchain-analysis documents: accumulation/distribution, whale signals, network health | done | Analysis framework section |
| 13.8 | crypto-sentiment documents: CT, governance forums, GitHub, signal weighting | done | Framework + weighting table |
| 13.9 | verdict-synthesis updated with crypto weighting | done | Crypto weighting table in verdict-synthesis |
| 13.10 | macro-context updated with crypto logic | done | Crypto market section in macro-context |

## Ticket 0014: Bursa data skills

| # | Gate | Status | Evidence |
|---|------|--------|----------|
| 14.1 | `data/bursa-announcements/SKILL.md` exists with correct sections | done | File created |
| 14.2 | Skill references existing `bursawhale_api.py` | done | Scripts section with usage |
| 14.3 | `data/bursa-macro/SKILL.md` exists with correct sections | done | File created |
| 14.4 | `data/bursa-fundamentals/SKILL.md` exists wrapping `bursa_flows.py` | done | File created, references script |
| 14.5 | Error handling is lenient: "unavailable" acceptable | done | Error handling in each skill |
| 14.6 | Required env vars documented: BURSAWHALE_CLIENT_ID, BURSAWHALE_CLIENT_SECRET | done | In bursa-announcements SKILL.md |

## Ticket 0015: Bursa analysis skills

| # | Gate | Status | Evidence |
|---|------|--------|----------|
| 15.1 | `analysis/bursa-valuation/SKILL.md` exists with correct sections | done | File created |
| 15.2 | `analysis/bursa-technical/SKILL.md` exists with correct sections | done | File created |
| 15.3 | `analysis/bursa-sentiment/SKILL.md` exists with correct sections | done | File created |
| 15.4 | bursa-valuation documents: dividend-focused framework, peer comparison, quality scoring | done | Framework sections |
| 15.5 | bursa-technical documents: weekly chart preference, volume confirmation, wider stops, low-liquidity awareness | done | Framework sections with Bursa-specific notes |
| 15.6 | bursa-sentiment documents: Bursa filings, The Edge, i3investor, insider interpretation | done | Framework + source sections |
| 15.7 | verdict-synthesis updated with Bursa weighting | done | Bursa weighting table in verdict-synthesis |
| 15.8 | macro-context updated with Bursa logic | done | Bursa market section in macro-context |

## Ticket 0016: Portfolio review monitor

| # | Gate | Status | Evidence |
|---|------|--------|----------|
| 16.1 | `monitor/portfolio-review/SKILL.md` exists with sections: Purpose, Input, Pipeline Steps, Output Format, Output Path, Error Handling, Dependencies | done | File created with all sections |
| 16.2 | holdings.yaml schema documented with multi-account, multi-market example | done | Full schema with example YAML |
| 16.3 | Skill checks: current price vs entry (P&L%), vs target (progress), vs stop (breach) | done | Pipeline steps + output format |
| 16.4 | Output flags positions needing action | done | Action items section in output |
| 16.5 | Helper script exists in `scripts/` for cron | done | scripts/run-review.ps1 |
| 16.6 | Output path: `~/notes/portfolio/reviews/YYYY-MM/YYYY-MM-DD-portfolio-review.md` | done | Output path section |

## Ticket 0017: Watchlist scan monitor

| # | Gate | Status | Evidence |
|---|------|--------|----------|
| 17.1 | `monitor/watchlist-scan/SKILL.md` exists with correct sections | done | File created |
| 17.2 | watchlist.yaml schema documented with multi-market examples | done | Full schema with US/Bursa/Crypto examples |
| 17.3 | Skill performs lighter checks: price, % change, entry condition status, catalysts | done | Pipeline steps section |
| 17.4 | Output highlights tickers where entry conditions met or catalysts imminent | done | Output format with priority sections |
| 17.5 | Helper script in `scripts/` for cron | done | scripts/run-scan.ps1 |
| 17.6 | Output path: `~/notes/watchlist/scans/YYYY-MM/YYYY-MM-DD-watchlist-scan.md` | done | Output path section |

## Ticket 0018: Alert checker monitor

| # | Gate | Status | Evidence |
|---|------|--------|----------|
| 18.1 | `monitor/alert-checker/SKILL.md` exists with correct sections | done | File created |
| 18.2 | holdings.yaml schema extended with optional `alert_conditions` field | done | Schema section with examples |
| 18.3 | Skill documents how agent interprets free-text conditions | done | Supported condition patterns table |
| 18.4 | Output writes only when alerts fire: `~/notes/portfolio/alerts/YYYY-MM/YYYY-MM-DD-alerts.md` | done | Output path + silent success section |
| 18.5 | Helper script in `scripts/` for cron | done | scripts/run-alerts.ps1 |
| 18.6 | When no conditions breached, skill writes nothing (silent success) | done | Silent success behavior section |
