"""Download a bounded, authentic Environment Agency E. coli sample.

The API contains observed surface-water laboratory measurements, not drinking-
water network telemetry.  This script deliberately preserves that domain
boundary and writes immutable raw CSV plus provenance/checksum metadata.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests


API = "https://environment.data.gov.uk/water-quality/data/observation"
DETERMINAND = "2348"  # Escherichia coli : Confirmed : MF
POLYGON = {"type": "Polygon", "coordinates": [[[-6, 49], [2, 49], [2, 56], [-6, 56], [-6, 49]]]}
HEADERS = {
    "Accept": "text/csv",
    "CSV-Header": "present",
    "API-Version": "1",
    "Content-Type": "application/json",
    "User-Agent": "NADI-authentic-data-replication/1.0",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def fetch_period(start: str, end: str, out: Path, limit: int = 2500) -> int:
    out.parent.mkdir(parents=True, exist_ok=True)
    chunks: list[bytes] = []
    offset = 0
    while True:
        params = {
            "skip": offset,
            "limit": limit,
            "dateFrom": start,
            "dateTo": end,
            "determinand": DETERMINAND,
        }
        response = requests.post(API, params=params, headers=HEADERS, json=POLYGON, timeout=90)
        response.raise_for_status()
        if not response.content.strip():
            break
        text = response.content
        if not chunks:
            chunks.append(text)
        else:
            # Drop the repeated CSV header from subsequent pages.
            lines = text.splitlines(keepends=True)
            chunks.append(b"".join(lines[1:]))
        if len(text.splitlines()) <= 1 or len(text.splitlines()) - 1 < limit:
            break
        offset += limit
        time.sleep(0.2)
    out.write_bytes(b"".join(chunks))
    return max(0, sum(max(0, len(c.splitlines()) - 1) for c in chunks))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default="2024-01-01")
    parser.add_argument("--end", default="2024-12-31")
    parser.add_argument(
        "--out",
        default="../nadi_resources/datasets/EA_ECOLI_AUTHENTIC/ea_ecoli_confirmed_mf_2024.csv",
    )
    args = parser.parse_args()
    out = Path(args.out).resolve()
    fetch_period(args.start, args.end, out)
    # Count parsed CSV records rather than physical lines: the API may return
    # quoted fields containing newlines, so line-counting can under-report.
    with out.open("r", encoding="utf-8", newline="") as handle:
        count = max(0, sum(1 for _ in csv.reader(handle)) - 1)
    metadata = {
        "dataset_id": "EA_ECOLI_AUTHENTIC",
        "source_url": API,
        "source_licence": "UK Open Government Licence v3.0 (verify current terms)",
        "determinand_notation": DETERMINAND,
        "determinand_label": "Escherichia coli : Confirmed : MF",
        "date_from": args.start,
        "date_to": args.end,
        "geography": "England bounding polygon (-6,49)-(2,56)",
        "records": count,
        "data_origin": "AUTHENTIC_OBSERVED",
        "domain": "surface_water_laboratory_observations",
        "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
        "sha256": sha256(out),
        "caveat": "Not drinking-water distribution telemetry; not a Delhi-NCR validation set.",
    }
    out.with_suffix(".json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
