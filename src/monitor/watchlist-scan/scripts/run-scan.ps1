#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Cron target for watchlist scan. Invokes the Kiro agent with the watchlist-scan skill.

.DESCRIPTION
    This script is designed to be called by an external scheduler (Task Scheduler on Windows,
    cron on Linux/Mac). It triggers the agent to run the watchlist-scan skill.

.EXAMPLE
    # Windows Task Scheduler - run weekly on Sunday at 10:00 AM (after portfolio review)
    # Action: powershell.exe
    # Arguments: -ExecutionPolicy Bypass -File "C:\path\to\investment-skills\src\monitor\watchlist-scan\scripts\run-scan.ps1"

    # Linux/Mac cron (if using pwsh)
    # 0 10 * * 0 pwsh /path/to/investment-skills/src/monitor/watchlist-scan/scripts/run-scan.ps1
#>

$ErrorActionPreference = "Stop"

# Resolve paths
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SkillsRoot = if ($env:SKILLS_ROOT) { $env:SKILLS_ROOT } else { (Resolve-Path "$ScriptDir\..\..\..").Path }
$WatchlistFile = Join-Path $env:USERPROFILE "notes\watchlist\watchlist.yaml"

# Validate watchlist file exists
if (-not (Test-Path $WatchlistFile)) {
    Write-Error "Watchlist file not found at: $WatchlistFile"
    Write-Error "Create it with tickers to track. See monitor/watchlist-scan/SKILL.md for schema."
    exit 1
}

# Output info
$Today = Get-Date -Format "yyyy-MM-dd"
$Month = Get-Date -Format "yyyy-MM"
$OutputDir = Join-Path $env:USERPROFILE "notes\watchlist\scans\$Month"

Write-Host "Watchlist Scan - $Today"
Write-Host "Watchlist: $WatchlistFile"
Write-Host "Output: $OutputDir\$Today-watchlist-scan.md"
Write-Host ""
Write-Host "To run this scan, invoke the agent with:"
Write-Host "  'Run watchlist scan using monitor/watchlist-scan skill'"
Write-Host ""
Write-Host "This script validates the environment. The actual scan"
Write-Host "is performed by the Kiro agent reading the SKILL.md."

# Ensure output directory exists
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

# Print watchlist summary
Write-Host "--- Watchlist Summary ---"
Get-Content $WatchlistFile | Select-Object -First 30
Write-Host "..."
