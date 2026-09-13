---
name: quick-look
description: One-pass fast filter. Given a ticker, detects the market, runs three data scripts, then a single judgment pass writes the report using the shared rubric. No analysis-skill reads, no LLM-written per-skill scratch.
---

Quick-look is one orchestrator pass. The LLM's only job is the final judgment;
scripts do all data fetching and all arithmetic. No valuation, technical, or
verdict-synthesis SKILL.md is read — the shared rubric carries the scoring rules.

## Input

- `ticker` - the asset to research (e.g., MSFT, 1155.KL, BTC/USD)
- `market` (optional) - override auto-detection: `US`, `Bursa`, or `Crypto`

## Step 0: Resolve paths (mandatory first action)

Run the path resolver and use its output verbatim for every scratch and report
path in this run — never guess from the current environment or directory:

```bash
python <ISK_ROOT>/utility/shared-lib/scripts/isk_paths.py
```

It prints `isk_root`, `isk_notes` (base for scratch and reports), and
`isk_cache`. All `$ISK_NOTES/...` references below mean the resolver's
`isk_notes` value. The data scripts also echo a `paths` block in their JSON
output — cross-check against it if unsure.

## Step 1: Detect market

| Pattern | Market | Examples |
|---------|--------|----------|
| Numeric code or `.KL` suffix | Bursa | `1155`, `5180.KL`, `1155:KLSE` |
| Contains `/` or known crypto pairs | Crypto | `BTC/USD`, `ETH/USD`, `SOL/USD` |
| Standard alphabetic | US | `MSFT`, `AAPL`, `NVDA` |

If `market` is explicitly provided, use that instead of auto-detection.

## Step 2: Run the three scripts (parallel)

Run the scripts simultaneously. They print JSON to stdout and the underlying
data lands in the same-day scratch directory — script-written data files stay
for traceability. Do not write any scratch yourself.

| Market | Scripts |
|--------|---------|
| US | `price_history.py MSFT` + `financials_fetch.py MSFT` + `quote_fetch.py MSFT` |
| Bursa | `price_history.py 1155` + `financials_fetch.py 1155` + `quote_fetch.py 1155` |
| Crypto | `price_history.py BTC-USD 6mo` + `quote_fetch.py BTC-USD` |

Script locations:
- `data/price-history/scripts/price_history.py` - price, trend, stage, MAs, indicators
- `data/fundamentals/scripts/financials_fetch.py` - annual statements (US and Bursa)
- `data/fundamentals/scripts/quote_fetch.py` - PE, forward PE, PEG, market cap, FCF, shares outstanding, 52-week range

For an altcoin, benchmark RS against BTC-USD via `data/price-history/scripts/sector_rs.py` when useful. Crypto has no annual statements: valuation judgment comes from the quote and on-chain context already in hand.

Copy the script outputs into the report as evidence. Do not recompute anything by hand.

## Step 3: One judgment pass writes the report

Read `utility/shared-lib/verdict_rubric.md` — strength labels, per-market
weights, and conviction thresholds. It is the only scoring reference needed.

1. Label each factor (valuation, technical; sentiment and macro only if data
   is already in hand — quick-look does not fetch them) with a strength label.
2. Run `utility/shared-lib/scripts/verdict_math.py --market <market> --label <factor>=<score> ...`
   to get the composite score, conviction, and applied weights. Never do the
   arithmetic yourself.
3. Write the report using `utility/report-writer` conventions.

## Report template

Write to: `$ISK_NOTES/YYYY-MM/YYYY-MM-DD-<DISPLAY_TICKER>-quick-look.md`

Use the ticker's **display ticker** in the title and filename — for Bursa
tickers that is the numeric code plus `.KL` and short company name (e.g.
`1155.KL-MAYBANK`); for others it is the normalized symbol. The data scripts
emit `display_ticker` in their JSON output.

```markdown
# <DISPLAY_TICKER> - Quick Look

Date: YYYY-MM-DD
Market: US | Bursa | Crypto

## Verdict

Action: Buy | Sell | Hold
Conviction: High | Medium | Low
Current Price: $XXX.XX
Target Price: $XXX.XX
Timeframe: X months
Stop Loss: $XXX.XX
Thesis: <one sentence>

## Thesis

<one paragraph>

## Factor summary

| Factor | Signal | Strength | Weight |
|--------|--------|----------|--------|
| Valuation | cheap / fair / expensive | <label words> | XX% |
| Technical | bullish / bearish / neutral | <label words> | XX% |

Composite: <score and label from verdict_math.py, e.g. "+0.8, mild bullish">
Conviction: <from verdict_math.py, with the deciding rule named>

## Fundamentals

<key multiples and growth from financials_fetch + quote_fetch output>

## Technical setup

<stage, trend, key levels, entry/stop zones from price_history output>

## Gaps

<what was not assessed in quick-look that deep-research would cover>
```

## Error handling

- If one script fails, continue with the other two. Note the gap.
- If both price and fundamentals scripts fail, abort: "Could not fetch any data for <TICKER>."
- If `quote_fetch.py` fails, note that multiples are unavailable — do not web-browse for them. Verdict proceeds on the remaining factors; verdict_math handles the missing weight.
- If ticker format is ambiguous, ask the user to specify market rather than guessing.
- Note all gaps in the "Gaps" section of the final report.

## Dependencies

- `data/price-history` scripts - `price_history.py`
- `data/fundamentals` scripts - `financials_fetch.py`, `quote_fetch.py`
- `utility/shared-lib` - `verdict_rubric.md` and `scripts/verdict_math.py` (shared files, not a skill)
- `utility/report-writer` - output path conventions and template
