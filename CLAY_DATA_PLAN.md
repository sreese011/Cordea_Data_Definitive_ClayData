# Clay Hospital Data Plan

## Ultimate Goal

**Get lists of hospital headquarters (HQ) within 100 miles of your chosen geographic locations, plus C-level executives based at those HQ locations, and export them as CSV files from Clay.** You want Clay configured correctly and to use Clay credits efficiently by testing on a small sample before running the full pull.

**Important:** Only **headquarters locations**—not regional offices, branches, or satellite facilities. Only **executives who work at HQ**—not regional managers or executives at other locations.

---

## Settings and Configuration

Copy `config/example.env` to `.env` and fill in your values:

| Variable | Required | Description |
|----------|----------|-------------|
| `DEFINITIVE_USERNAME` | API mode (yes) | Definitive Healthcare login |
| `DEFINITIVE_PASSWORD` | API mode (yes) | Definitive Healthcare password |
| `REPORT_SAVE_FOLDER` | No | Folder for API downloads. Default: `Contact Lists/` in project root |
| `MAPBOX_ACCESS_TOKEN` | No | Optional; improves city→ZIP geocoding |

**Report save folder:** API-downloaded reports are saved to `Contact Lists/` by default. Override with `REPORT_SAVE_FOLDER` in `.env` or `--output-dir` on the command line.

**Report filename:** `{city}_{YYYY-MM-DD}.csv` (e.g. `san_diego_2025-03-13.csv`). Pass `--city` for the filename when using API mode.

---

## Recommended Workflow: Interactive Tool

Use the **Definitive → Clay** tool for the smoothest experience:

```
.\run_definitive_to_clay.ps1
# or: python scripts/definitive_to_clay.py
```

**API mode (no manual export):** If you have Definitive API credentials and a saved Report Builder report:

```powershell
.\run_definitive_to_clay.ps1 -Api -ReportName "Your Report Name" -City "San Diego"
# or: python scripts/definitive_to_clay.py --api --report-name "Your Report Name" --city "San Diego"
```

Reports are saved to `Contact Lists/` as `{city}_{date}.csv`. Set `DEFINITIVE_USERNAME` and `DEFINITIVE_PASSWORD` in `.env`.

**Manual mode:** The tool will:
1. **Ask for city** (e.g. San Diego, CA)
2. **Resolve to ZIP** (for Definitive geography filter)
3. **Open Definitive** with instructions: use **Report Builder** (not table view), enter ZIP + 100 miles in Geography, then Export
4. **Let you choose** the export file (or pick from recent Downloads)
5. **Show preview and open for review** (Excel, etc.)
6. **Open Clay** for import and enrichment

**Important:** Use **Report Builder** to create reports—table view cannot be exported. When you use Definitive's geography filter (ZIP + 100 miles), the export is **already filtered**. No need to add a distance filter in Clay.

---

## Best Plan Overview

```
Definitive (data source) → Clay (filter + enrich) → CSV export
```

| Phase | What | Where |
|-------|------|--------|
| 1. Source the data | Hospital HQs + HQ-based executives (addresses) | Definitive: **Geography = ZIP + 100 mi radius** (filters before export) |
| 2. Import to Clay | Create base table | Clay: Import CSV |
| 3. Filter by distance | *(Optional)* Only if you did NOT use Definitive geography | Clay: Mapbox "Distance Between Two Locations" |
| 4. Enrich contacts | Add email, phone, etc. | Clay: contact enrichment providers |
| 5. Export | Download final table | Clay: CSV export |

---

## Credit-Efficient Workflow

1. **Test distance logic** on 5–10 rows first.
2. **Test enrichment** on 1–2 rows (~2–14 credits) to confirm quality.
3. **Run enrichment on full filtered table** once satisfied.
4. **Download CSV** from Clay.

---

## Key Constraints

- **Definitive:** You need access to pull hospitals + executives (with addresses)—either via web reports (sts.defhc.com) or API.
- **Clay:** Does not pull from Definitive directly (no pagination). Import via CSV.
- **Agent (optional):** Step-by-step instructions or browser automation; Clay has no API for configuration.

---

## Manual Instructions (Simple Version)

*Written for someone with minimal technical experience.*

---

### Part 1: Get the Hospital HQ List from Definitive

**What you're doing:** Getting a list of **hospital headquarters only** (not regional branches) and **executives who work at those HQ locations** from the Definitive website, **filtered by geography** so you only get hospitals within 100 miles of your city.

**Steps:**

1. Run `.\run_definitive_to_clay.ps1` (or `python scripts/definitive_to_clay.py`) and enter your city. It will resolve to a ZIP and open Definitive.
2. Go to: **https://sts.defhc.com** (if not already open).
3. Log in with your Definitive username and password.
4. Go to **Report Builder** (not table view—table view cannot be exported).
5. Create or open a report with hospitals and executives.
6. **Apply Geography filter (Modify Search / Geography):**
   - **ZIP code:** Use the ZIP the tool gave you (e.g. 92101 for San Diego).
   - **Radius:** 100 miles.
   - This filters *before* export—you only get hospitals within 100 miles.
7. **Apply filters to get HQ only:**
   - Look for: **"Headquarters"**, **"Primary facility"**, **"Parent organization"**, or **"HQ"**
   - Exclude: **"Branch"**, **"Satellite"**, **"Regional"**, or similar
8. Filter for C-level executives (CEO, CFO, COO, etc.) **at HQ**.
9. **Save the report**, then click **Download** or **Export** → **CSV** or **Excel**.
10. Remember where the file went (usually **Downloads**).

---

### Part 2: Make Sure the File Is Ready for Clay

**What you're doing:** Checking that the list has the important stuff before you bring it into Clay.

**Steps:**

1. Open the file you downloaded (double-click it).
2. You should see columns like: Hospital name, Hospital HQ address, Executive names (C-level at HQ).
3. Confirm the addresses are HQ locations, not regional offices.
3. If it looks good, close it. You're ready!

---

### Part 3: Put the List Into Clay

**What you're doing:** Taking the list you downloaded and putting it into Clay so Clay can add more info to it.

**Steps:**

1. Open your browser and go to: **https://app.clay.com**
2. Log in with your Clay account.
3. Click **New table** or **Create table** (a plus sign or "New" button).
4. Look for **Import** or **Add data**.
5. Click **Upload file** or **From computer**.
6. Click **Choose file** and pick the CSV or Excel file you downloaded.
7. Clay might ask you to match up columns—pick the right names if it does.
8. Click **Import** or **Done**.

---

### Part 4: Add Distance *(Only if you did NOT use Definitive geography filter)*

**If you used Definitive's Geography filter (ZIP + 100 miles):** Skip this step—your data is already within 100 miles.

**If you exported a national list from Definitive:** Use Clay to filter by distance:

1. In Clay, look for **Add column** or a **+** next to your columns.
2. Search for **Distance** or **Mapbox**.
3. Pick **"Distance between two locations"** (or similar).
4. For the first location: type in the address or city you care about.
5. For the second location: use the column with the **hospital address**.
6. Add a filter to **only keep rows where distance ≤ 100 miles** (or 75 if you prefer).

---

### Part 5: Add Emails and Phone Numbers (Test First!)

**What you're doing:** Adding contact info (emails and phones) to the list. You test on a few rows first so you don't burn credits.

**Step A – Test on a small amount first:**

1. In Clay, find a way to run or update just a few rows (like 5 rows). Look for **Run on 5 rows** or **Test**.
2. Add a column to find **work email** (Apollo, People Data Labs, etc.).
3. Add a column to find **phone number** if you want it.
4. Run it on **5 rows only**.
5. Look at the results. Does it look right?
6. If yes, go to Step B. If not, adjust and test again.

**Step B – Run on the full list:**

1. When happy with the test, click **Run on full table** or **Run on all rows**.
2. Wait for Clay to finish. This is when it uses most of your credits.
3. When done, your table will have the extra columns filled in.

---

### Part 6: Download Your Final List

**What you're doing:** Saving the final list to your computer so you can use it in Excel or send it to someone.

**Steps:**

1. When the table is done, look for **Export**, **Download**, or a download arrow.
2. Click it and pick **CSV** or **Excel**.
3. Save the file somewhere you can find it (Desktop or Downloads).
4. You're done! You now have your list of hospitals within 100 miles with executive names and contact info.

---

## Quick Checklist

- [ ] Run `.\run_definitive_to_clay.ps1`, enter city
- [ ] In Definitive: Geography = ZIP + 100 mi, export HQ + executives
- [ ] Use tool to pick export file, review, then import to Clay
- [ ] Add email and phone columns in Clay; run on 5 rows first
- [ ] Run on full table when satisfied
- [ ] Download the final CSV/Excel file

---

## Command Reference

| Option | Description |
|--------|-------------|
| `.\run_definitive_to_clay.ps1` | Interactive; prompts for city |
| `-City "San Diego"` | Pre-fill city (for ZIP lookup and filename) |
| `-Api` | Pull report via API instead of manual export |
| `-ReportName "Report Name"` | Definitive Report Builder report name (API mode) |
| `-OutputDir "C:\path"` | Override save folder (default: Contact Lists/) |

---

## Credits (With ~14,000 Clay Credits)

- Contact enrichment: ~2–14 credits per row
- Rough capacity: ~1,000–2,000 rows with full enrichment
- Always test on 5 rows first (~10–70 credits) before full run
