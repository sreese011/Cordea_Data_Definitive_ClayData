# Claydata Project Summary

**Last updated:** March 2025

This document consolidates the project goal, plan, settings, and all documentation for the Definitive → Clay hospital executive workflow.

---

## Ultimate Goal

**Get lists of hospital headquarters (HQ) within 100 miles of your chosen geographic locations, plus C-level executives based at those HQ locations, and export them as CSV files from Clay.**

**Scope:** Only headquarters locations—not regional offices, branches, or satellite facilities. Only executives who work at HQ—not regional managers.

---

## Plan Steps (5 Phases)

| Step | Action | Where |
|------|--------|-------|
| **1. Source data** | Hospital HQs + HQ-based executives within 100 miles of ZIP | Definitive Report Builder or API: Geography = ZIP + 100 mi |
| **2. Import to Clay** | Create base table | Clay: Import CSV |
| **3. Filter by distance** | *(Optional)* Only if Definitive geography was not used | Clay: Mapbox "Distance between two locations" |
| **4. Enrich contacts** | Add email, phone | Clay: contact enrichment providers |
| **5. Export** | Download final table | Clay: CSV export |

---

## Quick Start

### One-time setup
1. Copy `config/example.env` to `.env`
2. Set `DEFINITIVE_USERNAME` and `DEFINITIVE_PASSWORD` (for API mode)
3. `pip install -r requirements.txt`

### Run the workflow
```powershell
.\run_definitive_to_clay.ps1
# Or API mode (automatic download):
.\run_definitive_to_clay.ps1 -Api -ReportName "Your Report" -City "San Diego"
```

---

## Settings and Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `DEFINITIVE_USERNAME` | API mode | Definitive Healthcare login |
| `DEFINITIVE_PASSWORD` | API mode | Definitive Healthcare password |
| `REPORT_SAVE_FOLDER` | No | Folder for API downloads. Default: `Contact Lists/` |
| `MAPBOX_ACCESS_TOKEN` | No | Improves city→ZIP geocoding (optional) |

**Report save folder:** `Contact Lists/` in project root (default). Override with `REPORT_SAVE_FOLDER` or `--output-dir`.

**Report filename:** `{city}_{YYYY-MM-DD}.csv` (e.g. `san_diego_2025-03-13.csv`)

---

## Command Reference

| Command | Description |
|---------|-------------|
| `.\run_definitive_to_clay.ps1` | Interactive; prompts for city |
| `.\run_definitive_to_clay.ps1 -City "San Diego"` | Pre-fill city |
| `.\run_definitive_to_clay.ps1 -Api -ReportName "X" -City "San Diego"` | API mode; save to Contact Lists |
| `.\run_definitive_to_clay.ps1 -Api -ReportName "X" -OutputDir "C:\path"` | Override save folder |

---

## Project Structure

```
claydata/
├── Contact Lists/            # Default folder for API-downloaded reports
├── scripts/
│   ├── definitive_to_clay.py # Main interactive workflow (city → Definitive → Clay)
│   ├── definitive_pull.py    # Geo-filter script (CSV mode)
│   └── build_cities_near.py  # Build city list for filtering
├── config/
│   └── example.env          # Copy to .env
├── data/
│   └── cities_san_diego_75mi.txt
├── docs/
│   ├── clay_setup_guide.md
│   ├── definitive_hq_export_guide.md
│   └── CITY_SCRIPT_README.md
├── CLAY_DATA_PLAN.md        # Full plan and manual instructions
├── PROJECT_SUMMARY.md       # This file
├── run_definitive_to_clay.ps1
├── requirements.txt
└── README.md
```

---

## Documentation Index

| File | Purpose |
|------|---------|
| **README.md** | Project overview and quick start |
| **CLAY_DATA_PLAN.md** | Full plan, settings, manual instructions, checklist |
| **PROJECT_SUMMARY.md** | Consolidated summary (this file) |
| **config/example.env** | Environment variable template |
| **docs/clay_setup_guide.md** | Step-by-step Clay import and enrichment |
| **docs/definitive_hq_export_guide.md** | How to get HQ-only data from Definitive |
| **docs/CITY_SCRIPT_README.md** | City list and filtering workflow |
| **EXTRACT_SAN_DIEGO_75MI.md** | San Diego preset instructions |

---

## Key Updates (Session Summary)

- **Report Builder:** Use Report Builder (not table view); table view cannot be exported
- **ZIP + 100 miles:** Definitive geography filter (ZIP + radius) filters before export
- **API mode:** Pull reports directly via Definitive Reports API (no manual export)
- **Report save folder:** Default `Contact Lists/` in project root
- **Report filename:** `{city}_{YYYY-MM-DD}.csv` for traceability
- **City → ZIP:** Automatic resolution via geopy + uszipcode

---

## Credits

- **Script/API:** No Clay credits
- **Clay enrichment:** ~2–14 credits per row
- **Capacity:** ~1,000–2,000 rows with ~14,000 credits
- **Always test on 5 rows first** before full table run
