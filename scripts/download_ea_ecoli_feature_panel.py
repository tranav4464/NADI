"""Build an authentic EA E. coli + physicochemical sample panel.

All rows come from the official observation API.  Joins use the sample URI,
never nearest timestamps, so the feature panel is auditable at sample level.
"""
from __future__ import annotations

import hashlib
import io
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

API = "https://environment.data.gov.uk/water-quality/data/observation"
POLYGON = {"type": "Polygon", "coordinates": [[[-6, 49], [2, 49], [2, 56], [-6, 56], [-6, 49]]]}
HEADERS = {"Accept": "text/csv", "CSV-Header": "present", "API-Version": "1", "Content-Type": "application/json", "User-Agent": "NADI-authentic-panel/1.0"}
DETERMINANDS = {
    "ecoli_2348": "2348",
    "ph_0061": "0061",
    "temperature_0076": "0076",
    "conductivity_0077": "0077",
}
ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT.parent / "nadi_resources" / "datasets" / "EA_ECOLI_AUTHENTIC"


def get_all(det: str, start: str, end: str) -> pd.DataFrame:
    pages = []
    offset = 0
    while True:
        p = {"skip": offset, "limit": 2500, "dateFrom": start, "dateTo": end, "determinand": det}
        r = requests.post(API, params=p, headers=HEADERS, json=POLYGON, timeout=90)
        r.raise_for_status()
        if not r.content.strip():
            break
        page = pd.read_csv(io.BytesIO(r.content), dtype=str)
        if page.empty:
            break
        pages.append(page)
        if len(page) < 2500:
            break
        offset += 2500
        time.sleep(0.2)
    return pd.concat(pages, ignore_index=True) if pages else pd.DataFrame()


def sample_id(uri: str) -> str:
    m = re.search(r"/sample/([^/]+)/", str(uri))
    return m.group(1) if m else ""


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    start, end = "2024-01-01", "2024-03-31"
    raw = {}
    for name, det in DETERMINANDS.items():
        df = get_all(det, start, end)
        path = OUT_DIR / f"{name}_q1_2024.csv"
        df.to_csv(path, index=False)
        raw[name] = {"determinand": det, "records": int(len(df)), "sha256": sha256(path)}
    eco = pd.read_csv(OUT_DIR / "ecoli_2348_q1_2024.csv", dtype=str)
    eco["sample_id"] = eco["id"].map(sample_id)
    eco["ecoli_result_raw"] = eco["result"]
    eco["ecoli_detected"] = (~eco["result"].str.strip().str.startswith("<")).astype(int)
    base = eco[["sample_id", "id", "samplingPoint.notation", "samplingPoint.prefLabel", "phenomenonTime", "samplingPoint.easting", "samplingPoint.northing", "ecoli_result_raw", "ecoli_detected"]].drop_duplicates("sample_id")
    for name in list(DETERMINANDS)[1:]:
        df = pd.read_csv(OUT_DIR / f"{name}_q1_2024.csv", dtype=str)
        df["sample_id"] = df["id"].map(sample_id)
        df["value"] = pd.to_numeric(df["result"].str.replace(",", "", regex=False), errors="coerce")
        feature = df.dropna(subset=["value"]).groupby("sample_id", as_index=False)["value"].first().rename(columns={"value": name})
        base = base.merge(feature, on="sample_id", how="left")
    panel = base
    panel_path = OUT_DIR / "ea_ecoli_physchem_panel_q1_2024.csv"
    panel.to_csv(panel_path, index=False)
    metadata = {"dataset_id": "EA_ECOLI_AUTHENTIC_PHYSCHEM_PANEL", "data_origin": "AUTHENTIC_OBSERVED", "domain": "England_surface_water_laboratory_samples", "date_from": start, "date_to": end, "join_key": "sample_id parsed from official observation URI", "records_ecoli": int(len(eco)), "records_panel": int(len(panel)), "feature_columns": list(DETERMINANDS)[1:], "raw_files": raw, "panel_sha256": sha256(panel_path), "downloaded_at_utc": datetime.now(timezone.utc).isoformat(), "caveat": "Not drinking-water network telemetry and not Delhi-NCR validation."}
    (OUT_DIR / "ea_ecoli_physchem_panel_q1_2024.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
