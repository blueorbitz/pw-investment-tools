# 0001: Investment Skills Network

## Problem statement

Researching stocks and crypto tokens across three markets (Bursa Malaysia, US, Crypto) requires pulling data from scattered sources, running multiple analysis frameworks, and synthesizing a verdict. The process is slow, inconsistent, and easy to half-finish. Portfolio monitoring and watchlist tracking happen sporadically because there's no structured workflow to trigger them.

## Solution

A library of composable Kiro skills organized by concern (data fetching, analysis, orchestration, utility, monitoring) that an agent invokes on demand. Two orchestrator skills tie data and analysis together into polished reports: a quick-look for fast filtering and a deep-research for full due diligence. A monitoring layer handles scheduled portfolio reviews, watchlist scans, and custom alerts. All output lands in a date-based `~/notes/` directory for traceability.

## User stories

1. As an investor, I want to run a quick-look on a ticker so I can decide in two minutes whether it's worth deeper research.
2. As an investor, I want to run deep-research on a ticker so I get a complete report covering fundamentals, technicals, sentiment, macro context, and a final verdict.
3. As an investor, I want the system to determine the correct market (Bursa/US/Crypto) from my ticker so I don't have to specify it manually every time.
4. As an investor, I want data skills to fetch structured API data first and fall back to web search only when needed, so I save tokens and get reliable numbers.
5. As an investor, I want each report to open with a clear Buy/Sell/Hold verdict, conviction level, target price, timeframe, and stop loss so I can scan the decision without reading the full report.
6. As an investor, I want position sizing guidance (allocation % range) based on conviction and volatility included in every verdict.
7. As an investor, I want Bursa-specific fundamentals (PE, PB, DY, ROE, revenue growth, cash/debt, shareholding changes) fetched and normalized for analysis.
8. As an investor, I want US-specific fundamentals (PE, PEG, FCF yield, margins, EPS revisions, buybacks) fetched and normalized for analysis.
9. As an investor, I want crypto-specific fundamentals (market cap, FDV, supply schedule, TVL, protocol revenue, token unlocks) fetched and normalized for analysis.
10. As an investor, I want on-chain data (exchange flows, whale wallets, active addresses, staking ratios) available as a unique analysis dimension for crypto.
11. As an investor, I want crypto derivatives data (funding rates, open interest, liquidation levels) factored into technical analysis.
12. As an investor, I want market-appropriate macro indicators synthesized into a bullish/bearish/neutral backdrop per market.
13. As an investor, I want technical analysis tailored per market: volume-confirmed weekly charts for Bursa, RS vs SPY for US, 24/7 with funding rates for crypto.
14. As an investor, I want sentiment analysis that draws on market-specific sources: Bursa announcements for MY, SEC filings for US, governance forums and social buzz for crypto.
15. As an investor, I want incremental scratch notes preserved per sub-skill so I can trace how the agent reached its conclusion.
16. As an investor, I want final reports saved to `~/notes/YYYY-MM/YYYY-MM-DD-<TICKER>-<type>.md` so I can find past research by date.
17. As an investor, I want a weekly portfolio review that checks each holding's P&L, compares current state against thesis/targets/stops, and flags action items.
18. As an investor, I want a weekly watchlist scan that checks tracked tickers for entry conditions or material changes.
19. As an investor, I want custom alert conditions per position that fire when breached.
20. As an investor, I want my portfolio state stored in `~/notes/portfolio/holdings.yaml` (ticker, market, entry, shares, target, stop, thesis) so it's git-trackable and machine-parseable.
21. As an investor, I want multi-account support in holdings.yaml so positions across different brokers stay organized.
22. As an investor, I want the orchestrator to continue with partial data and note gaps in the report when an API fails, rather than aborting entirely.
23. As an investor, I want a web-search utility skill that analysis skills call when structured data raises follow-up questions.
24. As an investor, I want monitoring triggered by external cron calling a helper script, not embedded scheduling logic, so I control frequency.

## Implementation decisions

### Architecture

- All skill source lives under `src/`. Skills follow a `src/<category>/<skill-name>/SKILL.md` directory layout. Categories: `data/`, `analysis/`, `orchestrator/`, `utility/`, `monitor/`.
- The `ISK_ROOT` environment variable points to the `src/` directory. All scripts resolve cross-skill imports via `ISK_ROOT` (falls back to `__file__`-relative path if unset). This makes the workspace portable regardless of where it's cloned.
- Market prefix in skill name prevents conflicts: `bursa-fundamentals`, `us-fundamentals`, `crypto-fundamentals`.
- Data skills fetch and normalize. They never interpret. Analysis skills receive data and produce judgments. This separation lets data sources be swapped without rewriting analysis logic.
- One orchestrator per research depth (quick-look, deep-research). Each branches internally by market type via a decision tree rather than separate per-market orchestrators.
- Verdict synthesis is a single shared skill with market-aware weighting (crypto weights on-chain more, Bursa weights dividend yield more). The verdict structure (action, conviction, thesis) is universal.

### Orchestration

- Orchestrators reference sub-skills by category path. The orchestrator's SKILL.md lists dependencies; the agent reads those files to know how to invoke them.
- Sequencing: data skills run first (parallel where possible), analysis skills second (parallel where independent), verdict synthesis last.
- The agent decides which sub-skills to invoke based on a decision tree keyed on market type encoded in the orchestrator's SKILL.md.

### Inter-skill communication

- Sub-skills write structured markdown to `~/notes/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/`, one file per sub-skill.
- The orchestrator reads scratch to synthesize. Scratch is preserved alongside the final report.

### Data sourcing

- Structured APIs first: Yahoo Finance/FMP for US, CoinGecko/DeFiLlama for crypto.
- Bursa is the hardest market. No single great free API. Start with Yahoo Finance (.KL suffix) and KLSE Screener (unofficial). May need web scraping. Addressed last in implementation order.
- Crypto on-chain from Glassnode/CryptoQuant. Derivatives from Binance API.
- Web search is a standalone utility skill called by analysis skills when structured data raises questions.

### Scripts

- Hybrid approach per decision L1: SKILL.md instructs the agent. Complex APIs needing specific parsing get a helper script in `scripts/`. Simple REST calls go through the agent's tools directly. Start script-less, add scripts only where agent tool calls produce inconsistent results.

### Output

- Final reports: `~/notes/YYYY-MM/YYYY-MM-DD-<TICKER>-<type>.md`
- Scratch: `~/notes/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/`
- Portfolio state: `~/notes/portfolio/holdings.yaml` (YAML, git-tracked, optional `account` field for multi-broker)
- Watchlist: `~/notes/watchlist/watchlist.yaml`
- Report sections: Verdict, Thesis, Fundamentals, Technical Setup, Sentiment & News, Macro Context, Risks, Position Sizing.
- Verdict block: Action, Conviction, Target Price, Timeframe, Stop Loss, one-line thesis. Key-value format for scanning.

### Monitoring

- Portfolio review and watchlist scan default to weekly. Crypto can be more frequent. Frequency is configurable in the skill, not hardcoded.
- External cron/timer calls the agent with the monitor skill. Helper scripts in `src/monitor/<skill>/scripts/` serve as cron targets.

### Error handling

- Each SKILL.md has an `## Error Handling` section.
- Data skills: if API fails, try fallback or report "unavailable".
- Orchestrators continue with partial data and note gaps in the final report.

### Environment variables

- `ISK_ROOT` - path to the `src/` directory. Scripts use this to locate shared libraries and cross-skill imports. If unset, scripts fall back to resolving relative to their own `__file__` location.
- No dedicated env-check skill. Scripts read env directly. Root README documents all required env vars with a table mapping each to the skills that need it.

### Dependency declaration

- Each SKILL.md has a `## Dependencies` section listing skills it calls by path.

## Testing decisions

- Skills are tested by invoking the agent with a known ticker and verifying the output file exists with expected sections.
- Data skills: test that the output scratch file contains the documented fields (or a clear "unavailable" note).
- Analysis skills: test that the output scratch file contains a judgment (not raw data repetition).
- Orchestrators: end-to-end test with a US ticker first (best API coverage). Verify final report has all template sections and a verdict block.
- Monitoring: test portfolio-review with a sample holdings.yaml containing at least one position with a breached stop.
- No unit test framework needed. The "test" is running the skill and inspecting output. Acceptance criteria are structural (correct files, correct sections, correct verdict format).

## Out of scope

- Multi-ticker comparison orchestrator (deferred, per L4).
- Real-time or intraday alerting. Monitoring is batch/scheduled.
- Exact share count or dollar-amount position sizing (requires knowing total portfolio value).
- Chart image generation (chart-annotator is last priority, may remain text-only descriptions).
- Built-in scheduling. Skills don't implement cron; that's external.
- Paid API integrations beyond free tiers (start with free sources, upgrade later if needed).
- Mobile or web UI. Output is markdown files.

## Further notes

- Implementation order follows a vertical-slice approach: utilities first, then a complete US slice (easiest APIs) through quick-look, then deep-research, then crypto, then Bursa (hardest), then monitoring.
- Historical data defaults: 1Y daily + 5Y weekly for equities, 6M daily for crypto. Consider computed indicators (RSI, MACD values) rather than raw candles to manage token cost.
- The workspace rebuilds skills fresh. The existing dokploy-hervest repo is reference/inspiration only.
