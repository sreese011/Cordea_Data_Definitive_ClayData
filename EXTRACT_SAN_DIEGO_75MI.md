# Extract San Diego 75-Mile Hospital HQs + Executives

**Problem:** Definitive Executive Search returns 25,000+ results nationwide. You need only hospitals within 75 miles of San Diego, CA.

**Solution:** Export the full search from Definitive, then run our filter script.

---

## Step 1: Export from Definitive

1. In Definitive, run your **Executive Search** (C-level, hospital HQs, etc.).
2. When you see "Your search returned 25,263 results" (or similar):
   - Click **Export** or **Download**.
   - Choose **CSV**.
   - Save to a location you remember (e.g. `Downloads`).

**Important:** You export the *full unfiltered* list. The geographic filter happens in Step 2.

---

## Step 2: Run the Filter Script

Open PowerShell in the claydata folder and run:

```powershell
cd c:\DEV_Cursor\claydata
.\run_san_diego.ps1 -InputFile "C:\Users\User\Downloads\YOUR_EXPORT_FILENAME.csv"
```

**Replace** `YOUR_EXPORT_FILENAME.csv` with the actual file you exported.

**Or run manually:**

```powershell
python scripts/definitive_pull.py --input "C:\Users\User\Downloads\YOUR_EXPORT.csv" --cities-filter data/cities_san_diego_75mi.txt --output hospitals_san_diego_75mi.csv
```

---

## Step 3: Output

The script writes `hospitals_san_diego_75mi.csv` with only rows where **City** is in the San Diego 75-mile area (e.g. San Diego, Chula Vista, Oceanside, Temecula, etc.).

- Rows like **Falls Church VA**, **Pittsfield MA**, **Leawood KS**, **Santa Rosa CA** → **excluded**
- Rows like **San Diego**, **Chula Vista**, **Oceanside**, **La Jolla** → **kept**

---

## Verification

After running, check the output:

- Row count should drop from ~25,000 to a few hundred (depends on how many HQs are in the San Diego area).
- Spot-check a few rows: City values should all be San Diego area cities.
- If you still see distant cities, check that your Definitive export has a **City** column and that our filter file `data/cities_san_diego_75mi.txt` contains the correct city names.

---

## Cities in the Filter (75 miles of San Diego)

Aliso Viejo, Bonita, Carlsbad, Chula Vista, Coronado, Dana Point, Del Mar, El Cajon, Encinitas, Escondido, Fallbrook, Hemet, Imperial Beach, La Jolla, La Mesa, La Presa, Lake Elsinore, Lake Forest, Laguna Hills, Laguna Niguel, Lemon Grove, Mission Viejo, Murrieta, National City, Oceanside, Perris, Poway, Ramona, Rancho San Diego, Rancho Santa Margarita, San Clemente, San Diego, San Jacinto, San Juan Capistrano, San Marcos, Santee, Solana Beach, Spring Valley, Temecula, Vista
