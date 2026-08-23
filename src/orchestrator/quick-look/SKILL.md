# Quick-look orchestrator

## Purpose

Ties together the fast-filter pipeline end-to-end. Given a ticker, it determines market type, fetches core data, runs analysis, synthesizes a verdict, and produces a quick-look report. This is the "two-minute decision" tool: enough data to decide whether a ticker deserves deeper research.

Quick-look is deliberately lean. It skips sentiment, macro context, and deep valuation work in favor of speed. The output gives you a verdict, key fundamentals, and a technical picture.

## Input

- `ticker` - the asset to research (e.g., MSFT, 1155.KL, BTC/USD)
- `market` (optional) - override auto-detection: `US`, `Bursa`, or `Crypto`

## Pipeline steps

### Step 1: Market detection

Determine market from ticker format:

| Pattern | Market | Examples |
|---------|--------|----------|
| Numeric code or `.KL` suffix | Bursa | `1155`, `5180.KL`, `1155:KLSE` |
| Contains `/` or known crypto pairs | Crypto | `BTC/USD`, `ETH/USD`, `SOL/USD` |
| Standard alphabetic | US | `MSFT`, `AAPL`, `NVDA` |

If `market` is explicitly provided, use that instead of auto-detection.

### Step 2: Data fetch (parallel)

Run these data skills simultaneously:

| Market | Data skills invoked |
|--------|-------------------|
| US | `data/fundamentals` + `data/price-history` (benchmark: SPY) |
| Bursa | `data/fundamentals` + `data/price-history` (benchmark: ^KLSE) |
| Crypto | `data/fundamentals` (skip if no crypto-fundamentals yet) + `data/price-history` (benchmark: BTC-USD for alts) |

Both data skills write to scratch. Wait for both to complete before proceeding.

### Step 3: Analysis (parallel)

Run these analysis skills simultaneously:

| Market | Analysis skills invoked |
|--------|------------------------|
| US | `analysis/us-valuation` + `analysis/us-technical` |
| Bursa | `analysis/bursa-valuation` + `analysis/bursa-technical` |
| Crypto | `analysis/crypto-valuation` + `analysis/crypto-technical` |

Both read from scratch (written in step 2) and write their own scratch output.

### Step 4: Verdict synthesis (sequential)

Run `analysis/verdict-synthesis`. It reads all scratch from steps 2-3 and produces the verdict.

Note: For quick-look, macro and sentiment are not fetched. Verdict synthesis handles missing inputs by redistributing weights.

### Step 5: Report assembly (sequential)

Use `utility/report-writer` conventions to assemble the final report. Quick-look reports use a subset of the full template:

- Verdict (full verdict block)
- Thesis (one paragraph)
- Fundamentals (summary from valuation analysis)
- Technical setup (summary from technical analysis)

Write to: `~/notes/YYYY-MM/YYYY-MM-DD-<TICKER>-quick-look.md`

## Decision tree

```
Input: ticker
  │
  ├─ Detect market
  │   ├─ US ────────────────────────────────────┐
  │   ├─ Bursa ─────────────────────────────────┤
  │   └─ Crypto ────────────────────────────────┤
  │                                              │
  ├─ [Parallel] Fetch data                       │
  │   ├─ data/fundamentals(ticker)               │
  │   └─ data/price-history(ticker, benchmark)   │
  │                                              │
  ├─ [Parallel] Run analysis                     │
  │   ├─ <market>-valuation (reads scratch)      │
  │   └─ <market>-technical (reads scratch)      │
  │                                              │
  ├─ [Sequential] verdict-synthesis              │
  │                                              │
  └─ [Sequential] Write report                   │
      └─ ~/notes/YYYY-MM/YYYY-MM-DD-<TICKER>-quick-look.md
```

## Output

Final report at: `~/notes/YYYY-MM/YYYY-MM-DD-<TICKER>-quick-look.md`

```markdown
# <TICKER> - Quick Look

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

<one paragraph>

## Fundamentals

<condensed from valuation analysis: key multiples, growth, quality signal>

## Technical setup

<condensed from technical analysis: stage, trend, key levels, entry/stop zones>

## Gaps

<what was not assessed in quick-look that deep-research would cover>
```

Scratch directory preserved at: `~/notes/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/`

## Error handling

- If one data skill fails but the other succeeds, continue with partial data. The analysis and verdict skills are designed to handle partial inputs.
- If both data skills fail, abort and report: "Could not fetch any data for <TICKER>. Check ticker format and try again."
- If an analysis skill fails, proceed to verdict with whatever is available. Verdict synthesis will cap conviction at Medium or Low.
- If ticker format is ambiguous, ask the user to specify market rather than guessing.
- Note all gaps in the "Gaps" section of the final report.

## Dependencies

- `data/fundamentals` - financial data
- `data/price-history` - price and indicator data
- `analysis/us-valuation` | `analysis/bursa-valuation` | `analysis/crypto-valuation` - market-specific valuation
- `analysis/us-technical` | `analysis/bursa-technical` | `analysis/crypto-technical` - market-specific technical
- `analysis/verdict-synthesis` - final verdict
- `utility/report-writer` - output path conventions and template
