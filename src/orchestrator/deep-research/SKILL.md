---
name: deep-research
description: Gate-routed full research pipeline for any ticker across all three markets. Shared data fetch, quality gate, conditional factor packs fanned out to parallel sub-agents, verdict via verdict_math.py, compressed report.
---

## Input

- `ticker` - the asset to research (e.g., MSFT, 1155.KL, BTC/USD)
- `market` (optional) - override auto-detection: `US`, `Bursa`, or `Crypto`

## Pipeline steps

### Step 0: Resolve paths (mandatory first action)

Run the path resolver and use its output verbatim for every scratch and report
path in this run — never guess from the current environment or directory:

```bash
python <ISK_ROOT>/utility/shared-lib/scripts/isk_paths.py
```

It prints `isk_root`, `isk_notes` (base for scratch and reports), and
`isk_cache`. All `$ISK_NOTES/...` references below mean the resolver's
`isk_notes` value. The data scripts also echo a `paths` block in their JSON
output — cross-check against it if unsure.

### Step 1: Market detection

Same logic as quick-look:

| Pattern | Market | Examples |
|---------|--------|----------|
| Numeric code or `.KL` suffix | Bursa | `1155`, `5180.KL` |
| Contains `/` or known crypto pairs | Crypto | `BTC/USD`, `ETH/USD` |
| Standard alphabetic | US | `MSFT`, `AAPL` |

### Step 2: Shared data fetch (parallel, cheap)

Fetch the data every run needs, regardless of what the gate later decides:

| Market | Fetches (all parallel) |
|--------|------------------------|
| US | `financials_fetch.py` + `price_history.py` (benchmark SPY) + `quote_fetch.py` + `data/us-filings` |
| Bursa | `financials_fetch.py` + `price_history.py` (benchmark ^KLSE) + `quote_fetch.py` + `data/bursa-fundamentals` + `data/bursa-announcements` |
| Crypto | `price_history.py` (benchmark BTC-USD for alts) + `quote_fetch.py` + `data/crypto-fundamentals` |

Prices and quotes are fetched live every run — `yahoo_cache.py` serves its
cache only as a fallback when the live fetch fails. Statements are cached
daily; they cannot change intraday.

All fetches write to the same scratch directory. Wait for completion (or the
60-second per-skill timeout) before proceeding.

**Reuse same-day scratch (cost discipline).** If a `quick-look` (or an earlier
deep-research) already ran for this ticker today, its scratch for shared
factors (fundamentals, price-history) is present and current — the same-day
statement cache in `yahoo_cache.py` covers the underlying data. Reuse those
scratch files instead of re-fetching, and spend the run only on the factor
packs deep-research adds. Re-fetch only if the existing scratch is
`status: partial`/`unavailable` or you have reason to believe it is stale.
Prices and quotes are still fetched live regardless — freshness governs the
first fetch of the day and every fast-path price.

**On timeout or failure of a data skill:** mark that factor `unavailable`, continue,
and let verdict-synthesis redistribute weight and cap conviction. Do not retry by
default — a retry that also times out just burns cost. Name the gap in the report.

### Step 3: Quality gate (before any deep work)

Run `analysis/quality-gate` dispatch A on the shared data — the cheap screen
that decides which factor packs this run actually needs:

- **quality-pass**: full pipeline on the normal track.
- **speculative**: proceed; conviction will be capped at Medium (pass
  `--cap Medium` to verdict_math.py in step 5) and the report leads with the
  gate verdict.
- **reject**: proceed only on the capped speculative track. A gate FAIL never
  hard-stops or pauses — runs work headless. The report leads with
  "Quality gate: REJECT" and the reasons, so the failure is always visible.

For US candidates on the quality-pass or speculative track, the gate's
dispatch B reads its vendored buffett references and writes `us-valuation.md`
scratch — that file is the US valuation factor for verdict-synthesis.

Write the gate result to `quality-gate.md` in the ticker's scratch directory.

### Step 4: Conditional factor packs (parallel sub-agents)

The gate routes breadth: fetch and analyze only what this candidate needs. Run
each selected pack in a parallel sub-agent with one fresh context per pack —
fresh context keeps each factor judgment clean and any single context small.
Route the fan-out through the harness's kanban or task queue when one exists
(e.g. Hermes): the queue retries reliably and keeps every pack visible. Each
sub-agent reads only its own inputs from scratch and writes only its own
output file. A pack that returns `unavailable` is a noted gap, not retried.

| Factor pack | When |
|-------------|------|
| Technical (`<market>-technical`) | always |
| Valuation (Bursa: `bursa-valuation`; Crypto: `crypto-valuation`) | always (US: already produced by gate dispatch B) |
| Macro (`data/us-macro`/`data/bursa-macro`/`data/crypto-macro` + `analysis/macro-context`) | only when the gate flags it — macro-sensitive names, rate/FX exposure, risk-off regime |
| Sentiment (`us-sentiment`/`bursa-sentiment`/`crypto-sentiment`) | only when the gate flags it — news-driven names, insider activity, contested theses |
| On-chain + derivatives (`data/crypto-onchain` + `data/crypto-derivatives` + `analysis/crypto-onchain-analysis`) | always for crypto — verdict weights already give them 25% |

### Step 5: Verdict synthesis (sequential)

Run `analysis/verdict-synthesis`. It reads all analysis scratch, labels the
factors, and delegates the scoring math to `verdict_math.py`:

```bash
python <ISK_ROOT>/utility/shared-lib/scripts/verdict_math.py \
  --market US --label valuation=2 ... --cap Medium
```

Pass `--cap Medium` on the gate-FAIL or speculative track; omit it (default
High ceiling) on the quality-pass track.

### Step 6: Report assembly (sequential)

Deep-research **gathers selectively but reports tightly**. The factor packs are
chosen by the gate, and the final report must be balanced depth, not a data
dump. Length and noise are failures, not thoroughness. The compression rule:

- **Every factor keeps its signal.** Each fetched factor appears in the verdict's
  factor-summary table with its strength label and one-line rationale. Nothing that
  feeds the decision is dropped.
- **Prose is compressed, not the logic.** Each narrative section (Fundamentals,
  Technical, Sentiment, Macro) is a tight few-paragraph summary of its scratch, not a
  transcript. Lead with the conclusion, then the two or three facts that support it.
- **Push raw evidence down or out.** Full tables, long metric dumps, and every
  citation belong in the scratch files (already preserved) — reference them, don't
  inline them all. Include a citation only where it backs a load-bearing claim.
- **Target length.** Aim for a report a reader can absorb in a few minutes. If a
  section runs long without changing the verdict, cut it.

Use `utility/report-writer` conventions to assemble the report with these sections:

1. **Verdict** - includes the one-line gate result (quality-pass | speculative | reject)
2. **Thesis** - expanded reasoning from verdict-synthesis
3. **Fundamentals** - compressed summary from valuation scratch
4. **Technical setup** - compressed summary from technical scratch
5. **Sentiment and news** - compressed summary from sentiment scratch (when fetched)
6. **Macro context** - compressed summary from macro-context scratch (when fetched)
7. **Risks** - synthesized from all fetched packs

Write to: `$ISK_NOTES/YYYY-MM/YYYY-MM-DD-<TICKER>-deep-research.md`

## Output

Final report at: `$ISK_NOTES/YYYY-MM/YYYY-MM-DD-<TICKER>-deep-research.md`

```markdown
# <TICKER> - Deep Research

Date: YYYY-MM-DD
Market: US | Bursa | Crypto

## Verdict

Quality gate: quality-pass | speculative | reject
Action: Buy | Sell | Hold
Conviction: High | Medium | Low
Current Price: $XXX.XX
Target Price: $XXX.XX
Timeframe: X months
Stop Loss: $XXX.XX
Thesis: <one sentence>

## Thesis

<full paragraph>

## Fundamentals

<from valuation analysis>

## Technical setup

<from technical analysis>

## Sentiment and news

<from sentiment analysis, when fetched>

## Macro context

<from macro-context analysis, when fetched>

## Risks

- <risk 1 from valuation>
- <risk 2 from technical>
- <risk 3 from macro, when fetched>
- <risk 4 from sentiment, when fetched>
```

Scratch directory preserved at: `$ISK_NOTES/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/`

One file per skill or script invoked:
- `fundamentals.md`
- `price-history.md`
- `quote.md` (quote_fetch output: multiples, market cap, FCF)
- `quality-gate.md` (gate tier, scripted checks, checklist, dispatch B judgment)
- `us-valuation.md` (US: written by gate dispatch B) or market-specific valuation
- `<market>-technical.md`
- `<market>-sentiment.md` (when fetched)
- `macro-context.md` (when fetched)
- `crypto-onchain-analysis.md` (crypto only)
- `verdict-synthesis.md`

## Error handling

- If a data skill fails, continue with remaining skills. The analysis and verdict layers handle partial inputs.
- If all data skills for a market fail, abort with: "Could not fetch any data for <TICKER>. Check ticker and network connectivity."
- If the quality gate cannot run (missing scratch), treat as speculative: proceed capped at Medium and note it.
- If a factor-pack sub-agent fails or returns empty, note the gap in the report. Do not re-run the pack.
- The report should always note what was unavailable in a "Gaps" note at the bottom, even if all sections are populated.
- Timeout: if a data skill takes longer than 60 seconds, proceed without it and note "timed out" in scratch.

## Dependencies

### Data skills and scripts (market-conditional)

- `data/fundamentals` scripts - `financials_fetch.py` (US, Bursa)
- `data/price-history` scripts - `price_history.py` (all markets)
- `data/fundamentals/scripts/quote_fetch.py` - multiples, all markets
- `data/us-filings` (US)
- `data/bursa-fundamentals` (Bursa, peer context)
- `data/bursa-announcements` (Bursa)
- `data/crypto-fundamentals`, `data/crypto-onchain`, `data/crypto-derivatives` (Crypto; on-chain and derivatives unconditional)
- `data/us-macro` | `data/bursa-macro` | `data/crypto-macro` (conditional on gate flags)

### Analysis skills (market-conditional)

- `analysis/quality-gate` (gate stage; US valuation factor via dispatch B)
- `analysis/bursa-valuation` | `analysis/crypto-valuation` (their markets)
- `analysis/us-technical` | `analysis/bursa-technical` | `analysis/crypto-technical`
- `analysis/us-sentiment` | `analysis/bursa-sentiment` | `analysis/crypto-sentiment` (conditional)
- `analysis/crypto-onchain-analysis` (Crypto only)
- `analysis/macro-context` (conditional)
- `analysis/verdict-synthesis` (all markets)

### Shared files (not skills)

- `utility/shared-lib/verdict_rubric.md` - scoring rules
- `utility/shared-lib/scripts/verdict_math.py` - composite, conviction, weights
- `utility/report-writer` - output formatting and paths
- `utility/web-search` - called by sentiment packs as needed
