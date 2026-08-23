# Report writer

## Purpose

Handles all output file creation for the investment skills network. Responsible for selecting the correct output path, applying the report template, writing final reports to `~/notes/YYYY-MM/`, and writing incremental scratch notes to the `.scratch/` directory. Every skill that produces output calls this skill's conventions rather than inventing its own paths.

## Input

The calling skill provides:

- `ticker` - the asset ticker (e.g., MSFT, 1155.KL, BTC/USD)
- `report_type` - one of: `quick-look`, `deep-research`, `portfolio-review`, `watchlist-scan`, `alerts`
- `content` - the structured markdown content to write
- `skill_name` (for scratch notes only) - which sub-skill produced this intermediate output

## Output format

### Final report template

Every investment report follows this section order:

```markdown
# <TICKER> - <Report Type>

Date: YYYY-MM-DD
Market: US | Bursa | Crypto

## Verdict

Action: Buy | Sell | Hold
Conviction: High | Medium | Low
Target Price: $XX.XX
Timeframe: X months
Stop Loss: $XX.XX
Thesis: <one sentence summary>

## Thesis

<one paragraph expanding on the verdict reasoning>

## Fundamentals

<valuation and financial health assessment>

## Technical setup

<chart structure, trend, key levels>

## Sentiment and news

<market mood, insider/institutional signals, key headlines>

## Macro context

<market-level backdrop affecting this asset>

## Risks

<what could go wrong, key assumptions that could break>

## Position sizing

Suggested allocation: X-Y% of portfolio
Rationale: <based on conviction and volatility>
Note: This is an assessment framework, not financial advice.
```

Not all sections are required for every report type. Quick-look reports use: Verdict, Fundamentals, Technical setup. Deep-research reports use all sections.

### Verdict block format

The verdict block is a fixed key-value structure at the top of every report for scanning:

```
Action: Buy | Sell | Hold
Conviction: High | Medium | Low
Target Price: $XX.XX (or token-denominated for crypto)
Timeframe: X weeks | X months | X years
Stop Loss: $XX.XX
Thesis: <one sentence>
```

### Scratch note format

Scratch notes are intermediate outputs from sub-skills. They use free-form markdown but must start with a YAML-style header:

```markdown
---
ticker: MSFT
skill: us-valuation
date: 2024-03-15
status: complete | partial | unavailable
---

<structured analysis content>
```

If the skill could not produce output (API failure, insufficient data), set `status: unavailable` and include a brief reason.

## Output paths

### Final reports

```
~/notes/YYYY-MM/YYYY-MM-DD-<TICKER>-<report-type>.md
```

Examples:
- `~/notes/2024-03/2024-03-15-MSFT-quick-look.md`
- `~/notes/2024-03/2024-03-15-BTC-deep-research.md`
- `~/notes/2024-03/2024-03-15-1155-deep-research.md`

Ticker in filenames: uppercase, strip exchange suffixes (.KL), replace `/` with `-`.

### Scratch notes

```
~/notes/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/<skill-name>.md
```

Examples:
- `~/notes/2024-03/.scratch/2024-03-15-MSFT/us-valuation.md`
- `~/notes/2024-03/.scratch/2024-03-15-MSFT/price-history.md`
- `~/notes/2024-03/.scratch/2024-03-15-BTC/crypto-onchain.md`

### Monitoring outputs

- Portfolio reviews: `~/notes/portfolio/reviews/YYYY-MM/YYYY-MM-DD-portfolio-review.md`
- Watchlist scans: `~/notes/watchlist/scans/YYYY-MM/YYYY-MM-DD-watchlist-scan.md`
- Alerts: `~/notes/portfolio/alerts/YYYY-MM/YYYY-MM-DD-alerts.md`

## Error handling

- If the output directory does not exist, create it.
- If a file already exists at the target path, overwrite it (re-running a skill for the same ticker on the same day replaces the previous output).
- If writing fails (permissions, disk full), report the error to the calling skill. Do not silently swallow failures.

## Dependencies

None. This is a leaf utility skill with no upstream dependencies.
