#!/usr/bin/env python3
"""
Definitive Healthcare hospital + executive pull with 75-mile geo filter.

Supports two modes:
  1. API mode: Pull from Definitive API (requires API credentials)
  2. CSV mode: Filter an existing CSV from Definitive web export

Output: CSV ready for Clay import, filtered to hospitals within 75 miles.
"""

import argparse
import csv
import json
import math
import os
import sys
from pathlib import Path

# Optional: geopy for geocoding. Use Nominatim (free, no key) by default.
try:
    from geopy.geocoders import Nominatim
    from geopy.extra.rate_limiter import RateLimiter
    GEOPY_AVAILABLE = True
except ImportError:
    GEOPY_AVAILABLE = False

# Optional: requests for API calls
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


# Earth radius in miles for Haversine formula
EARTH_RADIUS_MILES = 3958.8


def haversine_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in miles between two lat/long points."""
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    return EARTH_RADIUS_MILES * c


def geocode_address(address: str, geolocator) -> tuple[float | None, float | None]:
    """Return (lat, lon) for an address, or (None, None) on failure."""
    if not address or not address.strip():
        return None, None
    try:
        loc = geolocator.geocode(address.strip(), timeout=10)
        if loc:
            return loc.latitude, loc.longitude
    except Exception:
        pass
    return None, None


def geocode_mapbox(address: str, token: str) -> tuple[float | None, float | None]:
    """Geocode via Mapbox API. Returns (lat, lon) or (None, None). More reliable for US addresses."""
    if not address or not address.strip() or not token:
        return None, None
    try:
        from urllib.parse import quote
        url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{quote(address.strip())}.json?access_token={token}&limit=1"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        features = data.get("features", [])
        if features and features[0].get("geometry"):
            coords = features[0]["geometry"]["coordinates"]  # [lon, lat]
            return coords[1], coords[0]
    except Exception:
        pass
    return None, None


def get_definitive_token(username: str, password: str) -> str | None:
    """Authenticate with Definitive API and return access token."""
    if not REQUESTS_AVAILABLE:
        print("ERROR: Install requests: pip install requests", file=sys.stderr)
        return None
    url = "https://api.defhc.com/v4/token"
    data = {
        "grant_type": "password",
        "username": username,
        "password": password,
    }
    try:
        r = requests.post(url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"}, timeout=30)
        r.raise_for_status()
        tok = r.json().get("access_token")
        return tok
    except Exception as e:
        print(f"ERROR: Definitive auth failed: {e}", file=sys.stderr)
        return None


def pull_hospitals_from_api(token: str, max_records: int = 1000) -> list[dict]:
    """Pull hospitals with executives from Definitive OData API."""
    if not REQUESTS_AVAILABLE:
        return []
    url = "https://api.defhc.com/v4/odata-v4/Hospitals?$expand=Executives"
    # Request more records; OData often limits to ~100 per page
    if max_records:
        url += f"&$top={min(max_records, 5000)}"
    records = []
    try:
        r = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=60)
        r.raise_for_status()
        data = r.json()
        rows = data.get("value", data) if isinstance(data, dict) else data
        if isinstance(rows, list):
            records = rows
        else:
            records = [rows] if rows else []
    except Exception as e:
        print(f"ERROR: API pull failed: {e}", file=sys.stderr)
    return records


def flatten_hospital_rows(api_records: list[dict]) -> list[dict]:
    """Convert API records to flat rows (one per executive per hospital, or one per hospital if no execs)."""
    rows = []
    for rec in api_records:
        hosp_name = rec.get("HospitalName") or rec.get("Name") or rec.get("name") or ""
        addr = (
            rec.get("Address1") or rec.get("Address") or ""
        )
        city = rec.get("City") or ""
        state = rec.get("State") or ""
        zip_code = rec.get("Zip") or rec.get("ZipCode") or ""
        full_addr = ", ".join(filter(None, [addr, city, state, zip_code]))
        base = {
            "hospital_name": hosp_name,
            "hospital_address": full_addr,
            "hospital_city": city,
            "hospital_state": state,
            "hospital_zip": zip_code,
        }
        execs = rec.get("Executives") or rec.get("executives")
        if isinstance(execs, list) and execs:
            for ex in execs:
                row = {**base, "executive_name": ex.get("Name") or ex.get("FullName") or "",
                       "executive_title": ex.get("Title") or ex.get("JobTitle") or ""}
                rows.append(row)
        else:
            rows.append({**base, "executive_name": "", "executive_title": ""})
    return rows


def load_csv_rows(path: Path) -> tuple[list[dict], list[str]]:
    """Load CSV and return (list of dicts, column names)."""
    rows = []
    cols = []
    with open(path, newline="", encoding="utf-8-sig", errors="replace") as f:
        reader = csv.DictReader(f)
        cols = reader.fieldnames or []
        for r in reader:
            rows.append(dict(r))
    return rows, cols


def infer_address_columns(cols: list[str]) -> str | None:
    """Return the best column name for address, or None."""
    lower_cols = [c.lower() for c in cols]
    for cand in ["address", "hospital_address", "address1", "full_address", "street", "location"]:
        for i, lc in enumerate(lower_cols):
            if cand in lc:
                return cols[i]
    # Try combined
    if "city" in lower_cols and "state" in lower_cols:
        return None  # Caller can build from parts
    return None


def _find_col_value(row: dict, cols: list[str], candidates: list[str]) -> str:
    """Get value from row using case-insensitive column match."""
    lower_cols = {c.lower(): c for c in cols}
    for cand in candidates:
        if cand.lower() in lower_cols:
            key = lower_cols[cand.lower()]
            val = row.get(key)
            if val and str(val).strip():
                return str(val).strip()
    return ""


def build_address_from_row(row: dict, cols: list[str]) -> str:
    """Build an address string from row using common column names (case-insensitive)."""
    parts = []
    # Street/full address
    addr = _find_col_value(row, cols, ["address", "address1", "street", "hospital_address", "address_line_1", "full_address"])
    if addr:
        parts.append(addr)
    # City (Definitive export uses "City")
    city = _find_col_value(row, cols, ["city", "hospital_city", "City"])
    if city:
        parts.append(city)
    # State (Definitive export uses "State")
    state = _find_col_value(row, cols, ["state", "hospital_state", "st", "State"])
    if state:
        parts.append(state)
    # ZIP
    zip_ = _find_col_value(row, cols, ["zip", "zipcode", "zip_code", "hospital_zip", "postal_code"])
    if zip_:
        parts.append(zip_)
    return ", ".join(parts) if parts else ""


def filter_by_distance(
    rows: list[dict],
    center_lat: float,
    center_lon: float,
    radius_miles: float,
    address_key: str | None,
    build_address_fn,
    mapbox_token: str | None = None,
) -> tuple[list[dict], int, int]:
    """Filter rows to those within radius_miles. EXCLUDES rows we cannot verify (failed geocode or no address).
    Returns (filtered_rows, kept_count, excluded_count)."""
    use_mapbox = mapbox_token and REQUESTS_AVAILABLE
    if use_mapbox:
        pass  # Use Mapbox
    elif not GEOPY_AVAILABLE:
        print("WARNING: geopy not installed. Install with: pip install geopy", file=sys.stderr)
        print("Skipping distance filter.", file=sys.stderr)
        return rows, len(rows), 0
    else:
        geolocator = Nominatim(user_agent="claydata-definitive-pull")
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1.1)
    if use_mapbox:
        print("  Using Mapbox for geocoding (more reliable for US addresses)", file=sys.stderr)
    out = []
    excluded_no_addr = 0
    excluded_geocode_fail = 0
    excluded_too_far = 0
    for i, row in enumerate(rows):
        addr = row.get(address_key or "") if address_key else ""
        if not addr:
            addr = build_address_fn(row)
        if not addr or not str(addr).strip():
            excluded_no_addr += 1
            continue
        if use_mapbox:
            lat, lon = geocode_mapbox(addr, mapbox_token)
        else:
            lat, lon = geocode_address(addr, geocode)
        if lat is None:
            excluded_geocode_fail += 1
            continue
        dist = haversine_miles(center_lat, center_lon, lat, lon)
        row2 = {**row, "distance_miles": f"{dist:.2f}", "lat": str(lat), "lon": str(lon)}
        if dist <= radius_miles:
            out.append(row2)
        else:
            excluded_too_far += 1
        if (i + 1) % 50 == 0:
            print(f"  Geocoded {i + 1} / {len(rows)} rows...", file=sys.stderr)
    excluded = excluded_no_addr + excluded_geocode_fail + excluded_too_far
    if excluded_geocode_fail > 0 or excluded_no_addr > 0:
        print(f"  Excluded: {excluded_no_addr} (no address), {excluded_geocode_fail} (geocode failed), {excluded_too_far} (outside radius)", file=sys.stderr)
    return out, len(out), excluded


def _load_filter_file(path: Path) -> tuple[set[str], set[str]]:
    """Load filter file (one entry per line). Returns (cities_set_lower, zips_set_normalized).
    Entries that are all digits (5 or 9) are treated as ZIPs; others as city names."""
    text = path.read_text(encoding="utf-8")
    cities = set()
    zips = set()
    for line in text.splitlines():
        val = line.strip()
        if not val:
            continue
        if val.replace("-", "").replace(" ", "").isdigit():
            # Normalize ZIP: first 5 digits (strip +4 if present)
            z = val.replace(" ", "").replace("-", "")[:5]
            if len(z) == 5:
                zips.add(z)
        else:
            cities.add(val.lower())
    return cities, zips


def _find_col(row: dict, cols: list[str], candidates: list[str]) -> tuple[str | None, str]:
    """Return (column_key, value) for first matching column. Used for city/zip lookup."""
    lower_cols = {c.lower(): c for c in cols}
    for cand in candidates:
        if cand.lower() in lower_cols:
            key = lower_cols[cand.lower()]
            val = row.get(key)
            if val is not None and str(val).strip():
                return key, str(val).strip()
    return None, ""


def filter_by_cities(
    rows: list[dict],
    cities_file: Path,
    city_col: str | None,
    zip_col: str | None,
    cols: list[str],
) -> tuple[list[dict], int]:
    """Filter rows to those whose City OR ZIP is in the filter file.
    File format: one city name or ZIP code per line. 5-digit entries = ZIPs.
    Returns (filtered_rows, excluded_count)."""
    cities_set, zips_set = _load_filter_file(cities_file)
    lower_cols = {c.lower(): c for c in cols}
    city_key = city_col if city_col and city_col in cols else None
    if not city_key:
        for cand in ["city", "hospital_city", "City"]:
            if cand.lower() in lower_cols:
                city_key = lower_cols[cand.lower()]
                break
    zip_key = zip_col if zip_col and zip_col in cols else None
    if not zip_key:
        for cand in ["zip", "zipcode", "zip_code", "ZIP", "postal_code", "hospital_zip"]:
            if cand.lower() in lower_cols:
                zip_key = lower_cols[cand.lower()]
                break
    if not city_key and not zip_key:
        print("WARNING: No City or ZIP column found. Cannot filter.", file=sys.stderr)
        return rows, 0
    out = []
    for row in rows:
        city_val = row.get(city_key or "") if city_key else ""
        zip_val = row.get(zip_key or "") if zip_key else ""
        city_match = city_val and str(city_val).strip().lower() in cities_set
        zip_normalized = str(zip_val).replace(" ", "").replace("-", "")[:5] if zip_val else ""
        zip_match = len(zip_normalized) == 5 and zip_normalized in zips_set
        if city_match or zip_match:
            out.append(row)
    excluded = len(rows) - len(out)
    return out, excluded


def write_csv(rows: list[dict], path: Path):
    """Write rows to CSV."""
    if not rows:
        print("WARNING: No rows to write.", file=sys.stderr)
        return
    all_keys = set()
    for r in rows:
        all_keys.update(r.keys())
    cols = sorted(all_keys)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def main():
    try:
        from dotenv import load_dotenv
        load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    except ImportError:
        pass
    mapbox_token = os.environ.get("MAPBOX_ACCESS_TOKEN", "").strip() or None
    parser = argparse.ArgumentParser(
        description="Pull hospitals + executives from Definitive, filter by 75 miles, output CSV for Clay."
    )
    parser.add_argument(
        "--mode",
        choices=["api", "csv"],
        default="csv",
        help="api = pull from Definitive API; csv = read from a file you exported",
    )
    parser.add_argument(
        "--input",
        type=Path,
        help="Input CSV path (for csv mode). Required in csv mode.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("hospitals_within_75_miles.csv"),
        help="Output CSV path",
    )
    parser.add_argument(
        "--cities-filter",
        type=Path,
        help="Path to cities list (one per line). When set, filters by city instead of geocoding. Generate with build_cities_near.py",
    )
    parser.add_argument(
        "--city-column",
        type=str,
        help="Column name for city (auto-detected if omitted). Used with --cities-filter.",
    )
    parser.add_argument(
        "--zip-column",
        type=str,
        help="Column name for ZIP code (auto-detected if omitted). Filter file may include ZIPs.",
    )
    parser.add_argument(
        "--lat",
        type=float,
        help="Center latitude (required unless --cities-filter is used)",
    )
    parser.add_argument(
        "--lon",
        type=float,
        help="Center longitude (required unless --cities-filter is used)",
    )
    parser.add_argument(
        "--radius",
        type=float,
        default=75,
        help="Radius in miles (default: 75)",
    )
    parser.add_argument(
        "--address-column",
        type=str,
        help="Column name containing hospital address (auto-detected if omitted)",
    )
    # API mode
    parser.add_argument("--definitive-user", type=str, help="Definitive API username")
    parser.add_argument("--definitive-password", type=str, help="Definitive API password")
    parser.add_argument("--max-records", type=int, default=500, help="Max API records (api mode)")
    args = parser.parse_args()

    if not args.cities_filter and (args.lat is None or args.lon is None):
        print("ERROR: Provide --lat and --lon, or use --cities-filter with a cities list file.", file=sys.stderr)
        sys.exit(1)
    if args.cities_filter and not args.cities_filter.exists():
        print(f"ERROR: Cities filter file not found: {args.cities_filter}", file=sys.stderr)
        sys.exit(1)

    # Load .env for MAPBOX_ACCESS_TOKEN (optional, improves geocoding)
    try:
        from dotenv import load_dotenv
        load_dotenv(Path(__file__).parent.parent / ".env")
    except ImportError:
        pass

    mapbox_token = os.environ.get("MAPBOX_ACCESS_TOKEN", "").strip() or None

    addr_col = None
    if args.mode == "api":
        user = args.definitive_user or os.environ.get("DEFINITIVE_USERNAME")
        pw = args.definitive_password or os.environ.get("DEFINITIVE_PASSWORD")
        if not user or not pw:
            print("ERROR: In api mode, set DEFINITIVE_USERNAME and DEFINITIVE_PASSWORD env vars or use --definitive-user/--definitive-password", file=sys.stderr)
            sys.exit(1)
        token = get_definitive_token(user, pw)
        if not token:
            sys.exit(1)
        print("Pulling from Definitive API...", file=sys.stderr)
        api_rows = pull_hospitals_from_api(token, args.max_records)
        rows = flatten_hospital_rows(api_rows)
        if not rows:
            print("No records from API. Check credentials and API access.", file=sys.stderr)
            sys.exit(1)
        cols = list(rows[0].keys()) if rows else []
        def build_addr(r):
            return r.get("hospital_address") or r.get("hospital_city") or ""
    else:
        if not args.input or not args.input.exists():
            print("ERROR: In csv mode, --input path is required and must exist.", file=sys.stderr)
            sys.exit(1)
        rows, cols = load_csv_rows(args.input)
        addr_col = args.address_column or infer_address_columns(cols)
        def build_addr(r):
            return build_address_from_row(r, cols)

    addr_key = args.address_column or ("hospital_address" if args.mode == "api" else addr_col)
    try:
        from dotenv import load_dotenv
        load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    except ImportError:
        pass
    mapbox_token = os.environ.get("MAPBOX_ACCESS_TOKEN", "").strip() or None

    if args.cities_filter:
        if not args.cities_filter.exists():
            print(f"ERROR: Cities filter file not found: {args.cities_filter}", file=sys.stderr)
            sys.exit(1)
        print(f"Loaded {len(rows)} rows. Filtering by city/ZIP list ({args.cities_filter})...", file=sys.stderr)
        filtered, excluded = filter_by_cities(rows, args.cities_filter, args.city_column, getattr(args, "zip_column", None), cols)
        print(f"  Kept {len(filtered)} rows, excluded {excluded} (city/ZIP not in filter)", file=sys.stderr)
    else:
        if args.lat is None or args.lon is None:
            print("ERROR: Either --cities-filter or both --lat and --lon are required.", file=sys.stderr)
            sys.exit(1)
        print(f"Loaded {len(rows)} rows. Filtering by {args.radius} miles from ({args.lat}, {args.lon})...", file=sys.stderr)
        filtered, kept, excluded = filter_by_distance(
            rows,
            args.lat,
            args.lon,
            args.radius,
            addr_key,
            build_addr,
            mapbox_token=mapbox_token,
        )
        if excluded > 0:
            print(f"  Excluded {excluded} rows", file=sys.stderr)

    write_csv(filtered, args.output)
    print(f"Wrote {len(filtered)} rows to {args.output}", file=sys.stderr)
    if len(filtered) == 0 and excluded > 0 and not args.cities_filter:
        print("TIP: If many rows were excluded due to geocode failure, add MAPBOX_ACCESS_TOKEN to .env for better results.", file=sys.stderr)


if __name__ == "__main__":
    main()
