# Definitive Healthcare: Export Hospital HQ + C-Level Executives

How to export **hospital headquarters only** with **executives at those HQ locations**—not regional branches or regional executives.

**Important:** Use **Report Builder** to create and export reports. Table view cannot be exported.

---

## Requirement

- **Hospital headquarters (HQ)** – primary/corporate locations only
- **Executives at HQ** – C-level (CEO, CFO, COO, etc.) based at headquarters
- **Not included:** Regional facilities, branch offices, outpatient centers, satellite locations, or executives at those regional locations

---

## How to Get HQ-Only Data in Definitive

Definitive Healthcare structures data by facility and health system hierarchy. Use these filters to get HQ-only:

### 1. Facility Type / Role

Look for filters such as:

- **Headquarters** or **HQ** – if Definitive has this as a facility attribute
- **Primary facility** – main system location
- **Parent organization** – the health system or hospital system HQ
- **Exclude:** Branch, satellite, affiliate, regional, outpatient (if you want HQ only)

### 2. Health System Hierarchy

- Use **HospitalView** or **Health System** search
- Filter by **parent/child** or **system component** – select **parent** or **primary** only
- Avoid “child” or “affiliate” facilities unless they are also HQ

### 3. Executive Affiliation

- When adding executives, ensure they are linked to the **headquarters address**, not regional offices
- Use **executive search** but restrict by **location type** or **facility role** if Definitive offers these options

### 4. Ask Definitive Support

If filters are unclear:

- Contact your Definitive account manager or support
- Request: *“Export of hospital headquarters only, with C-level executives based at those HQ locations—no regional facilities or regional executives.”*
- They may have saved reports or filters tuned for this use case

---

## Export Checklist

- [ ] Filter to **headquarters** / **primary** / **parent** facilities only
- [ ] Confirm executives are **HQ-based**, not regional
- [ ] Include **HQ address** (street, city, state, zip)
- [ ] Export as **CSV**

---

## After Export

Run the geo-filter script with your center point (e.g. San Diego):

```powershell
python scripts/definitive_pull.py --input "your_export.csv" --lat 32.7157 --lon -117.1611 --radius 75 --output hospitals_hq_san_diego_75mi.csv
```

Then import the output CSV into Clay for contact enrichment.
