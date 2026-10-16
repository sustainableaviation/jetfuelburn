# %%
"""
Builds the airport table used by `jetfuelburn.utility.geography`.

Source: `airports.csv` from OurAirports (public domain, https://ourairports.com/data/),
downloaded from the OurAirports download repository on GitHub,
https://github.com/davidmegginson/ourairports-data, at a pinned commit.
Every rebuild from the same commit writes the same table.

Output: `src/jetfuelburn/data/Airports/airports.csv.gz` with the five columns
`iata, icao, airport, latitude, longitude`.

Usage: `python processing/ourairports/ourairports.py` (standard library only).

To update the data:
1. set `COMMIT` and `SHA256` to a newer commit of the repository and the SHA-256 of its `airports.csv`,
2. run the script,
3. update the commit and date in `src/jetfuelburn/data/Airports/__init__.py`,
   the counts in the comments below and the expected values in `tests/test_geography.py`.
"""

import csv
import gzip
import hashlib
import io
import pathlib
import urllib.request
from collections import Counter

# ourairports-data commit of 2026-10-05
COMMIT = "660b39168c35e6f74f8c63836cbff0268b19c5a9"
SHA256 = "1baffe51282f40a192490ff27654309dd9252e9dafd7a179f69b2f4fa96a75af"
URL = f"https://raw.githubusercontent.com/davidmegginson/ourairports-data/{COMMIT}/airports.csv"

# this script lives in processing/ourairports/, two folders below the repository root
ROOT = pathlib.Path(__file__).resolve().parents[2]
TARGET = ROOT / "src" / "jetfuelburn" / "data" / "Airports" / "airports.csv.gz"

# %%
with urllib.request.urlopen(URL, timeout=60) as response:
    raw = response.read()
if hashlib.sha256(raw).hexdigest() != SHA256:
    raise SystemExit(f"airports.csv at {COMMIT[:7]} has an unexpected SHA-256")
rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8"), newline="")))

# Keep every open airport with an IATA or an ICAO code. All airport types stay in:
# heliports and seaplane bases also carry scheduled services (Air Greenland
# heliports, seaplane bases in Alaska and British Columbia).
airports = [
    r
    for r in rows
    if r["type"] != "closed"  # safety net: OurAirports clears codes of closed airports
    and (r["iata_code"] or r["icao_code"])
    # drop the two placeholder rows that carry codes:
    # "(Bogus)Jezero Crater" (country "ZZ") and "[Duplicate] Beijing Xijiao Airport"
    and r["iso_country"] != "ZZ"
    and not r["name"].startswith(("[Duplicate]", "(Duplicate)"))
]

# Each IATA code and each ICAO code must point to exactly one airport.
for column in ("iata_code", "icao_code"):
    counts = Counter(r[column] for r in airports if r[column])
    repeated = sorted(code for code, n in counts.items() if n > 1)
    if repeated:
        raise SystemExit(f"repeated {column}: {repeated}")

# Names are written with single spaces (12 names contain double spaces at the pinned commit),
# so that lookups by name work with the usual spelling.
for r in airports:
    r["name"] = " ".join(r["name"].split())

# %%
# Some airports share a name (60 names at the pinned commit). geography.py keeps
# the last row it reads for a name, so the rows are sorted by name and, within a
# name, the preferred airport comes last. Preference goes to scheduled service,
# then to the larger airport type, then to the row with both codes.
SIZE = {
    "balloonport": 0,
    "heliport": 1,
    "seaplane_base": 2,
    "small_airport": 3,
    "medium_airport": 4,
    "large_airport": 5,
}


def sort_key(r):
    return (
        r["name"],
        r["scheduled_service"] == "yes",
        SIZE.get(r["type"], 0),
        bool(r["iata_code"] and r["icao_code"]),
        r["icao_code"],  # the codes settle any remaining tie
        r["iata_code"],
    )


def degrees(value):
    # 6 decimals (about 0.1 m) also remove float noise such as 15-digit values
    return f"{float(value):.6f}".rstrip("0").rstrip(".")


# All rows are converted first, so a malformed value stops the script before the target is touched.
table = [["iata", "icao", "airport", "latitude", "longitude"]] + [
    [
        r["iata_code"],
        r["icao_code"],
        r["name"],
        degrees(r["latitude_deg"]),
        degrees(r["longitude_deg"]),
    ]
    for r in sorted(airports, key=sort_key)
]

# mtime=0 keeps the gzip header free of timestamps, so the same commit gives the same file
gz = gzip.GzipFile(TARGET, "wb", mtime=0)
with io.TextIOWrapper(gz, "utf-8", newline="") as file:
    csv.writer(file).writerows(table)

print(f"{len(airports)} airports written to {TARGET.relative_to(ROOT)}")
