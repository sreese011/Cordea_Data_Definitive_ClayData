# Interactive Definitive → Clay workflow
# Asks for city, resolves to ZIP, then either:
#   - API mode: Pulls report directly from Definitive (no manual export)
#   - Manual mode: Guides you through Report Builder export, review, Clay import
#
# Settings: Copy config/example.env to .env
#   DEFINITIVE_USERNAME, DEFINITIVE_PASSWORD  (API mode)
#   REPORT_SAVE_FOLDER                      (default: Contact Lists/)
#
# Usage:
#   .\run_definitive_to_clay.ps1
#   .\run_definitive_to_clay.ps1 -City "San Diego, CA"
#   .\run_definitive_to_clay.ps1 -Api -ReportName "My Report" -City "San Diego"
#   .\run_definitive_to_clay.ps1 -Api -ReportName "My Report" -OutputDir "C:\Reports"

param(
    [string]$City,
    [switch]$Api,
    [string]$ReportName,
    [string]$OutputDir
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

$scriptArgs = @()
if ($City) { $scriptArgs += "--city"; $scriptArgs += $City }
if ($Api) { $scriptArgs += "--api" }
if ($ReportName) { $scriptArgs += "--report-name"; $scriptArgs += $ReportName }
if ($OutputDir) { $scriptArgs += "--output-dir"; $scriptArgs += $OutputDir }

python scripts/definitive_to_clay.py @scriptArgs
