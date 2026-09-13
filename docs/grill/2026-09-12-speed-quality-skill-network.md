# Grill session: skill network speed and quality optimization

Date: 2026-09-12
Method: Auto-grill. The user confirmed five principles up front, then the design tree was worked question by question against them. The delegated grill sub-agent stalled mid-run, so the session completed inline from the same principles and repo reads.

**Review status.** All low-confidence rows are resolved by user review. A gate FAIL now proceeds autonomously on a capped speculative track, with the gate result stated in the report; same-day scratch reuse stays; sub-agent fan-out is in, routed through the harness kanban queue when available. Position sizing is removed from verdict output at the user's request. Second review pass: `analysis/us-valuation` is removed and the buffett framework takes over US valuation, and the dead `sentiment_dashboard.py` script is slated for deletion.

## Principles

| # | Principle | Category |
|---|-----------|----------|
| 1 | Signal density over volume. Fewer, sharper inputs beat a full dump. Deep-research currently drowns in factor data and verdict quality drops with it. Cutting inputs raises quality. | Scope |
| 2 | Always-fresh data, cache only as fallback. Fetch decision-relevant data fresh every run. One trusted canonical source for quick fundamentals. Cache serves only when the live fetch fails. | Freshness |
| 3 | Every speed mechanism allowed. Scripts precompute mechanical work, stages get trimmed or merged, independent work runs in parallel. LLM tokens go to judgment, never to data shuffling or arithmetic. | Speed |
| 4 | Quality gates before deep work. Cheap checks early kill weak candidates and focus expensive research where it pays. From buffett-skills, the user's pick. | Feature |
| 5 | Trusted-source breadth, selectively fetched. More data sources, but each one fetched to serve a judgment, not dumped into context. From FinceptTerminal and finance-skills, the user's pick. | Feature |

Tiebreaker: when 4 and 5 seem to add work while 1 and 3 cut it, the gate routes the work. The gate decides which sources and factors a run actually needs, so breadth costs nothing on runs that do not need it.

## Decisions

### High confidence (principles clearly decided)

| # | Question | Answer | Driving principle |
|---|----------|--------|-------------------|
| 1 | Why is quick-look slow today? | Seven sequential LLM stages, roughly a thousand lines of SKILL.md reads across six files, agent web-browsing for valuation multiples, and LLM-written scratch at every hop. The Python scripts were never the bottleneck. | #3 |
| 2 | Should quick-look collapse into fewer passes? | Yes, into one. Detect market, run three scripts (price history, financials, new quote fetch), then a single judgment pass writes the report. No separate valuation, technical, or verdict skill reads. | #3 |
| 3 | Where should valuation multiples come from? | A new `quote_fetch.py` script hitting the Yahoo quote endpoint through `yahoo_cache`. The agent stops web-browsing for point-in-time numbers. | #3, #2 |
| 4 | Should quick-look still read the analysis SKILL.md files? | No. Extract the scoring rubric (strength labels, per-market weights, conviction thresholds) into one compact shared file that the orchestrator includes. | #3, #1 |
| 5 | Does quick-look keep per-skill scratch files? | Script-written data files stay, so traceability survives at near-zero token cost. The LLM writes only the final report. | #3 |
| 6 | Is the composite score math judgment or mechanics? | Mechanics. The LLM labels each factor, a script computes composite score, conviction, and applied weights from the labels. Removes arithmetic errors and shrinks the verdict prompt. | #3, quality win |
| 7 | Does deep-research fetch every factor by default? | No. Macro and sentiment become conditional, fetched only when the gate flags them. Crypto keeps on-chain and derivatives by default, since verdict weights already give them 25 percent. | #1 |
| 8 | Does same-day scratch reuse survive? | Yes, unchanged. Deep-research keeps reusing same-day scratch for shared factors (fundamentals, price history) and re-fetches when that scratch is partial or stale. Confirmed by the user in review. Freshness still governs the first fetch of the day and all fast-path prices. | #2, confirmed in review |
| 9 | Does deep-research get the script-first data layer too? | Yes, the same `quote_fetch.py` and shared rubric. No agent web-fetching in either pipeline. | #3 |
| 10 | Should verdicts and reports include position sizing? | No. Verdict output is Action (Buy/Sell/Hold) with conviction level, plus target, timeframe, and stop. The position-sizing section and its allocation table come out of verdict-synthesis and the deep-research report. | User-directed, review |
| 11 | What replaces `analysis/us-valuation`? | The skill is removed. The quality gate adopts the buffett dispatch model: quick screen (A) routes candidates, deep analysis (B) reads vendored buffett references 03-06 and produces the US valuation factor for verdict-synthesis. Bursa and crypto valuation stay untouched. This trades some token cost for valuation depth; the user directed it. | User-directed, review |

### Medium confidence (principles align but don't directly address)

| # | Question | Answer | Driving principle | Reasoning |
|---|----------|--------|-------------------|-----------|
| 1 | Should the quality gate be a new skill? | Yes, `analysis/quality-gate`, invoked by deep-research after the shared data fetch. | #4 | Principles say gates come before deep work but not where they live. A skill keeps deep-research lean and lets watchlist-scan reuse it. |
| 2 | Where does the gate sit in the flow? | After the cheap data fetch (fundamentals plus price history), before any factor-specific fetch. | #4 | It needs the same inputs quick-look already produces, so researching a gate-failed candidate costs about one quick-look. |
| 3 | What does the gate actually check? | Dispatch A, the cheap path: buffett's 8-question quick-screen checklist plus scripted thresholds from `05-financial-metrics` (ROE, margins, debt, FCF conversion, dividend stability, EPS trend). Dispatch B, the deep path: vendored buffett references 03-06 produce the moat, management, and intrinsic-value judgment that feeds verdict-synthesis as the valuation factor. | #4, #3 | The split follows the same scripts-compute rule, and the buffett skill's own dispatch model keeps the cheap path cheap. |
| 4 | What happens when a candidate fails the quality gate? | Proceed, capped. Deep-research continues on a speculative track with conviction capped at Medium, and the report leads with the gate verdict. Resolved in review after the pause-and-ask idea broke headless runs. | #4 | The gate surfaces the failure cheaply; proceeding keeps weak-quality names researchable while the cap stops the verdict from overselling them. |
| 5 | How should cache policy split by data type? | Prices and quotes fresh every run within market hours. Quarterly statements cached daily, since they cannot change intraday. Cache always serves as fallback when a live fetch fails. | #2 | Applying "always fresh" literally to quarterly statements buys nothing. Freshness where it moves decisions. |
| 6 | Which new sources for the breadth goal? | Each data skill declares a primary and a fallback. New sources enter as fallbacks and get promoted only on demonstrated reliability. Yahoo stays the trusted quick-fundamentals source. | #5, #2 | Specific sources deferred. Naming them now would guess rather than measure. |
| 7 | Do the monitors change? | watchlist-scan reuses `gate_checks.py` for screening and escalates only tickers that trip entry conditions. Portfolio-review and alert-checker stay as they are. | #3, #4 | Natural fit, but monitors were not the pain point. Keep the core change focused. |

### Low confidence (needs human review)

| # | Question | Answer | Reasoning | Tension |
|---|----------|--------|-----------|---------|
| 1 | Should deep-research fan factor packs out to parallel sub-agents? | Yes. One fresh context per factor pack. Route the fan-out through the harness's kanban or task queue when one exists (e.g. Hermes), because the queue retries reliably. Resolved by the user in review. | Fresh context keeps each factor judgment clean and any single context small. The kanban queue adds retry and visibility that plain parallel calls lack. | Resolved. The old tension, token cost against parallelism, is answered by the fresh-context split. |
| 2 | Should a gate FAIL hard-stop deep-research? | No, and it no longer pauses either. The user also runs deep-research without anyone at the keyboard, so the skills decide: a FAIL proceeds on a capped speculative track, conviction capped at Medium, and the report states the gate verdict up front so the failure is always visible. Resolved by the user in review, second pass. | Runs must work headless, and silent failure is worse than a capped verdict. Principle 4 holds: the gate surfaces the failure cheaply, the cap keeps it honest. | Resolved. |
| 3 | Is daily-cached fundamentals data fresh enough? | Yes. Confirmed by the user's reuse decision in review. Statements are quarterly and same-day scratch gets reused, so fresh means decision-relevant freshness: prices live, statements by the day. | Literal refetch of quarterly statements buys nothing, and the user chose reuse over refetch. | Resolved. |

## Design tree

```
Root: faster quick-look, sharper deep-research, gate-routed breadth
│
├─ Entry points
│   ├─ quick-look ............ one orchestrator pass:
│   │     detect market
│   │     run price_history.py + financials_fetch.py + quote_fetch.py (new)
│   │     one judgment pass writes the report, using the shared rubric
│   │     no analysis-skill reads, no LLM-written per-skill scratch
│   └─ deep-research ......... gate-routed pipeline:
│         shared data fetch (fundamentals + price history + quote)
│         quality gate (new skill)
│         conditional factor packs (macro, sentiment only when flagged;
│             on-chain + derivatives always for crypto)
│         factor packs fan out to parallel sub-agents, one fresh
│             context each; via the harness kanban queue when available
│         verdict via verdict_math.py
│         compressed report (existing rules unchanged)
│
├─ Data layer
│   ├─ yahoo_cache.py ........ per-endpoint TTL: prices/quotes fresh
│   │                          intraday, statements daily; fallback-only mode
│   ├─ quote_fetch.py (new) .. Yahoo quote endpoint: PE, forward PE, PEG,
│   │                          market cap, FCF, shares outstanding
│   └─ source policy ......... every data skill declares primary + fallback
│
├─ Gate layer (new, buffett-based)
│   ├─ analysis/quality-gate/SKILL.md
│   │     dispatch A: quick-screen checklist + scripted thresholds
│   │     dispatch B: vendored buffett refs 03-06 for deep valuation
│   ├─ scripts/gate_checks.py  scripted thresholds
│   ├─ references/ ............. trimmed buffett 03, 04, 05, 06
│   └─ output tiers ........... quality-pass / speculative / reject;
│                               FAIL proceeds on a capped track,
│                               conviction capped at Medium, gate
│                               result stated in the report
│
├─ Analysis layer
│   ├─ shared rubric file (new)  strength labels, per-market weights,
│   │                            conviction thresholds, extracted from
│   │                            verdict-synthesis
│   ├─ us-valuation ............. REMOVED; buffett dispatch B (quality
│   │                            gate) supplies the US valuation factor
│   ├─ verdict_math.py (new) ..... labels in, composite + conviction + weights out
│   └─ macro / sentiment ......... conditional in deep-research
│
├─ Verdict and report
│   ├─ verdict-synthesis ....... keeps thesis, target, stop judgment;
│   │                             delegates all scoring math; no
│   │                             position sizing in output
│   └─ report .................. compression rules unchanged; gate result
│                                 appears as one line
│
├─ Monitors
│   └─ watchlist-scan .......... reuses gate_checks.py for screening
│
└─ Cross-cutting
    └─ README .................. update design principles: traceability
                                clarified, gate routing and sub-agent
                                fan-out added
```

## Concrete change list

1. `src/orchestrator/quick-look/SKILL.md`: rewrite to three steps (detect, run scripts, one judgment pass). Drop the per-skill analysis reads and LLM-written scratch. Reference the shared rubric.
2. New `src/data/fundamentals/scripts/quote_fetch.py` (or shared-lib): Yahoo quote endpoint, returns PE, forward PE, PEG, market cap, FCF components, shares outstanding, 52-week range. Removes agent web-browsing from the hot path.
3. New `src/utility/shared-lib/verdict_rubric.md`: compact file with the -2..+2 strength labels, per-market baseline weights, regime multipliers, and conviction thresholds, extracted from verdict-synthesis.
4. New `src/utility/shared-lib/scripts/verdict_math.py`: takes factor labels, market, and regime; returns composite score, conviction, and applied weights with the bounded multipliers enforced.
5. `src/analysis/verdict-synthesis/SKILL.md`: keep the judgment sections (thesis, target, stop, factor labels). Delegate composite and conviction math to `verdict_math.py`. Reference the rubric instead of inlining the tables.
6. New `src/analysis/quality-gate/SKILL.md` with `scripts/gate_checks.py` and `references/`: built on the buffett dispatch model. Dispatch A is the quick-screen checklist plus scripted thresholds, outputting quality-pass, speculative, or reject. Dispatch B reads vendored, trimmed copies of buffett references 03 (moat), 04 (management), 05 (financial metrics), and 06 (valuation and capital), and produces the US valuation factor for verdict-synthesis.
7. `src/orchestrator/deep-research/SKILL.md`: insert the gate stage after the shared data fetch. Make macro and sentiment conditional on gate flags, keep crypto on-chain and derivatives unconditional. Fan the factor packs out to parallel sub-agents, one fresh context each, routed through the harness's kanban or task queue when available. On a gate FAIL, proceed on a capped speculative track: conviction capped at Medium, and the report states the gate verdict so the failure is visible. Keep the same-day scratch reuse rule and the report compression rules.
8. `src/utility/shared-lib/scripts/yahoo_cache.py`: split TTLs by endpoint type, expose a fallback-only mode per principle 2.
9. `src/data/price-history/SKILL.md`: document fresh-price semantics within market hours.
10. `README.md`: update the design principles section to record the gate routing, the sub-agent fan-out, and the clarified traceability rule. Update the skill catalogue: `us-valuation` removed, quality gate added.
11. `src/monitor/watchlist-scan/SKILL.md`: use `gate_checks.py` for cheap screening, escalate only tickers that trip entry conditions.
12. `src/analysis/verdict-synthesis/SKILL.md` and the deep-research report template: remove the position-sizing section and its allocation table. Verdicts report Action, conviction, target, timeframe, and stop only.
13. Delete `src/analysis/us-valuation/`. Deep-research's US analysis list and verdict-synthesis's dependency list drop it; the valuation factor comes from the quality gate's buffett dispatch B. `bursa-valuation` and `crypto-valuation` stay.
14. Delete `src/data/us-macro/scripts/sentiment_dashboard.py`. It is referenced nowhere and duplicates sentiment concerns.

## Repo conflicts found

- deep-research's "Reuse same-day scratch (cost discipline)" sits against principle 2's always-fresh rule. Resolved: keep the reuse rule, confirmed by the user. Freshness governs the first fetch of the day and fast-path prices, and same-day re-runs reuse scratch.
- README's "Scratch for traceability" conflicts with the quick-look single pass. Resolved: script-written data files are preserved, LLM-written per-skill scratch is dropped.
- README's "Partial data is OK" is untouched and still honored.
- README's "Market-specific weighting" is untouched; it moves into the shared rubric and `verdict_math.py`.
