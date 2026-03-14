# Run definitive_pull for San Diego, CA (75 mile radius)
# IMPORTANT: Your Definitive export must be hospital HEADQUARTERS only (not regional branches)
# and executives AT those HQ locations (not regional executives). See docs/definitive_hq_export_guide.md
#
# Usage: After exporting CSV from Definitive, run:
#   .\run_san_diego.ps1 -InputFile "C:\Users\User\Downloads\your_export.csv"
#
# Or place your export in the claydata folder and run:
#   .\run_san_diego.ps1 -InputFile ".\my_definitive_export.csv"

param(
    [Parameter(Mandatory=$true, HelpMessage="Path to your Definitive CSV export")]
    [string]$InputFile
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

$outputFile = "hospitals_san_diego_75mi.csv"
$citiesFile = "data\cities_san_diego_75mi.txt"

Write-Host "Filtering hospital HQ + C-level executives to cities within 75 miles of San Diego, CA..."
python scripts/definitive_pull.py --mode csv --input $InputFile --cities-filter $citiesFile --output $outputFile

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nDone! Output saved to: $outputFile"
    Write-Host "Import this file into Clay and add contact enrichment (see docs/clay_setup_guide.md)"
}
