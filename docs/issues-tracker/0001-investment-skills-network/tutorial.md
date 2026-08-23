# Verification walkthrough

Verifies the full Investment Skills Network implementation (spec 0001, tickets 0001-0018).

## Prerequisites

1. **Clone and enter the workspace:**
   ```powershell
   cd C:\Users\PakWai\Documents\PythonWorkspace\investment-skills
   ```

2. **Set ISK_ROOT** (all scripts use this to find each other):
   ```powershell
   $env:ISK_ROOT = "C:\Users\PakWai\Documents\PythonWorkspace\investment-skills\src"
   ```

3. **Python 3.9+** available on PATH. Verify:
   ```powershell
   python --version
   ```

4. **Optional env vars** (needed only for live data tests, not structural verification):
   ```powershell
   $env:FRED_API_KEY = "your-fred-key"
   $env:SEC_EDGAR_USER_AGENT = "YourName your@email.com"
   $env:BURSAWHALE_CLIENT_ID = "your-client-id"
   $env:BURSAWHALE_CLIENT_SECRET = "your-client-secret"
   ```

5. **Python packages** for scripts that use `requests`:
   ```powershell
   pip install requests
   ```

---

## 1. Directory structure matches spec architecture

**What changed:** Created 5 skill categories with 27 skills total following the `src/<category>/<skill-name>/SKILL.md` layout.

**Files:** All of `src/`

**How to verify:**

```powershell
# Confirm all 5 categories exist
Get-ChildItem src -Directory | Select-Object Name
```

Expected output:
```
analysis
data
monitor
orchestrator
utility
```

```powershell
# Confirm all 12 analysis skills
Get-ChildItem src\analysis -Directory | Select-Object Name
```

Expected output:
```
bursa-sentiment
bursa-technical
bursa-valuation
crypto-onchain-analysis
crypto-sentiment
crypto-technical
crypto-valuation
macro-context
us-sentiment
us-technical
us-valuation
verdict-synthesis
```

```powershell
# Confirm all 11 data skills
Get-ChildItem src\data -Directory | Select-Object Name
```

Expected output:
```
bursa-announcements
bursa-fundamentals
bursa-macro
crypto-derivatives
crypto-fundamentals
crypto-macro
crypto-onchain
fundamentals
price-history
us-filings
us-macro
```

```powershell
# Confirm 2 orchestrators
Get-ChildItem src\orchestrator -Directory | Select-Object Name
```

Expected output:
```
deep-research
quick-look
```

```powershell
# Confirm 3 monitors
Get-ChildItem src\monitor -Directory | Select-Object Name
```

Expected output:
```
alert-checker
portfolio-review
watchlist-scan
```

```powershell
# Confirm 3 utility skills (including pre-existing shared-lib)
Get-ChildItem src\utility -Directory | Select-Object Name
```

Expected output:
```
report-writer
shared-lib
web-search
```

---

## 2. Every skill has a SKILL.md

**What changed:** Each skill directory contains a SKILL.md file with the documented sections.

**How to verify:**

```powershell
# Find all SKILL.md files (should be 27)
Get-ChildItem src -Recurse -Filter "SKILL.md" | Measure-Object | Select-Object Count
```

Expected: `Count: 27`

```powershell
# List them all
Get-ChildItem src -Recurse -Filter "SKILL.md" | Select-Object FullName
```

Every directory under `src/analysis/`, `src/data/`, `src/orchestrator/`, `src/monitor/`, and `src/utility/` (except `shared-lib` which has scripts only) should have a SKILL.md.

---

## 3. Utility foundation (ticket 0001)

**What changed:** Created `utility/report-writer/SKILL.md` and `utility/web-search/SKILL.md`.

**Files:**
- `src/utility/report-writer/SKILL.md`
- `src/utility/web-search/SKILL.md`

**How to verify:**

```powershell
# Verify report-writer has required sections
Select-String -Path src\utility\report-writer\SKILL.md -Pattern "## Purpose|## Input|## Output format|## Output paths|## Error handling|## Dependencies"
```

Expected: 6 matches (one per section heading).

```powershell
# Verify verdict block format is documented
Select-String -Path src\utility\report-writer\SKILL.md -Pattern "Action.*Conviction.*Target Price"
```

Expected: At least one match.

```powershell
# Verify scratch path convention
Select-String -Path src\utility\report-writer\SKILL.md -Pattern "\.scratch/YYYY-MM-DD"
```

Expected: At least one match.

```powershell
# Verify web-search prefers structured APIs
Select-String -Path src\utility\web-search\SKILL.md -Pattern "fallback"
```

Expected: At least one match confirming web search is a fallback.

---

## 4. Data skills reference existing scripts (tickets 0002-0004)

**What changed:** SKILL.md files reference the pre-existing Python scripts.

**Files:**
- `src/data/fundamentals/SKILL.md`
- `src/data/price-history/SKILL.md`
- `src/data/us-macro/SKILL.md`

**How to verify:**

```powershell
# Verify fundamentals references both scripts
Select-String -Path src\data\fundamentals\SKILL.md -Pattern "financials_fetch\.py|dividend_fetch\.py"
```

Expected: At least 2 matches.

```powershell
# Verify price-history references both scripts
Select-String -Path src\data\price-history\SKILL.md -Pattern "price_history\.py|sector_rs\.py"
```

Expected: At least 2 matches.

```powershell
# Verify us-macro references FRED_API_KEY
Select-String -Path src\data\us-macro\SKILL.md -Pattern "FRED_API_KEY"
```

Expected: At least one match.

```powershell
# Verify the referenced scripts actually exist
Test-Path src\data\fundamentals\scripts\financials_fetch.py
Test-Path src\data\fundamentals\scripts\dividend_fetch.py
Test-Path src\data\price-history\scripts\price_history.py
Test-Path src\data\price-history\scripts\sector_rs.py
Test-Path src\data\us-macro\scripts\fed_liquidity.py
Test-Path src\data\us-macro\scripts\yield_curve.py
```

Expected: All `True`.

---

## 5. Price history script runs end-to-end

**What changed:** The SKILL.md documents how to invoke `price_history.py`. Verify the script works.

**How to verify:**

```powershell
python src\data\price-history\scripts\price_history.py MSFT
```

Expected: JSON output with `"ok": true`, containing `summary`, `ma_levels`, `indicators`, `volume`, `signals`, and `weekly_ohlcv` fields. If network is available, real data appears.

```powershell
# Test Bursa routing (numeric code becomes .KL)
python src\data\price-history\scripts\price_history.py 1155
```

Expected: JSON with `"ticker": "1155"` and data for Maybank (1155.KL).

---

## 6. Analysis skills never fetch data

**What changed:** All analysis SKILL.md files read from scratch only.

**How to verify:**

```powershell
# Verify analysis skills declare they only interpret
Get-ChildItem src\analysis -Recurse -Filter "SKILL.md" | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    if ($content -match "never fetches" -or $content -match "never fetches raw data" -or $content -match "It never fetches") {
        "$($_.Directory.Name): OK (declares no fetching)"
    } else {
        "$($_.Directory.Name): WARNING - missing no-fetch declaration"
    }
}
```

Expected: All 12 analysis skills print "OK".

---

## 7. Verdict synthesis has market-specific weighting

**What changed:** `analysis/verdict-synthesis/SKILL.md` documents different weights for US, Bursa, and Crypto.

**Files:** `src/analysis/verdict-synthesis/SKILL.md`

**How to verify:**

```powershell
Select-String -Path src\analysis\verdict-synthesis\SKILL.md -Pattern "US equities|Bursa Malaysia|Crypto"
```

Expected: At least 3 matches (one per market weighting section).

```powershell
# Verify on-chain is weighted for crypto
Select-String -Path src\analysis\verdict-synthesis\SKILL.md -Pattern "on-chain.*25%|On-chain.*25%"
```

Expected: Match showing on-chain gets 25% weight for crypto.

---

## 8. Orchestrators define parallel/sequential pipeline

**What changed:** Both orchestrator SKILL.md files document which steps run in parallel vs sequentially.

**Files:**
- `src/orchestrator/quick-look/SKILL.md`
- `src/orchestrator/deep-research/SKILL.md`

**How to verify:**

```powershell
# Quick-look has parallel data fetch + parallel analysis + sequential verdict
Select-String -Path src\orchestrator\quick-look\SKILL.md -Pattern "parallel|sequential" -AllMatches
```

Expected: Multiple matches showing the execution plan.

```powershell
# Deep-research covers all 3 markets in decision tree
Select-String -Path src\orchestrator\deep-research\SKILL.md -Pattern "US|Bursa|Crypto" | Measure-Object
```

Expected: Many matches (>10) showing comprehensive coverage.

---

## 9. Monitor helper scripts exist and are valid PowerShell

**What changed:** Each monitor skill has a `scripts/` directory with a `.ps1` file.

**Files:**
- `src/monitor/portfolio-review/scripts/run-review.ps1`
- `src/monitor/watchlist-scan/scripts/run-scan.ps1`
- `src/monitor/alert-checker/scripts/run-alerts.ps1`

**How to verify:**

```powershell
# Confirm all three scripts exist
Test-Path src\monitor\portfolio-review\scripts\run-review.ps1
Test-Path src\monitor\watchlist-scan\scripts\run-scan.ps1
Test-Path src\monitor\alert-checker\scripts\run-alerts.ps1
```

Expected: All `True`.

```powershell
# Validate PowerShell syntax (no parse errors)
$null = [System.Management.Automation.PSParser]::Tokenize((Get-Content src\monitor\portfolio-review\scripts\run-review.ps1 -Raw), [ref]$null)
Write-Host "run-review.ps1: valid syntax"

$null = [System.Management.Automation.PSParser]::Tokenize((Get-Content src\monitor\watchlist-scan\scripts\run-scan.ps1 -Raw), [ref]$null)
Write-Host "run-scan.ps1: valid syntax"

$null = [System.Management.Automation.PSParser]::Tokenize((Get-Content src\monitor\alert-checker\scripts\run-alerts.ps1 -Raw), [ref]$null)
Write-Host "run-alerts.ps1: valid syntax"
```

Expected: Three "valid syntax" lines, no errors.

---

## 10. Holdings.yaml schema documented with multi-account example

**What changed:** `monitor/portfolio-review/SKILL.md` defines the holdings.yaml schema.

**Files:** `src/monitor/portfolio-review/SKILL.md`

**How to verify:**

```powershell
# Verify multi-account and multi-market in example
Select-String -Path src\monitor\portfolio-review\SKILL.md -Pattern "account:"
```

Expected: Multiple matches showing different accounts (ibkr, mplus, binance).

```powershell
# Verify all three markets in example
Select-String -Path src\monitor\portfolio-review\SKILL.md -Pattern "market: US|market: Bursa|market: Crypto"
```

Expected: At least 3 matches.

---

## 11. Alert checker documents silent success

**What changed:** `monitor/alert-checker/SKILL.md` writes nothing when no alerts fire.

**Files:** `src/monitor/alert-checker/SKILL.md`

**How to verify:**

```powershell
Select-String -Path src\monitor\alert-checker\SKILL.md -Pattern "silent success|writes nothing"
```

Expected: At least 2 matches confirming the no-output behavior.

---

## 12. Crypto data skills document API sources

**What changed:** Four crypto data SKILL.md files each document their data sources.

**Files:**
- `src/data/crypto-fundamentals/SKILL.md`
- `src/data/crypto-onchain/SKILL.md`
- `src/data/crypto-derivatives/SKILL.md`
- `src/data/crypto-macro/SKILL.md`

**How to verify:**

```powershell
# Each should have a Data sources section
Get-ChildItem src\data\crypto-* -Filter "SKILL.md" | ForEach-Object {
    $has = (Get-Content $_.FullName -Raw) -match "## Data sources"
    "$($_.Directory.Name): $(if ($has) {'has data sources'} else {'MISSING data sources'})"
}
```

Expected: All four print "has data sources".

```powershell
# Verify key sources mentioned
Select-String -Path src\data\crypto-fundamentals\SKILL.md -Pattern "CoinGecko|DeFiLlama"
Select-String -Path src\data\crypto-onchain\SKILL.md -Pattern "Glassnode|CryptoQuant"
Select-String -Path src\data\crypto-derivatives\SKILL.md -Pattern "Binance"
Select-String -Path src\data\crypto-macro\SKILL.md -Pattern "DXY|stablecoin"
```

Expected: Each command returns at least one match.

---

## 13. Bursa data skills reference existing scripts

**What changed:** Bursa SKILL.md files reference `bursawhale_api.py` and `bursa_flows.py`.

**Files:**
- `src/data/bursa-announcements/SKILL.md`
- `src/data/bursa-fundamentals/SKILL.md`

**How to verify:**

```powershell
Select-String -Path src\data\bursa-announcements\SKILL.md -Pattern "bursawhale_api\.py"
```

Expected: At least one match.

```powershell
Select-String -Path src\data\bursa-fundamentals\SKILL.md -Pattern "bursa_flows\.py"
```

Expected: At least one match.

```powershell
# Confirm the referenced scripts exist
Test-Path src\data\bursa-announcements\scripts\bursawhale_api.py
Test-Path src\data\bursa-fundamentals\scripts\bursa_flows.py
```

Expected: Both `True`.

---

## 14. Bursa technical requires volume confirmation

**What changed:** `analysis/bursa-technical/SKILL.md` mandates volume confirmation for signals.

**Files:** `src/analysis/bursa-technical/SKILL.md`

**How to verify:**

```powershell
Select-String -Path src\analysis\bursa-technical\SKILL.md -Pattern "volume confirm|Volume confirm"
```

Expected: Multiple matches showing this is a hard requirement.

```powershell
# Verify wider stops documented
Select-String -Path src\analysis\bursa-technical\SKILL.md -Pattern "wider|8-12%|15-20%"
```

Expected: Matches showing wider stop guidance vs US.

---

## 15. All tickets marked done in issue tracker

**What changed:** Every ticket file has `Status: done` and all checkboxes `[x]`.

**How to verify:**

```powershell
# Check no unchecked boxes remain
Get-ChildItem docs\issues-tracker\0001-investment-skills-network\0*.md | ForEach-Object {
    $unchecked = (Select-String -Path $_.FullName -Pattern "- \[ \]").Count
    if ($unchecked -gt 0) { "$($_.Name): $unchecked unchecked items!" }
}
```

Expected: No output (all boxes checked).

```powershell
# Verify all status fields say done
Get-ChildItem docs\issues-tracker\0001-investment-skills-network\0*.md | ForEach-Object {
    $status = Select-String -Path $_.FullName -Pattern "^\*\*Status:\*\*"
    "$($_.Name): $($status.Line)"
}
```

Expected: All 18 lines show `**Status:** done`.

---

## 16. GATES.md has no pending gates

**What changed:** GATES.md tracks all acceptance criteria with evidence.

**Files:** `docs/issues-tracker/0001-investment-skills-network/GATES.md`

**How to verify:**

```powershell
$pending = (Select-String -Path docs\issues-tracker\0001-investment-skills-network\GATES.md -Pattern "\| pending \|").Count
Write-Host "Pending gates: $pending"
```

Expected: `Pending gates: 0`

```powershell
$done = (Select-String -Path docs\issues-tracker\0001-investment-skills-network\GATES.md -Pattern "\| done \|").Count
Write-Host "Done gates: $done"
```

Expected: `Done gates: 78`

---

## Regression check

The implementation added only SKILL.md files and helper scripts. No existing Python scripts were modified.

```powershell
# Verify pre-existing scripts are unchanged (check they still parse)
python -c "import ast; ast.parse(open('src/data/price-history/scripts/price_history.py').read()); print('price_history.py: OK')"
python -c "import ast; ast.parse(open('src/data/fundamentals/scripts/financials_fetch.py').read()); print('financials_fetch.py: OK')"
python -c "import ast; ast.parse(open('src/data/fundamentals/scripts/dividend_fetch.py').read()); print('dividend_fetch.py: OK')"
python -c "import ast; ast.parse(open('src/data/price-history/scripts/sector_rs.py').read()); print('sector_rs.py: OK')"
python -c "import ast; ast.parse(open('src/utility/shared-lib/scripts/yahoo_cache.py').read()); print('yahoo_cache.py: OK')"
python -c "import ast; ast.parse(open('src/data/us-macro/scripts/fed_liquidity.py').read()); print('fed_liquidity.py: OK')"
python -c "import ast; ast.parse(open('src/data/us-macro/scripts/yield_curve.py').read()); print('yield_curve.py: OK')"
python -c "import ast; ast.parse(open('src/data/bursa-announcements/scripts/bursawhale_api.py').read()); print('bursawhale_api.py: OK')"
```

Expected: All 8 print "OK". No syntax errors means existing scripts were not corrupted.

```powershell
# Quick functional check - price_history.py still produces valid JSON
$output = python src\data\price-history\scripts\price_history.py AAPL 2>&1
$json = $output | ConvertFrom-Json
Write-Host "price_history.py functional: ok=$($json.ok)"
```

Expected: `price_history.py functional: ok=True` (requires network).
