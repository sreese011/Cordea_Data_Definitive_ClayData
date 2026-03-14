# Claydata: Hospital HQ + Executive Lists

Get lists of **hospital headquarters** (HQ only, not regional branches) within **100 miles** of a geographic location, with **C-level executives at those HQ locations** and their contact info. Output is ready for Clay import; you download CSV from Clay after enrichment.

**Important:** Data must be hospital headquarters and HQ-based executives—not regional facilities or regional executives.

## What This Does

1. **Definitive Healthcare** → Source for hospitals + executives (API or web export); filter by ZIP + 100 miles
2. **Script** → Optional post-filter, or use the interactive workflow for city → Definitive → Clay
3. **Clay** → Import, enrich with email/phone, export CSV

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Interactive Workflow (Recommended)

The easiest path: city → Definitive export → review → Clay import.

```powershell
.\run_definitive_to_clay.ps1
# or: python scripts/definitive_to_clay.py
```

You’ll enter a city (e.g. San Diego, CA); the tool resolves it to a ZIP, opens Definitive with instructions to use ZIP + 100 miles, lets you pick and review the export file, then opens Clay for import.

**API mode (automatic download):** With Definitive credentials in `.env`:

```powershell
.\run_definitive_to_clay.ps1 -Api -ReportName "Your Report" -City "San Diego"
```

Reports are saved to `Contact Lists/` as `{city}_{date}.csv`. See [CLAY_DATA_PLAN.md](CLAY_DATA_PLAN.md) for settings.

### 3. Or Run the Script Directly (CSV Mode)

**Option A - City list (recommended, no geocoding needed):**

Build a city list, then filter your Definitive export by those cities:

```bash
# 1. Generate cities within 75 miles of San Diego (uses data/cities_san_diego_75mi.txt)
#    Or use the pre-built list: data/cities_san_diego_75mi.txt

# 2. Filter your Definitive export by city
python scripts/definitive_pull.py --mode csv --input your_export.csv --cities-filter data/cities_san_diego_75mi.txt --output hospitals_san_diego_75mi.csv
```

**Option B - Geocoding (requires Mapbox token for reliability):**

```bash
python scripts/definitive_pull.py --mode csv --input your_export.csv --lat 32.7157 --lon -117.1611 --radius 75 --output hospitals_within_75_miles.csv
```

### 3. Import to Clay

1. Go to https://app.clay.com
2. Create a new table
3. Import the CSV (`hospitals_within_75_miles.csv`)
4. Add enrichment columns for email and phone
5. **Test on 5 rows first**, then run on full table
6. Download your final CSV

See [docs/clay_setup_guide.md](docs/clay_setup_guide.md) for Clay setup and [docs/definitive_hq_export_guide.md](docs/definitive_hq_export_guide.md) for exporting HQ-only data from Definitive.

---

## Script Options

### CSV Mode (Recommended if you export from Definitive web)

```bash
python scripts/definitive_pull.py --mode csv --input path/to/export.csv --lat 40.7128 --lon -74.0060 [--output output.csv] [--radius 75] [--address-column ColumnName]
```

- `--input` – Path to your Definitive CSV export
- `--lat`, `--lon` – Center point (e.g., your office or city)
- `--output` – Output CSV path (default: `hospitals_within_75_miles.csv`)
- `--radius` – Miles from center (default: 75)
- `--address-column` – Column with hospital address (auto-detected if omitted)

### API Mode (If you have Definitive API access)

```bash
# Set credentials (or use --definitive-user and --definitive-password)
set DEFINITIVE_USERNAME=your_username
set DEFINITIVE_PASSWORD=your_password

python scripts/definitive_pull.py --mode api --lat 40.7128 --lon -74.0060 [--max-records 500]
```

---

## Project Structure

```
claydata/
├── Contact Lists/            # Default folder for API-downloaded reports
├── scripts/
│   ├── definitive_pull.py    # Pull + geo-filter script
│   └── definitive_to_clay.py # Interactive workflow (city → Definitive → Clay)
├── config/
│   └── example.env           # Copy to .env; set DEFINITIVE_USERNAME, etc.
├── data/
│   └── cities_san_diego_75mi.txt
├── docs/
│   └── clay_setup_guide.md   # Step-by-step Clay setup
├── CLAY_DATA_PLAN.md         # Full plan, settings, manual instructions
├── run_definitive_to_clay.ps1
├── requirements.txt
└── README.md
```

---

## Credits

- **Script + geo filter** – No Clay credits
- **Clay enrichment** – ~2–14 credits per row (email, phone)
- **With ~14,000 credits** – Roughly 1,000–2,000 rows
- **Always test on 5 rows first** to avoid wasting credits

---

## See Also

- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) – Consolidated goal, plan, settings, and documentation index
- [CLAY_DATA_PLAN.md](CLAY_DATA_PLAN.md) – Full plan and manual instructions
- [docs/clay_setup_guide.md](docs/clay_setup_guide.md) – Clay configuration guide
