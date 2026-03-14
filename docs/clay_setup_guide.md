# Clay Setup Guide: Hospital HQ + Executive Data

Step-by-step guide to configure Clay to produce **hospital headquarters** (HQ) lists within 100 miles with **executives at those HQ locations**. Written in simple language.

**Important:** We need **headquarters locations only**—not regional branches, satellites, or outpatient centers. Executives must be those based at HQ, not regional managers.

---

## Before You Start

You need:

1. A **Clay** account (https://app.clay.com)
2. A **CSV file** from the `definitive_pull` script (or from Definitive web export)
3. The CSV must have: **hospital HQ name**, **HQ address**, **executive names at HQ** (and titles if available)

---

## Part 1: Create a New Table in Clay

1. Open your browser and go to **https://app.clay.com**
2. Log in with your Clay account
3. Click **New table** or **Create table** (look for a plus sign or "New" button)
4. Give the table a name like "Hospitals Within 100 Miles"

---

## Part 2: Import Your CSV

1. In the new table, look for **Import** or **Add data** or **Add source**
2. Click **Upload file** or **From computer** or **Import CSV**
3. Click **Choose file** and pick your CSV (e.g. from `Contact Lists/` or `hospitals_within_75_miles.csv`)
4. Clay may show you a preview and ask you to match columns
   - If it asks, make sure each column from your file maps to the right Clay column
   - Click **Import** or **Confirm** when done

---

## Part 3: Verify the Distance Column (Optional)

If you ran the `definitive_pull` script, your CSV already has a `distance_miles` column. You can:

- **Skip this step** if you used Definitive geography filter (ZIP + 100 miles) or the script already filtered (your output only contains within-range rows)
- **Or** add a filter in Clay: show only rows where `distance_miles` is less than or equal to 100

To add a filter in Clay:

1. Look for **Filter** or **Filter rows** or a funnel icon
2. Add a rule: `distance_miles` ≤ 100
3. Apply the filter

---

## Part 4: Add Contact Enrichment (Email and Phone)

### Test on 5 Rows First

1. Find the option to **Run on 5 rows** or **Test** or **Run on sample**
2. Add a new column: click **Add enrichment** or the **+** next to your columns
3. Search for **"Find work email"** or **"Email finder"**
4. Pick a provider (Apollo, People Data Labs, Lusha, etc.)
5. Map: use the `executive_name` and `hospital_name` columns to find the email
6. Run on **5 rows only** (do not run on full table yet)
7. Check the results. Are the emails correct?
8. If yes, add a **phone** column the same way (optional)
9. Run on 5 rows again for the phone column

### Run on Full Table

1. When you are happy with the test results, click **Run on full table** or **Run on all rows**
2. Wait for Clay to finish (this uses credits)
3. When done, all rows will have email (and phone if you added it) filled in

---

## Part 5: Download Your Final List

1. When the table is complete, look for **Export** or **Download** or a download arrow
2. Click it and choose **CSV** or **Excel**
3. Save the file to your computer
4. You now have your list of hospitals within 100 miles with executive names and contact info

---

## Quick Reference: Credit-Saving Checklist

- [ ] Run `run_definitive_to_clay.ps1` or `definitive_pull` script first (no Clay credits used)
- [ ] Import CSV to Clay
- [ ] Add email enrichment column
- [ ] **Run on 5 rows** and verify output
- [ ] Add phone enrichment column (optional)
- [ ] **Run on 5 rows** again
- [ ] **Run on full table** only when satisfied
- [ ] Download CSV

---

## Troubleshooting

**"I don't see Add enrichment"**  
Look for **+** next to column headers, or search for "enrichment" in the table menu.

**"The script needs an address column"**  
Your Definitive export must include hospital address (street, city, state, zip). Use `--address-column` to specify the column name if it is not auto-detected.

**"Geocoding is slow"**  
The script uses Nominatim (free) which limits requests. For large files, consider using a Mapbox API key (add support in the script if needed).
