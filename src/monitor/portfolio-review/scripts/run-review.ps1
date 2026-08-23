#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Cron target for portfolio review. Invokes the Kiro agent with the portfolio-review skill.

.DESCRIPTION
    This script is designed to be called by an external scheduler (Task Scheduler on Windows,
    cron on Linux/Mac). It triggers the agent to run the portfolio-review skill.

.EXAMPLE
    # Windows Task Scheduler - run weekly on Sunday at 9:00 AM
    # Action: powershell.exe
    # Arguments: -ExecutionPolicy Bypass -File "C:\path\to\investment-skills\src\monitor\portfolio-review\scripts\run-review.ps1"

    # Linux/Mac cron (if using pwsh)
    # 0 9 * * 0 pwsh /path/to/investment-skills/src/monitor/portfolio-review/scripts/run-review.ps1
#>

$ErrorActionPreference = "Stop"

# Resolve paths
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SkillsRoot = if ($env:SKILLS_ROOT) { $env:SKILLS_ROOT } else { (Resolve-Path "$ScriptDir\..\..\..").Path }
$HoldingsFile = Join-Path $env:USERPROFILE "notes\portfolio\holdings.yaml"

# Validate holdings file exists
if (-not (Test-Path $HoldingsFile)) {
    Write-Error "Holdings file not found at: $HoldingsFile"
    Write-Error "Create it with your portfolio positions. See monitor/portfolio-review/SKILL.md for schema."
    exit 1
}

# Output info
$Today = Get-Date -Format "yyyy-MM-dd"
$Month = Get-Date -Format "yyyy-MM"
$OutputDir = Join-Path $env:USERPROFILE "notes\portfolio\reviews\$Month"

Write-Host "Portfolio Review - $Today"
Write-Host "Holdings: $HoldingsFile"
Write-Host "Output: $OutputDir\$Today-portfolio-review.md"
Write-Host ""
Write-Host "To run this review, invoke the agent with:"
Write-Host "  'Run portfolio review using monitor/portfolio-review skill'"
Write-Host ""
Write-Host "This script validates the environment. The actual review"
Write-Host "is performed by the Kiro agent reading the SKILL.md."

# Ensure output directory exists
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

# Print holdings summary
Write-Host "--- Holdings Summary ---"
Get-Content $HoldingsFile | Select-Object -First 30
Write-Host "..."
