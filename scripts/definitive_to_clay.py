#!/usr/bin/env python3
"""
Interactive workflow: City → Definitive (ZIP + 100 mi) → Review → Clay.

1. Asks for city (e.g. "San Diego, CA")
2. Resolves city to ZIP code for Definitive geography filter
3. Either:
   - API mode: Pulls report directly from Definitive Reports API (no manual export)
   - Manual mode: Opens Definitive Report Builder; you export, then pick the file
4. Tool shows preview and opens for review
5. Opens Clay for import and enrichment

Usage:
  python scripts/definitive_to_clay.py
  python scripts/definitive_to_clay.py --city "San Diego, CA"
  python scripts/definitive_to_clay.py --api --report-name "My Report"
  python scripts/definitive_to_clay.py --api --report-name "My Report" --output-dir "C:\Reports"
"""

import csv
import io
import os
import platform
import subprocess
import sys
import webbrowser
from datetime import date
from pathlib import Path
from urllib.parse import quote

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Optional: geopy for city → lat/lon, uszipcode for lat/lon → ZIP
try:
    from geopy.geocoders import Nominatim
    GEOPY_AVAILABLE = True
except ImportError:
    GEOPY_AVAILABLE = False

try:
    from uszipcode import SearchEngine
    USZIPCODE_AVAILABLE = True
except ImportError:
    USZIPCODE_AVAILABLE = False


DEFINITIVE_URL = "https://sts.defhc.com"
CLAY_IMPORT_URL = "https://app.clay.com"
RADIUS_MILES = 100
REPORTS_API_BASE = "https://api.defhc.com/v4"


def get_definitive_token(username: str, password: str) -> str | None:
    """Authenticate with Definitive API and return access token."""
    if not REQUESTS_AVAILABLE:
        return None
    try:
        r = requests.post(
            f"{REPORTS_API_BASE}/token",
            data={"grant_type": "password", "username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30,
        )
        r.raise_for_status()
        return r.json().get("access_token")
    except Exception:
        return None


def list_definitive_reports(token: str) -> list[str]:
    """List report names available to the user. Returns list of report names."""
    if not REQUESTS_AVAILABLE:
        return []
    try:
        r = requests.get(
            f"{REPORTS_API_BASE}/Reports",
            headers={"Authorization": f"Bearer {token}"},
            params={"returnType": "csv"},
            timeout=30,
        )
        r.raise_for_status()
        text = r.text.strip()
        if not text:
            return []
        # Response may be CSV with report names, or XML - try to parse as CSV first
        reader = csv.reader(io.StringIO(text))
        rows = list(reader)
        if not rows:
            return []
        # First row may be header; look for report name column
        names = []
        for row in rows[1:] if len(rows) > 1 else rows:
            if row and row[0] and not row[0].lower().startswith("report"):
                names.append(str(row[0]).strip())
        if names:
            return names
        # Fallback: return first column of all rows
        return [str(r[0]).strip() for r in rows if r and str(r[0]).strip()]
    except Exception:
        return []


def download_definitive_report(
    token: str, report_name: str, output_path: Path, page_size: int = 50000
) -> bool:
    """Download a report by name from Definitive API. Returns True on success."""
    if not REQUESTS_AVAILABLE:
        return False
    all_rows = []
    cols = []
    page = 1
    while True:
        try:
            r = requests.get(
                f"{REPORTS_API_BASE}/reports/{quote(report_name)}",
                headers={"Authorization": f"Bearer {token}"},
                params={"page": page, "pageSize": page_size, "returnType": "csv"},
                timeout=120,
            )
            r.raise_for_status()
            text = r.text.strip()
            if not text:
                break
            reader = csv.DictReader(io.StringIO(text))
            rows = list(reader)
            if not rows:
                break
            if not cols:
                cols = reader.fieldnames or []
            all_rows.extend(rows)
            if len(rows) < page_size:
                break
            page += 1
        except Exception:
            return False
    if not all_rows:
        return False
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols or list(all_rows[0].keys()), extrasaction="ignore")
        w.writeheader()
        w.writerows(all_rows)
    return True


def slug_for_filename(text: str) -> str:
    """Sanitize text for use in filenames: lowercase, alphanumeric + underscore."""
    if not text or not str(text).strip():
        return "report"
    s = str(text).strip().lower()
    s = "".join(c if c.isalnum() or c in " -" else "_" for c in s)
    s = "_".join(s.split()).replace("__", "_").strip("_")
    return s[:50] if s else "report"


def report_filename(city: str | None, report_name: str | None) -> str:
    """Build filename: {city_or_report}_{YYYY-MM-DD}.csv"""
    slug = slug_for_filename(city) if city else slug_for_filename(report_name or "report")
    return f"{slug}_{date.today().isoformat()}.csv"


def city_to_zip(city: str) -> str | None:
    """Resolve city (e.g. 'San Diego, CA') to a 5-digit ZIP code."""
    city = (city or "").strip()
    if not city:
        return None

    lat, lon = None, None

    if GEOPY_AVAILABLE:
        try:
            geolocator = Nominatim(user_agent="claydata-definitive-to-clay")
            loc = geolocator.geocode(city + ", USA", timeout=10)
            if loc:
                lat, lon = loc.latitude, loc.longitude
        except Exception:
            pass

    if lat is None or lon is None:
        return None

    if USZIPCODE_AVAILABLE:
        try:
            with SearchEngine() as search:
                results = search.by_coordinates(lat, lon, radius=5, returns=1)
                if results and results[0]:
                    z = str(results[0].zipcode).strip()[:5]
                    if len(z) == 5 and z.isdigit():
                        return z
        except Exception:
            pass

    # Fallback: Nominatim reverse for postcode
    if GEOPY_AVAILABLE:
        try:
            geolocator = Nominatim(user_agent="claydata-definitive-to-clay")
            loc = geolocator.reverse(f"{lat}, {lon}", timeout=10)
            if loc and loc.raw:
                addr = loc.raw.get("address", {}) or {}
                postcode = (addr.get("postcode") or addr.get("zip") or "").strip()
                postcode = postcode.split("-")[0][:5]
                if len(postcode) == 5 and postcode.isdigit():
                    return postcode
        except Exception:
            pass

    return None


def open_file_with_default_app(path: Path) -> None:
    """Open file with OS default application (Excel, etc.)."""
    path = path.resolve()
    if not path.exists():
        print(f"  File not found: {path}", file=sys.stderr)
        return
    try:
        if platform.system() == "Windows":
            os.startfile(str(path))
        elif platform.system() == "Darwin":
            subprocess.run(["open", str(path)], check=False)
        else:
            subprocess.run(["xdg-open", str(path)], check=False)
    except Exception as e:
        print(f"  Could not open file: {e}", file=sys.stderr)


def open_url(url: str) -> None:
    """Open URL in default browser."""
    webbrowser.open(url)


def get_downloads_dir() -> Path:
    """Return user Downloads folder."""
    home = Path.home()
    if platform.system() == "Windows":
        return home / "Downloads"
    return home / "Downloads"


def find_recent_csvs(directory: Path, limit: int = 10) -> list[Path]:
    """Return most recently modified CSV files in directory."""
    if not directory.exists():
        return []
    csvs = list(directory.glob("*.csv"))
    csvs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return csvs[:limit]


def load_csv_preview(path: Path, max_rows: int = 10) -> tuple[list[dict], list[str], int]:
    """Load CSV, return (rows for preview, columns, total row count)."""
    rows = []
    cols = []
    total = 0
    with open(path, newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        cols = reader.fieldnames or []
        for row in reader:
            total += 1
            if len(rows) < max_rows:
                rows.append(row)
    return rows, cols, total


def main():
    try:
        from dotenv import load_dotenv
        load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    except ImportError:
        pass

    # Parse args
    use_api = "--api" in sys.argv
    report_name = None
    if "--report-name" in sys.argv:
        idx = sys.argv.index("--report-name")
        if idx + 1 < len(sys.argv):
            report_name = sys.argv[idx + 1]
    output_dir = os.environ.get("REPORT_SAVE_FOLDER", "").strip()
    if "--output-dir" in sys.argv:
        idx = sys.argv.index("--output-dir")
        if idx + 1 < len(sys.argv):
            output_dir = sys.argv[idx + 1]
    if not output_dir:
        output_dir = str(Path(__file__).resolve().parent.parent / "Contact Lists")
    output_dir = Path(output_dir)
    city = None
    if "--city" in sys.argv:
        idx = sys.argv.index("--city")
        if idx + 1 < len(sys.argv):
            city = sys.argv[idx + 1]

    print("\n=== Definitive → Clay Workflow ===\n")

    csv_path = None

    # API mode: pull report directly from Definitive
    if use_api and REQUESTS_AVAILABLE:
        user = os.environ.get("DEFINITIVE_USERNAME", "").strip()
        pw = os.environ.get("DEFINITIVE_PASSWORD", "").strip()
        if not user or not pw:
            print("API mode requires DEFINITIVE_USERNAME and DEFINITIVE_PASSWORD in .env")
            print("Falling back to manual export flow.\n")
        else:
            token = get_definitive_token(user, pw)
            if not token:
                print("Definitive API auth failed. Check credentials. Falling back to manual export.\n")
            else:
                if not report_name:
                    names = list_definitive_reports(token)
                    if names:
                        print("Available reports:")
                        for i, n in enumerate(names[:20], 1):
                            print(f"  {i}. {n}")
                        try:
                            pick = input("\nEnter number (or report name): ").strip()
                            if pick.isdigit() and 1 <= int(pick) <= len(names):
                                report_name = names[int(pick) - 1]
                            else:
                                report_name = pick or (names[0] if names else None)
                        except EOFError:
                            report_name = names[0] if names else None
                    else:
                        report_name = input("Enter report name (exact name from Report Builder): ").strip()
                if report_name:
                    output_dir.mkdir(parents=True, exist_ok=True)
                    out_file = output_dir / report_filename(city, report_name)
                    print(f"Downloading report '{report_name}'...")
                    if download_definitive_report(token, report_name, out_file):
                        csv_path = out_file.resolve()
                        _, _, total = load_csv_preview(csv_path, 5)
                        print(f"Downloaded {total} rows to {csv_path}\n")
                    else:
                        print("Download failed. Falling back to manual export.\n")

    # Manual mode or API failed: need city, ZIP, and manual export
    if csv_path is None:
        if not city:
            try:
                city = input("Enter city (e.g. San Diego, CA): ").strip()
            except EOFError:
                print("No input. Run with --city \"San Diego, CA\" for non-interactive use.")
                sys.exit(1)
        if not city:
            print("City is required.")
            sys.exit(1)

        print(f"\nCity: {city}")
        print("Resolving city to ZIP code...")
        zip_code = city_to_zip(city)
        if not zip_code:
            print("Could not resolve city to ZIP. Enter ZIP manually:")
            try:
                zip_code = input("ZIP code: ").strip()[:5]
            except EOFError:
                zip_code = ""
            if len(zip_code) != 5 or not zip_code.isdigit():
                print("Invalid ZIP. Exiting.")
                sys.exit(1)

        print(f"ZIP code: {zip_code}")
        print(f"Radius: {RADIUS_MILES} miles\n")

        print("STEP 1: Export from Definitive Report Builder")
        print("-" * 50)
        print("Use Report Builder (not table view) - table view cannot be exported.")
        print(f"1. Open: {DEFINITIVE_URL}")
        print("2. Go to Report Builder and create/open your report.")
        print("3. In Geography filter: ZIP =", zip_code, "| Radius =", RADIUS_MILES, "miles")
        print("4. Save the report, then Export/Download as CSV.")
        print("-" * 50)

        open_url(DEFINITIVE_URL)

        print("\nSTEP 2: Choose your export file")
        print("-" * 50)
        downloads = get_downloads_dir()
        recent = find_recent_csvs(downloads, 5)
        if recent:
            for i, p in enumerate(recent, 1):
                print(f"  {i}. {p.name}")
        try:
            file_input = input("\nEnter path or number 1-5 (or Enter for first recent): ").strip()
        except EOFError:
            file_input = "1" if recent else ""
        if file_input.isdigit() and 1 <= int(file_input) <= len(recent):
            csv_path = recent[int(file_input) - 1]
        elif file_input:
            csv_path = Path(file_input).expanduser().resolve()
            if not csv_path.exists():
                csv_path = (downloads / file_input).resolve()
        elif recent:
            csv_path = recent[0]
        if not csv_path or not csv_path.exists():
            print("No valid file. Exiting.")
            sys.exit(1)

    # 5. Preview and review
    print("\nSTEP 3: Review the list")
    print("-" * 50)

    rows, cols, total = load_csv_preview(csv_path, 10)
    print(f"Total rows: {total}")
    print(f"Columns: {', '.join(cols[:8])}{'...' if len(cols) > 8 else ''}\n")
    if rows:
        print("First few rows (sample):")
        for i, r in enumerate(rows[:3], 1):
            preview = {k: str(v)[:30] for k, v in list(r.items())[:4]}
            print(f"  {i}. {preview}")

    try:
        open_for_review = input("\nOpen file for review/edit? (y/n, default y): ").strip().lower()
        if open_for_review != "n":
            open_file_with_default_app(csv_path)
            input("Press Enter when done reviewing/editing...")
    except EOFError:
        pass

    # 6. Clay import
    print("\nSTEP 4: Import to Clay for enrichment")
    print("-" * 50)
    print("1. Opening Clay...")
    print("2. Create New table → Import → Upload your file.")
    print(f"3. Use this file: {csv_path}")
    print("4. Add contact enrichment (email, phone) - test on 5 rows first!")
    print("-" * 50)

    open_url(CLAY_IMPORT_URL)

    print("\nDone! Your file is ready to import into Clay.")
    print(f"Path: {csv_path}\n")


if __name__ == "__main__":
    main()
