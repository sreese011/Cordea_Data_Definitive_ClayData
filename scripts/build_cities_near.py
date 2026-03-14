#!/usr/bin/env python3
"""
Build a list of cities within a radius of a center point (e.g., San Diego).

Uses uszipcode to get all ZIP codes in the radius, extracts unique city names,
and writes them to a text file. Use this file with --cities-filter in definitive_pull.py
to filter Definitive exports by city (faster and more reliable than per-row geocoding).

Usage:
  python scripts/build_cities_near.py --lat 32.7157 --lon -117.1611 --radius 75 --output cities_san_diego_75mi.txt
"""

import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Build list of cities within radius of a center point."
    )
    parser.add_argument("--lat", type=float, required=True, help="Center latitude")
    parser.add_argument("--lon", type=float, required=True, help="Center longitude")
    parser.add_argument("--radius", type=float, default=75, help="Radius in miles (default: 75)")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("cities_within_radius.txt"),
        help="Output text file (one city per line)",
    )
    args = parser.parse_args()

    try:
        from uszipcode import SearchEngine
    except ImportError:
        print("ERROR: Install uszipcode: pip install uszipcode", file=sys.stderr)
        raise SystemExit(1)

    cities = set()
    with SearchEngine() as search:
        # returns=2000 to get all zips within 75 miles (San Diego area has ~200+ zips)
        zips = search.by_coordinates(args.lat, args.lon, radius=args.radius, returns=2000)
        for z in zips:
            if z.major_city and str(z.major_city).strip():
                cities.add(str(z.major_city).strip())
            # Some zips have common_city_list (multiple cities)
            if hasattr(z, "common_city_list") and z.common_city_list:
                for c in z.common_city_list:
                    if c and str(c).strip():
                        cities.add(str(c).strip())

    cities_sorted = sorted(cities)
    args.output.write_text("\n".join(cities_sorted), encoding="utf-8")
    print(f"Wrote {len(cities_sorted)} cities to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
