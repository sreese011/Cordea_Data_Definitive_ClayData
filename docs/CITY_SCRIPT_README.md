# City & ZIP Filter Script: Reusable Guide

Use this tool to pull hospital HQ executives within a radius of any meeting location. Build a list of cities (and optionally ZIP codes) within your radius, then filter Definitive Healthcare exports to only those locations.

---

## Quick Start (Any City)

### 1. Create your location list

Create a text file with **one city name or ZIP code per line**. Mix cities and ZIPs as needed.

**City names** (case-insensitive):
```
San Diego
Chula Vista
Oceanside
Escondido
```

**ZIP codes** (5-digit; 9-digit +4 are auto-truncated):
```
92101
92103
92054
```

**Example combined file** (`data/my_meeting_location.txt`):
```
San Diego
Chula Vista
92101
92103
92111
Oceanside
92054
Escondido
```

### 2. Export from Definitive Healthcare

1. Log in at https://sts.defhc.com
2. Search for **hospital headquarters** + **C-level executives**
3. Filter by your meeting region if possible (or export broad, we filter next)
4. Ensure your export includes **City** and/or **State** and **ZIP** columns
5. Export as CSV

### 3. Run the filter

```powershell
cd c:\DEV_Cursor\claydata
python scripts/definitive_pull.py --input "path\to\your_export.csv" --cities-filter data\my_meeting_location.txt --output hospitals_my_meeting.csv
```

### 4. Import to Clay

Import the output CSV into Clay, add contact enrichment (email, phone), test on 5 rows, then run on full table. Download when done. See [clay_setup_guide.md](clay_setup_guide.md).

---

## Filter File Format

| Entry type | Format | Example | Notes |
|------------|--------|---------|-------|
| City name | Any non-numeric text | San Diego, Chula Vista | Case-insensitive match |
| ZIP code | 5 digits (or 9 with hyphen) | 92101, 92103-1234 | First 5 digits used |

- One entry per line
- Blank lines ignored
- Comments: prefix with `#` (not yet supported; avoid for now)

---

## Reuse for New Meeting Locations

### Option A: Use an online radius tool

1. Go to https://milesofme.com/ or https://www.freemaptools.com/radius-around-point.htm
2. Enter your meeting city (e.g. "Chicago, IL") or address
3. Set radius (e.g. 75 miles)
4. Copy the list of cities (and ZIPs if shown) into a new `.txt` file
5. Save as `data/cities_<location>_75mi.txt`

### Option B: Use pre-built data files

For San Diego, a pre-built list is included:

- `data/cities_san_diego_75mi.txt` — cities within 75 miles of San Diego, CA

Copy this file as a template and replace with cities for your location.

### Option C: Build from ZIP codes

If you have a list of ZIP codes (e.g. from a sales territory or radius tool):

1. Create `data/my_location.txt`
2. Add one ZIP per line (5-digit)
3. Run with `--cities-filter` — the script will match on the ZIP column

---

## Command Reference

### Filter by city/ZIP list (recommended)

```powershell
python scripts/definitive_pull.py ^
  --input "definitive_export.csv" ^
  --cities-filter "data/my_location.txt" ^
  [--city-column City] ^
  [--zip-column "ZIP Code"] ^
  --output "hospitals_filtered.csv"
```

- `--input` — Your Definitive CSV export
- `--cities-filter` — Path to text file (cities and/or ZIPs, one per line)
- `--city-column` — Override city column name (auto-detects: City, city, hospital_city)
- `--zip-column` — Override ZIP column name (auto-detects: zip, zipcode, zip_code, postal_code)
- `--output` — Output CSV path

### Filter by geocoding (alternative)

If you prefer per-row geocoding instead of a city list:

```powershell
python scripts/definitive_pull.py ^
  --input "definitive_export.csv" ^
  --lat 32.7157 --lon -117.1611 ^
  --radius 75 ^
  --output "hospitals_filtered.csv"
```

Uses Mapbox (set `MAPBOX_ACCESS_TOKEN` in `.env`) or Nominatim for geocoding. Slower and can fail on some addresses.

---

## San Diego Example (Pre-built)

```powershell
.\run_san_diego.ps1 -InputFile "C:\Users\User\Downloads\definitive_export.csv"
```

Uses `data/cities_san_diego_75mi.txt` and outputs `hospitals_san_diego_75mi.csv`.

---

## Creating a Run Script for Another City

Copy `run_san_diego.ps1` and edit:

```powershell
# run_chicago.ps1
param([Parameter(Mandatory=$true)][string]$InputFile)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

$outputFile = "hospitals_chicago_75mi.csv"
$citiesFile = "data\cities_chicago_75mi.txt"  # Create this file first

python scripts/definitive_pull.py --mode csv --input $InputFile --cities-filter $citiesFile --output $outputFile
```

Create `data/cities_chicago_75mi.txt` with cities/ZIPs within 75 miles of Chicago.

---

## Data Requirements

Your Definitive export must include:

| Column | Purpose |
|--------|---------|
| City (or similar) | Matched against city names in filter file |
| ZIP / ZipCode / Postal Code | Matched against ZIPs in filter file |
| Hospital Name | For context |
| Executive Name, Title | For C-level executives |
| Business Email, Phone | Often empty; Clay enrichment adds these |

At least one of **City** or **ZIP** must exist for the filter to work.

---

## Troubleshooting

**"Kept 0 rows"**  
- Check that your filter file has correct city names (match Definitive exactly, e.g. "Chula Vista" not "ChulaVista")
- If using ZIPs, ensure your export has a ZIP column and values are 5-digit
- Use `--city-column` and `--zip-column` if your columns have different names

**"No City or ZIP column found"**  
- Your export needs at least one location column. Add `--city-column "Your Column Name"` or `--zip-column "Your ZIP Column"`

**Definitive has different city names**  
- Normalize: e.g. "St. Louis" vs "Saint Louis" — add both to your filter file if needed

---

## Project Structure

```
claydata/
├── scripts/
│   ├── definitive_pull.py    # Main filter script (city/ZIP or geocode)
│   └── build_cities_near.py  # Optional: generate city list (uszipcode)
├── data/
│   ├── cities_san_diego_75mi.txt   # Pre-built San Diego
│   └── cities_<location>.txt      # Add for other cities
├── docs/
│   ├── CITY_SCRIPT_README.md      # This file
│   ├── clay_setup_guide.md        # Clay import & enrichment
│   └── definitive_hq_export_guide.md
├── run_san_diego.ps1
├── CLAY_DATA_PLAN.md
└── PROJECT_SUMMARY.md
```
