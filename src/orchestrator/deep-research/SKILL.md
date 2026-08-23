# Deep-research orchestrator

## Purpose

Runs the full research pipeline for any ticker across all three markets. Produces a complete polished report covering fundamentals, technicals, sentiment, macro context, and a final verdict with position sizing. This is the "full due diligence" tool for when a ticker has passed the quick-look filter and deserves thorough analysis.

## Input

- `ticker` - the asset to research (e.g., MSFT, 1155.KL, BTC/USD)
- `market` (optional) - override auto-detection: `US`, `Bursa`, or `Crypto`

## Pipeline steps

### Step 1: Market detection

Same logic as quick-look:

| Pattern | Market | Examples |
|---------|--------|----------|
| Numeric code or `.KL` suffix | Bursa | `1155`, `5180.KL` |
| Contains `/` or known crypto pairs | Crypto | `BTC/USD`, `ETH/USD` |
| Standard alphabetic | US | `MSFT`, `AAPL` |

### Step 2: Data fetch (parallel)

Fetch ALL data skills for the detected market simultaneously:

| Market | Data skills invoked (all parallel) |
|--------|-----------------------------------|
| US | `data/fundamentals` + `data/price-history` (SPY) + `data/us-macro` + `data/us-filings` |
| Bursa | `data/fundamentals` + `data/price-history` (^KLSE) + `data/bursa-macro` + `data/bursa-announcements` |
| Crypto | `data/price-history` (BTC-USD for alts) + `data/crypto-fundamentals` + `data/crypto-onchain` + `data/crypto-derivatives` + `data/crypto-macro` |

All data skills write to the same scratch directory. Wait for all to complete (or timeout at 60 seconds per skill) before proceeding.

### Step 3: Analysis (parallel, respecting data dependencies)

Run ALL analysis skills for the detected market simultaneously. Each analysis skill reads the scratch it needs (written in step 2):

| Market | Analysis skills invoked (all parallel) |
|--------|---------------------------------------|
| US | `analysis/us-valuation` + `analysis/us-technical` + `analysis/us-sentiment` + `analysis/macro-context` (market=US) |
| Bursa | `analysis/bursa-valuation` + `analysis/bursa-technical` + `analysis/bursa-sentiment` + `analysis/macro-context` (market=Bursa) |
| Crypto | `analysis/crypto-valuation` + `analysis/crypto-technical` + `analysis/crypto-onchain-analysis` + `analysis/crypto-sentiment` + `analysis/macro-context` (market=Crypto) |

### Step 4: Verdict synthesis (sequential)

Run `analysis/verdict-synthesis`. Reads all analysis scratch and produces the final verdict. This must run after all analysis skills complete because it needs all their outputs.

### Step 5: Report assembly (sequential)

Use `utility/report-writer` conventions to assemble the full report with ALL template sections:

1. **Verdict** - from verdict-synthesis scratch
2. **Thesis** - expanded reasoning from verdict-synthesis
3. **Fundamentals** - from valuation analysis scratch
4. **Technical setup** - from technical analysis scratch
5. **Sentiment and news** - from sentiment analysis scratch
6. **Macro context** - from macro-context scratch
7. **Risks** - synthesized from all analysis (each skill notes risks)
8. **Position sizing** - from verdict-synthesis

Write to: `~/notes/YYYY-MM/YYYY-MM-DD-<TICKER>-deep-research.md`

## Full decision tree

```
Input: ticker
  │
  ├─ Detect market
  │
  ├─── US ─────────────────────────────────────────────────────────┐
  │     Step 2 [Parallel]:                                          │
  │       data/fundamentals(ticker)                                 │
  │       data/price-history(ticker, benchmark=SPY)                 │
  │       data/us-macro()                                           │
  │       data/us-filings(ticker)                                   │
  │     Step 3 [Parallel]:                                          │
  │       analysis/us-valuation (reads: fundamentals)               │
  │       analysis/us-technical (reads: price-history)              │
  │       analysis/us-sentiment (reads: us-filings + web-search)    │
  │       analysis/macro-context (reads: us-macro, market=US)       │
  │                                                                 │
  ├─── Bursa ──────────────────────────────────────────────────────┐
  │     Step 2 [Parallel]:                                          │
  │       data/fundamentals(ticker)                                 │
  │       data/price-history(ticker, benchmark=^KLSE)               │
  │       data/bursa-macro()                                        │
  │       data/bursa-announcements(ticker)                          │
  │     Step 3 [Parallel]:                                          │
  │       analysis/bursa-valuation (reads: fundamentals)            │
  │       analysis/bursa-technical (reads: price-history)           │
  │       analysis/bursa-sentiment (reads: bursa-announcements)     │
  │       analysis/macro-context (reads: bursa-macro, market=Bursa) │
  │                                                                 │
  ├─── Crypto ─────────────────────────────────────────────────────┐
  │     Step 2 [Parallel]:                                          │
  │       data/price-history(ticker, benchmark=BTC-USD)             │
  │       data/crypto-fundamentals(ticker)                          │
  │       data/crypto-onchain(ticker)                               │
  │       data/crypto-derivatives(ticker)                           │
  │       data/crypto-macro()                                       │
  │     Step 3 [Parallel]:                                          │
  │       analysis/crypto-valuation (reads: crypto-fundamentals)    │
  │       analysis/crypto-technical (reads: price-history, derivs)  │
  │       analysis/crypto-onchain-analysis (reads: crypto-onchain)  │
  │       analysis/crypto-sentiment (reads: web-search)             │
  │       analysis/macro-context (reads: crypto-macro, market=Crypto)│
  │                                                                 │
  ├─ Step 4 [Sequential]: analysis/verdict-synthesis                │
  │                                                                 │
  └─ Step 5 [Sequential]: Write full report                         │
      └─ ~/notes/YYYY-MM/YYYY-MM-DD-<TICKER>-deep-research.md
```

## Output

Final report at: `~/notes/YYYY-MM/YYYY-MM-DD-<TICKER>-deep-research.md`

```markdown
# <TICKER> - Deep Research

Date: YYYY-MM-DD
Market: US | Bursa | Crypto

## Verdict

Action: Buy | Sell | Hold
Conviction: High | Medium | Low
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

<from sentiment analysis>

## Macro context

<from macro-context analysis>

## Risks

- <risk 1 from valuation>
- <risk 2 from technical>
- <risk 3 from macro>
- <risk 4 from sentiment>

## Position sizing

Suggested allocation: X-Y% of portfolio
Rationale: <conviction + volatility reasoning>
Note: This is an assessment framework, not financial advice.
```

Scratch directory preserved at: `~/notes/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/`

One file per sub-skill invoked:
- `fundamentals.md`
- `price-history.md`
- `us-macro.md` (or `bursa-macro.md` or `crypto-macro.md`)
- `us-filings.md` (or `bursa-announcements.md` or `crypto-onchain.md`, etc.)
- `us-valuation.md` (or market-specific equivalent)
- `us-technical.md` (or market-specific equivalent)
- `us-sentiment.md` (or market-specific equivalent)
- `macro-context.md`
- `verdict-synthesis.md`

## Error handling

- If a data skill fails, continue with remaining skills. The analysis and verdict layers handle partial inputs.
- If all data skills for a market fail, abort with: "Could not fetch any data for <TICKER>. Check ticker and network connectivity."
- If an analysis skill fails, proceed to verdict with whatever is available. Note the gap in the report.
- The report should always note what was unavailable in a "Gaps" note at the bottom, even if all sections are populated.
- Timeout: if a data skill takes longer than 60 seconds, proceed without it and note "timed out" in scratch.

## Dependencies

### Data skills (market-conditional)

- `data/fundamentals` (US, Bursa)
- `data/price-history` (all markets)
- `data/us-macro` (US)
- `data/us-filings` (US)
- `data/bursa-macro` (Bursa)
- `data/bursa-announcements` (Bursa)
- `data/crypto-fundamentals` (Crypto)
- `data/crypto-onchain` (Crypto)
- `data/crypto-derivatives` (Crypto)
- `data/crypto-macro` (Crypto)

### Analysis skills (market-conditional)

- `analysis/us-valuation` | `analysis/bursa-valuation` | `analysis/crypto-valuation`
- `analysis/us-technical` | `analysis/bursa-technical` | `analysis/crypto-technical`
- `analysis/us-sentiment` | `analysis/bursa-sentiment` | `analysis/crypto-sentiment`
- `analysis/crypto-onchain-analysis` (Crypto only)
- `analysis/macro-context` (all markets)
- `analysis/verdict-synthesis` (all markets)

### Utility

- `utility/report-writer` - output formatting and paths
- `utility/web-search` - called by sentiment skills as needed
