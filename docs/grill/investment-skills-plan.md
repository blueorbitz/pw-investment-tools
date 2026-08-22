# Grill Session: Investment Skills Network

Date: 2026-08-22
Method: Auto-grill with principle-based delegation

> **Review priority:** Low-confidence decisions (#L1-L4 below) are where the principles were silent or in tension. These rows need human review.

## Principles

| # | Principle | Category |
|---|-----------|----------|
| 1 | Small, composable skills the model can call + defined orchestrator skills for readable workflow logic | Granularity |
| 2 | Each market (Bursa, US, Crypto) owns its skills. No overlap. Small utility skills shared across markets | Market coverage |
| 3 | Research and stock picking is manual. Portfolio review and alerts are scheduled/automatic | Automation model |
| 4 | Complete polished reports as final output. Incremental notes preserved for thought-process visibility | Output quality |
| 5 | Structured APIs first (saves tokens). Web search as fallback or for follow-up questions triggered by available data | Data sourcing |
| 6 | Agent decides what's relevant based on asset type. Fed liquidity for US/crypto, BNM/Ringgit for Bursa, etc | Orchestration intelligence |
| 7 | Rebuild fresh skills in this workspace. Existing dokploy-hervest is reference/inspiration only | Build approach |
| 8 | Final output MUST include a clear Buy/Sell/Hold verdict with conviction/confidence level | Decision authority |

## Decisions

### High confidence (principles clearly decided)

| # | Question | Answer | Driving Principle |
|---|----------|--------|-------------------|
| A1 | Directory structure | Max 2 levels: `<category>/<skill-name>/SKILL.md`. Market prefix in skill name to avoid conflicts (e.g., `data/bursa-fundamentals/`, `data/us-fundamentals/`). Categories: `data/`, `analysis/`, `orchestrator/`, `utility/`, `monitor/` | #1 + #2, AGENTS.md |
| A2 | Boundary: data skill vs analysis skill | Data skill fetches and normalizes. Never interprets. Analysis skill receives data and produces judgments. Clean separation lets you swap data sources without rewriting analysis | #1, #5 |
| A3 | How orchestrators reference sub-skills | By category path name. Orchestrator SKILL.md lists dependencies. Agent reads those SKILL.md files to know invocation | #1, AGENTS.md |
| A4 | Shared output handler | Yes. `utility/report-writer/SKILL.md` handles: path selection, template application, writing both final report and incremental notes | #4 |
| A5 | Inter-skill communication | Structured markdown to `~/notes/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/`. Each sub-skill writes there. Orchestrator reads to synthesize. Scratch preserved alongside report | #4, #1 |
| B1 | Fundamental metrics per market | Bursa: PE, PB, DY, ROE, revenue growth, cash/debt, shareholder changes. US: PE, PEG, FCF yield, margins, EPS revisions, buybacks. Crypto: market cap, FDV, supply schedule, TVL, protocol revenue, token unlocks | #2, #6 |
| B2 | TA differences per market | Bursa: volume confirmation critical (low liquidity), weekly chart focus. US: standard TA + RS vs SPY + options flow. Crypto: 24/7, funding rates, liquidation heatmaps, BTC dominance | #2, #6 |
| B3 | Macro indicators per market | Bursa: BNM OPR, MYR strength, palm oil, ASEAN flows. US: Fed rate, CPI/PCE, yields, Fed balance sheet. Crypto: Fed liquidity, DXY, stablecoin supply, BTC ETF flows | #6 |
| B4 | News/catalyst sources per market | Bursa: Bursa announcements, The Edge, i3investor. US: SEC filings, earnings transcripts. Crypto: on-chain alerts, governance forums, CT, CoinDesk | #2, #5 |
| B5 | Crypto needs on-chain as unique dimension | Yes. Whale wallets, exchange flows, active addresses, staking ratios. No equivalent in equities. Gets its own data skill | #2, #1 |
| C1 | Trigger interface | User invokes orchestrator skill with ticker/token. Agent determines market from the ticker or user specifies it | #3 |
| C2 | Agent decides which sub-skills | Orchestrator SKILL.md contains a decision tree keyed on market type. If crypto, include on-chain. If Bursa, skip Fed liquidity. Logic is explicit in the skill file | #6 |
| C3 | Sequencing | Data skills first (parallel). Analysis skills second (parallel where independent). Verdict synthesis last | #1 |
| C4 | Verdict synthesis | Dedicated `analysis/shared/verdict-synthesis/SKILL.md` takes all analysis outputs, weighs them, produces Buy/Sell/Hold + conviction (High/Medium/Low) + one-paragraph thesis | #8, #4 |
| C5 | Quick-look vs deep-research | Yes, two orchestrators. Quick-look: fundamentals + technical + verdict (~2 min). Deep-research: all sub-skills, full report (~5-10 min) | #1 |
| D1 | Notes directory structure | Date-first: `~/notes/YYYY-MM/YYYY-MM-DD-<TICKER>-<type>.md`. Also `~/notes/portfolio/` and `~/notes/watchlist/` for monitoring | #4 |
| D2 | Incremental vs final storage | Final: `~/notes/YYYY-MM/YYYY-MM-DD-<TICKER>-<type>.md`. Scratch: `~/notes/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/` with one file per sub-skill | #4 |
| D3 | Report template | Sections: Verdict, Thesis, Fundamentals, Technical Setup, Sentiment & News, Macro Context, Risks, Position Sizing | #8, #4 |
| D4 | Verdict section format | Top of report. Action (Buy/Sell/Hold), Conviction (High/Medium/Low), Target Price, Timeframe, Stop Loss, one-line thesis. Key-value block for easy scanning | #8 |
| D5 | Central research index | No. Not needed. Git history and date-based folder structure provide sufficient traceability | #4 |
| E1 | Portfolio review skill | Reads holdings.yaml, fetches current prices and metrics, compares vs thesis/targets/stops, flags breaches, writes summary with action items | #3 |
| E2 | Alert mechanism | Portfolio state includes per-position: entry, target, stop, custom conditions. Monitor checks on schedule, writes alert output | #3 |
| E3 | Portfolio state storage | `~/notes/portfolio/holdings.yaml`. Contains: ticker, market, entry date, entry price, shares, target, stop, thesis summary. YAML for structured parsing, git-tracked | #4 |
| E4 | Watchlist vs portfolio distinction | Watchlist = interested but don't own. Lighter checks (price movement, catalyst dates, entry conditions). Portfolio = active positions with P&L, thesis validation, exit discipline | #1 |
| E5 | Monitoring frequency | Default: weekly for portfolio review, weekly for watchlist scan. Crypto can be more frequent if needed. Configurable in skill, not hardcoded. Bias toward less frequent to save tokens | #3 |
| F1 | Web search integration | Standalone utility: `utility/web-search/SKILL.md`. Analysis skills call it when structured data raises questions. Not embedded in every skill | #5 |
| F2 | Env var management | No dedicated env-check skill. Scripts read from env directly. Document all required env vars in the root README with a table mapping env var to which skills need it | #5 |
| F3 | Error handling | Each SKILL.md has `## Error Handling`. Data skills: if API fails, try fallback or report "unavailable". Orchestrator continues with partial data, notes gaps in report | #1 |
| F4 | Versioning | No formal scheme. Git history is enough. Skills evolve in place | #7 |
| F5 | Dependency graph declaration | Each SKILL.md has `## Dependencies` listing skills it calls by path. Serves as both runtime reference and documentation | #1 |
| G1 | Crypto data sources | CoinGecko (prices, supply), DeFiLlama (TVL, revenue), Glassnode/CryptoQuant (on-chain), Binance (funding rates, OI), CoinMarketCal (events) | #5 |
| G2 | Crypto fundamental analysis | No PE. Instead: tokenomics, supply schedule, inflation, protocol revenue/fees, TVL trend, active users, dev activity, competitive position, team/VC quality | #2 |
| G3 | On-chain as separate skill | Yes. `data/crypto/onchain/SKILL.md`: exchange flows, whale wallets, staking ratios, active addresses. Pure data skill feeding into analysis | #1, #2 |
| G4 | Crypto TA differences | 24/7 (no gaps), wider stops. Unique inputs: funding rates, liquidation heatmaps, BTC correlation coefficient, market dominance %. Encoded in `analysis/crypto/technical/SKILL.md` | #2 |

### Medium confidence (principles align but don't directly address)

| # | Question | Answer | Driving Principle | Reasoning |
|---|----------|--------|-------------------|-----------|
| M1 | One orchestrator per research type (branches by market) vs per-market orchestrators | One orchestrator with internal market branching. `orchestrator/deep-research/SKILL.md` handles all markets via decision tree | #1 + #6 | Per-market orchestrators would mean 6 files (3 markets x 2 depths). Unified with branching is cleaner. Can split later if complexity grows |
| M2 | Verdict synthesis: shared or per-market | One shared skill with market-aware weighting. Crypto weights on-chain more, Bursa weights dividend yield more. Same verdict structure everywhere | #2 + #8 | The framework (conviction levels, action types) is universal. Only weights differ. One file with conditional logic stays DRY |
| M3 | Position sizing detail level | Suggest allocation % range (e.g., "1-3% position") based on conviction and volatility. Not exact share counts (requires knowing portfolio size) | #8 | Useful guidance without being prescriptive. Clearly labeled as assessment, not advice |
| M4 | Multi-account support in holdings.yaml | Yes, optional `account` field per position. Defaults to a single unnamed account. Multi-market implies multiple brokers | #2 | Multi-market inherently means multiple brokers. Schema should support this from the start |
| M5 | How is the scheduled monitor triggered | External cron/timer calls the agent with the monitor skill. The skill itself doesn't implement scheduling. A helper script in `monitor/<skill>/scripts/` can be the cron target | #3 | Kiro skills don't have built-in cron. The scheduling mechanism is external to the skill definition |

### Low confidence (needs human review)

| # | Question | Answer | Reasoning | Tension |
|---|----------|--------|-----------|---------|
| L1 | Should skills include API-calling scripts or just instruct the agent to use tools? | Hybrid. SKILL.md instructs the agent. For complex APIs needing specific parsing, include a script in `scripts/`. For simple REST, agent uses tools directly | Scripts add maintenance burden. But complex APIs (Bursa financials parsing, CoinGecko pagination) benefit from dedicated parsers | Maintenance cost vs parsing reliability. Suggest: start script-less, add scripts only where agent tool calls produce inconsistent results |
| L2 | Data source for Bursa Malaysia fundamentals | No single great free API. Options: KLSE Screener (unofficial), Yahoo Finance (.KL suffix, limited), Bursa website scraping (fragile), paid services | Principle 5 says "structured APIs first" but Bursa's ecosystem is weak compared to US or crypto | May need to accept web scraping or unofficial APIs as primary for Bursa. This is the hardest market to automate |
| L3 | How much historical data for TA | Default: 1Y daily + 5Y weekly for equities, 6M daily for crypto. Configurable per skill | More data = better context but higher token cost if agent processes raw numbers. Might need chart-image generation scripts to avoid drowning in data | Token efficiency vs analysis quality. Consider computed indicators (RSI, MACD values) rather than raw candles |
| L4 | Should there be a "comparison" skill for multiple tickers | Defer to later. Initial focus is single-ticker research. A comparison orchestrator would call N single-ticker analyses then compare. Add to roadmap | Multiplies complexity. Each comparison = N full runs | Scope vs usefulness. Park as future work, don't build day one |

## Design tree (resolved)

```
investment-skills/
├── data/
│   ├── bursa-fundamentals/      Fetch MY financials (PE, PB, DY, ROE, debt)
│   ├── bursa-price-history/     OHLCV for Bursa stocks
│   ├── bursa-announcements/     Corporate actions, Bursa filings
│   ├── bursa-macro/             BNM OPR, MYR, commodities, ASEAN flows
│   ├── us-fundamentals/         FCF, margins, EPS revisions, buybacks
│   ├── us-price-history/        OHLCV for US stocks
│   ├── us-filings/              SEC 10-K, 10-Q, 8-K, Form 4
│   ├── us-macro/                Fed rate, CPI, yields, balance sheet
│   ├── crypto-fundamentals/     Market cap, FDV, TVL, tokenomics, revenue
│   ├── crypto-price-history/    OHLCV candles
│   ├── crypto-onchain/          Exchange flows, whale wallets, staking
│   ├── crypto-derivatives/      Funding rates, OI, liquidation levels
│   └── crypto-macro/            DXY, stablecoin supply, ETF flows
├── analysis/
│   ├── bursa-valuation/         Fair value, peer comparison, quality score
│   ├── bursa-technical/         Trend, S/R, volume, entry/exit zones
│   ├── bursa-sentiment/         News tone, insider activity, flow
│   ├── us-valuation/            DCF context, multiples, growth-adjusted
│   ├── us-technical/            RS vs SPY, levels, options flow context
│   ├── us-sentiment/            Analyst revisions, news, options activity
│   ├── crypto-valuation/        Tokenomics, TVL trend, competitive position
│   ├── crypto-technical/        24/7 TA, funding, liquidations, BTC corr
│   ├── crypto-onchain-analysis/ Accumulation/distribution, whale behavior
│   ├── crypto-sentiment/        Social buzz, governance, dev activity
│   ├── macro-context/           Synthesize macro into market opinion
│   └── verdict-synthesis/       Final Buy/Sell/Hold + conviction level
├── orchestrator/
│   ├── deep-research/           Full pipeline, all skills, polished report
│   └── quick-look/              Fast filter: fundamentals + TA + verdict
├── utility/
│   ├── report-writer/           Format, save to ~/notes
│   ├── web-search/              Supplementary search when APIs fall short
│   └── chart-annotator/         Generate chart descriptions with levels
└── monitor/
    ├── portfolio-review/        Weekly check on holdings, P&L, thesis
    ├── watchlist-scan/          Weekly check on tracked tickers
    └── alert-checker/           Custom condition alerts per position
```

## Proposed skill list

| # | Skill Name | Path | Type | Description | Dependencies | Markets |
|---|-----------|------|------|-------------|--------------|---------|
| 1 | bursa-fundamentals | data/bursa-fundamentals | data | Fetch Bursa financials: PE, PB, DY, ROE, revenue growth, net cash/debt, shareholdings | none | bursa |
| 2 | bursa-price-history | data/bursa-price-history | data | Fetch OHLCV data for Bursa stocks (daily + weekly) | none | bursa |
| 3 | bursa-announcements | data/bursa-announcements | data | Fetch recent Bursa announcements and corporate actions | none | bursa |
| 4 | bursa-macro | data/bursa-macro | data | Fetch MY macro: OPR, USD/MYR, palm oil, commodity indices, ASEAN fund flows | none | bursa |
| 5 | us-fundamentals | data/us-fundamentals | data | Fetch US financials: PE, PEG, FCF yield, margins, EPS revisions, institutional ownership | none | us |
| 6 | us-price-history | data/us-price-history | data | Fetch OHLCV data for US stocks (daily + weekly) | none | us |
| 7 | us-filings | data/us-filings | data | Fetch SEC filings: insider Form 4, 13F, 10-K/10-Q summaries | none | us |
| 8 | us-macro | data/us-macro | data | Fetch US macro: Fed rate, CPI, PCE, yields, ISM, Fed balance sheet, RRP, TGA | none | us |
| 9 | crypto-fundamentals | data/crypto-fundamentals | data | Fetch token data: market cap, FDV, supply schedule, TVL, protocol revenue, unlocks | none | crypto |
| 10 | crypto-price-history | data/crypto-price-history | data | Fetch OHLCV candle data for crypto tokens | none | crypto |
| 11 | crypto-onchain | data/crypto-onchain | data | Fetch on-chain: exchange inflows/outflows, whale wallets, active addresses, staking ratios | none | crypto |
| 12 | crypto-derivatives | data/crypto-derivatives | data | Fetch perp data: funding rates, open interest, liquidation levels | none | crypto |
| 13 | crypto-macro | data/crypto-macro | data | Fetch crypto-macro: DXY, stablecoin total supply, BTC ETF flows, Fed liquidity proxy | none | crypto |
| 14 | bursa-valuation | analysis/bursa-valuation | analysis | Interpret Bursa fundamentals: fair value, peer comparison, quality scoring, moat assessment | data/bursa-fundamentals | bursa |
| 15 | bursa-technical | analysis/bursa-technical | analysis | Bursa TA: stage, trend, S/R levels, volume analysis, entry/exit zones | data/bursa-price-history | bursa |
| 16 | bursa-sentiment | analysis/bursa-sentiment | analysis | Bursa sentiment: news tone, insider activity, institutional/retail flow, buzz | data/bursa-announcements, utility/web-search | bursa |
| 17 | us-valuation | analysis/us-valuation | analysis | US valuation: DCF framing, sector multiples, growth-adjusted metrics, peer rank | data/us-fundamentals | us |
| 18 | us-technical | analysis/us-technical | analysis | US TA: RS vs SPY, stage, key levels, entry/exit zones, MA structure | data/us-price-history | us |
| 19 | us-sentiment | analysis/us-sentiment | analysis | US sentiment: EPS revision trend, analyst consensus, options unusual activity, news | data/us-filings, utility/web-search | us |
| 20 | crypto-valuation | analysis/crypto-valuation | analysis | Crypto valuation: tokenomics assessment, TVL trend, revenue quality, competitive rank | data/crypto-fundamentals | crypto |
| 21 | crypto-technical | analysis/crypto-technical | analysis | Crypto TA: 24/7 levels, funding rate context, BTC correlation, liquidation zones | data/crypto-price-history, data/crypto-derivatives | crypto |
| 22 | crypto-onchain-analysis | analysis/crypto-onchain-analysis | analysis | Interpret on-chain: accumulation/distribution signals, whale behavior, network health | data/crypto-onchain | crypto |
| 23 | crypto-sentiment | analysis/crypto-sentiment | analysis | Crypto sentiment: social buzz, governance proposals, dev activity, narrative momentum | utility/web-search | crypto |
| 24 | macro-context | analysis/macro-context | analysis | Synthesize macro backdrop into bullish/bearish/neutral opinion for the target market | data/bursa-macro OR data/us-macro OR data/crypto-macro | all |
| 25 | verdict-synthesis | analysis/verdict-synthesis | analysis | Combine all analysis into Buy/Sell/Hold + Conviction (High/Med/Low) + thesis + sizing | all relevant analysis skills | all |
| 26 | deep-research | orchestrator/deep-research | orchestrator | Full research pipeline: all data + analysis skills for the market, produces complete report | all data + analysis for market, utility/report-writer | all |
| 27 | quick-look | orchestrator/quick-look | orchestrator | Fast filter: fundamentals + technical + verdict. ~2 min. "Is this worth spending time on?" | market fundamentals + technical + verdict-synthesis, utility/report-writer | all |
| 28 | report-writer | utility/report-writer | utility | Format final reports, write scratch notes, save to ~/notes/YYYY-MM/ | none | all |
| 29 | web-search | utility/web-search | utility | Web search for supplementary info when structured APIs are insufficient | none | all |
| 30 | chart-annotator | utility/chart-annotator | utility | Generate or describe annotated price charts with marked entry/exit levels | none | all |
| 31 | portfolio-review | monitor/portfolio-review | monitor | Weekly review: check all holdings P&L, thesis status, stop/target breaches, action items | utility/web-search | all |
| 32 | watchlist-scan | monitor/watchlist-scan | monitor | Weekly scan: check watchlist tickers for entry conditions or material changes | utility/web-search | all |
| 33 | alert-checker | monitor/alert-checker | monitor | Check custom alert conditions per position, write alerts when triggered | none | all |

## Output structure (~/notes)

```
~/notes/
├── portfolio/
│   ├── holdings.yaml                 Active positions (ticker, market, entry, target, stop, thesis)
│   ├── alerts/YYYY-MM/              Alert outputs
│   └── reviews/YYYY-MM/            Weekly review outputs
├── watchlist/
│   ├── watchlist.yaml               Tracked tickers with entry conditions
│   └── scans/YYYY-MM/             Scan outputs
├── YYYY-MM/
│   ├── YYYY-MM-DD-<TICKER>-deep-research.md   Final polished report
│   ├── YYYY-MM-DD-<TICKER>-quick-look.md      Quick assessment
│   └── .scratch/
│       └── YYYY-MM-DD-<TICKER>/               Incremental notes (one file per sub-skill)
└── ...
```

## Implementation order (suggested)

1. Foundation: `utility/report-writer`, `utility/web-search`
2. First vertical slice (US, easiest APIs): `data/us-fundamentals`, `data/us-price-history`, `data/us-macro`, `analysis/us-valuation`, `analysis/us-technical`, `analysis/macro-context`, `analysis/verdict-synthesis`
3. First orchestrator: `orchestrator/quick-look` (ties the US slice together end-to-end)
4. Complete US: `data/us-filings`, `analysis/us-sentiment`, `orchestrator/deep-research`
5. Crypto (second easiest, CoinGecko/DeFiLlama are generous free tiers): all crypto data + analysis skills
6. Bursa (hardest, data source issues per L2): all bursa data + analysis skills
7. Monitoring layer (needs portfolio state): `monitor/portfolio-review`, `monitor/watchlist-scan`, `monitor/alert-checker`
8. Nice-to-have: `utility/chart-annotator`, comparison orchestrator (future)

## Dependency graph (network view)

```
orchestrator/deep-research
├── data/* (parallel fetch, market-specific selection)
├── analysis/*-valuation ← data/*-fundamentals
├── analysis/*-technical ← data/*-price-history (+ data/crypto-derivatives for crypto)
├── analysis/*-sentiment ← data/*-announcements|filings + utility/web-search
├── analysis/crypto-onchain-analysis ← data/crypto-onchain (crypto only)
├── analysis/macro-context ← data/*-macro
├── analysis/verdict-synthesis ← all analysis outputs
└── utility/report-writer ← verdict-synthesis output

orchestrator/quick-look
├── data/*-fundamentals
├── data/*-price-history
├── analysis/*-valuation ← data/*-fundamentals
├── analysis/*-technical ← data/*-price-history
├── analysis/verdict-synthesis ← valuation + technical
└── utility/report-writer

monitor/portfolio-review
├── reads ~/notes/portfolio/holdings.yaml
├── calls data/*-price-history for each holding
└── writes to ~/notes/portfolio/reviews/

monitor/watchlist-scan
├── reads ~/notes/watchlist/watchlist.yaml
├── calls data/*-price-history + data/*-fundamentals (lightweight)
└── writes to ~/notes/watchlist/scans/
```
