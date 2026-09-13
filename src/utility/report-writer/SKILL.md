---
name: report-writer
description: Handles all output file creation for the investment skills network. Selects the correct output path, applies the report template, and writes final reports and scratch notes.
---

## Base path resolution

All output paths are relative to a configurable base directory:

1. Run the path resolver:

   ```bash
   python <ISK_ROOT>/utility/shared-lib/scripts/isk_paths.py
   ```

2. Use its `isk_notes` value as the base directory for all output in this run.
3. If the resolver cannot run, fall back to reading `ISK_NOTES` from the
   environment, then `.env` in the workspace root, then `~/notes`.

Precedence rules (enforced by the resolver): `.env` in the workspace root is
the source of truth for `ISK_NOTES`, `ISK_CACHE`, and `ISK_ROOT` — it
overrides an inherited environment variable, because scheduler/harness
sessions often carry stale copies. Relative paths (e.g. `ISK_NOTES=./.notes`)
resolve against the workspace root, never the current working directory. The
Python scripts apply the identical rules via
`utility/shared-lib/scripts/yahoo_cache.py`.

Throughout all SKILL.md files, `$ISK_NOTES` refers to this resolved base path. If you set `ISK_NOTES=/home/user/Dropbox/research`, then `$ISK_NOTES/2024-03/...` becomes `/home/user/Dropbox/research/2024-03/...`.

**When running interactively:** The agent inherits env vars from your shell. Set `ISK_NOTES` in your shell profile or terminal before starting Kiro.

**When running via cron/scheduler:** The scheduler / agent harness (e.g. Hermes cron) triggers a `monitor/*` skill directly. The skill resolves paths via these conventions and writes its output. There is no wrapper script. Make sure `ISK_NOTES` is set in the harness's environment so the skill resolves the right base path.

**When no env var is set:** Everything defaults to `~/notes`. This works out of the box with no configuration.

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

Quality gate: quality-pass | speculative | reject

Action: Buy | Sell | Hold
Conviction: High | Medium | Low
Current Price: $XX.XX
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
```

Not all sections are required for every report type. Quick-look reports use: Verdict (with factor summary), Thesis, Fundamentals, Technical setup. Deep-research reports use all sections. The gate line applies only to reports that ran the quality gate; quick-look and monitor reports omit it.

### Verdict block format

The verdict block is a fixed key-value structure at the top of every report for scanning:

```
Action: Buy | Sell | Hold
Conviction: High | Medium | Low
Current Price: $XX.XX (or token-denominated for crypto)
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

All paths below use `$ISK_NOTES` as the base directory (defaults to `~/notes` if unset).

### Final reports

```
$ISK_NOTES/YYYY-MM/YYYY-MM-DD-<TICKER>-<report-type>.md
```

Examples:
- `$ISK_NOTES/2024-03/2024-03-15-MSFT-quick-look.md`
- `$ISK_NOTES/2024-03/2024-03-15-BTC-deep-research.md`
- `$ISK_NOTES/2024-03/2024-03-15-1155-deep-research.md`

Ticker in filenames: uppercase, strip exchange suffixes (.KL), replace `/` with `-`.

### Scratch notes

```
$ISK_NOTES/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/<skill-name>.md
```

Examples:
- `$ISK_NOTES/2024-03/.scratch/2024-03-15-MSFT/us-valuation.md`
- `$ISK_NOTES/2024-03/.scratch/2024-03-15-MSFT/price-history.md`
- `$ISK_NOTES/2024-03/.scratch/2024-03-15-BTC/crypto-onchain.md`

### Monitoring outputs

- Portfolio reviews: `$ISK_NOTES/portfolio/reviews/YYYY-MM/YYYY-MM-DD-portfolio-review.md`
- Watchlist scans: `$ISK_NOTES/watchlist/scans/YYYY-MM/YYYY-MM-DD-watchlist-scan.md`
- Alerts: `$ISK_NOTES/portfolio/alerts/YYYY-MM/YYYY-MM-DD-alerts.md`

## Error handling

- If the output directory does not exist, create it.
- If a file already exists at the target path, overwrite it (re-running a skill for the same ticker on the same day replaces the previous output).
- If writing fails (permissions, disk full), report the error to the calling skill. Do not silently swallow failures.
- If `ISK_NOTES` is not set in the environment, check for a `.env` file in the workspace root. If it contains `ISK_NOTES=...`, use that value. Otherwise fall back to `~/notes`.

## Dependencies

None. This is a leaf utility skill with no upstream dependencies.
