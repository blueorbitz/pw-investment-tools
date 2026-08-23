#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Cron target for alert checking. Invokes the Kiro agent with the alert-checker skill.

.DESCRIPTION
    This script is designed to be called by an external scheduler. It triggers the agent
    to evaluate custom alert conditions defined in holdings.yaml.

    Can run more frequently than portfolio review (e.g., daily for crypto positions).

.EXAMPLE
    # Windows Task Scheduler - run daily at 8:00 AM
    # Action: powershell.exe
    # Arguments: -ExecutionPolicy Bypass -File "C:\path\to\investment-skills\src\monitor\alert-checker\scripts\run-alerts.ps1"

    # Linux/Mac cron - daily at 8am
    # 0 8 * * * pwsh /path/to/investment-skills/src/monitor/alert-checker/scripts/run-alerts.ps1

    # More frequent for crypto (every 4 hours)
    # 0 */4 * * * pwsh /path/to/investment-skills/src/monitor/alert-checker/scripts/run-alerts.ps1
#>

$ErrorActionPreference = "Stop"

# Resolve paths
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SkillsRoot = if ($env:SKILLS_ROOT) { $env:SKILLS_ROOT } else { (Resolve-Path "$ScriptDir\..\..\..").Path }
$HoldingsFile = Join-Path $env:USERPROFILE "notes\portfolio\holdings.yaml"

# Validate holdings file exists
if (-not (Test-Path $HoldingsFile)) {
    Write-Error "Holdings file not found at: $HoldingsFile"
    Write-Error "Create it with alert_conditions. See monitor/alert-checker/SKILL.md for schema."
    exit 1
}

# Check if any positions have alert_conditions
$content = Get-Content $HoldingsFile -Raw
if ($content -notmatch "alert_conditions") {
    Write-Host "No alert_conditions found in holdings.yaml. Nothing to check."
    exit 0
}

# Output info
$Today = Get-Date -Format "yyyy-MM-dd"
$Month = Get-Date -Format "yyyy-MM"
$OutputDir = Join-Path $env:USERPROFILE "notes\portfolio\alerts\$Month"

Write-Host "Alert Checker - $Today $(Get-Date -Format 'HH:mm')"
Write-Host "Holdings: $HoldingsFile"
Write-Host "Output (if alerts fire): $OutputDir\$Today-alerts.md"
Write-Host ""
Write-Host "To run this check, invoke the agent with:"
Write-Host "  'Run alert checker using monitor/alert-checker skill'"
Write-Host ""
Write-Host "This script validates the environment. The actual check"
Write-Host "is performed by the Kiro agent reading the SKILL.md."

# Ensure output directory exists
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}
