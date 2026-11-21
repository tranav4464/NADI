"""Download official historical weather for authentic EA sample locations.

Open-Meteo is used exactly as in the Open E. coli prior-art description. The
weather rows are joined by sampling location and UTC calendar date; no future
weather is used for a sample.
"""
from __future__ import annotations

import hashlib
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT.parent / "nadi_resources" / "datasets" / "EA_ECOLI_AUTHENTIC"
PANEL = DATA / "ea_ecoli_physchem_panel_q1_2024.csv"
OUT = DATA / "ea_openmeteo_weather_panel_q1_2024.csv"
META = DATA / "ea_openmeteo_weather_panel_q1_2024.json"
API = "https://archive-api.open-meteo.com/v1/archive"
TRANSFORM = Transformer.from_crs("EPSG:27700", "EPSG:4326", always_xy=True)


def fetch(site: str, easting: float, northing: float) -> tuple[str, pd.DataFrame, str]:
    lon, lat = TRANSFORM.transform(easting, northing)
    params = {"latitude": round(lat, 5), "longitude": round(lon, 5), "start_date": "2024-01-01", "end_date": "2024-03-31", "daily": "temperature_2m_mean,precipitation_sum,relative_humidity_2m_mean", "timezone": "UTC"}
    r = requests.get(API, params=params, timeout=60)
    r.raise_for_status()
    obj = r.json()
    daily = obj.get("daily", {})
    frame = pd.DataFrame(daily)
    if frame.empty:
        return site, frame, r.url
    frame["date"] = pd.to_datetime(frame["time"], utc=True).dt.date.astype(str)
    frame["samplingPoint.notation"] = site
    frame["latitude"] = lat
    frame["longitude"] = lon
    return site, frame.drop(columns=["time"]), r.url


def main() -> None:
    df = pd.read_csv(PANEL, dtype=str)
    coords = df[["samplingPoint.notation", "samplingPoint.easting", "samplingPoint.northing"]].drop_duplicates().dropna()
    results, urls, errors = [], [], []
    with ThreadPoolExecutor(max_workers=8) as pool:
        jobs = {pool.submit(fetch, r["samplingPoint.notation"], float(r["samplingPoint.easting"]), float(r["samplingPoint.northing"])): r["samplingPoint.notation"] for _, r in coords.iterrows()}
        for job in as_completed(jobs):
            try:
                site, frame, url = job.result()
                if not frame.empty: results.append(frame)
                urls.append(url)
            except Exception as exc:
                errors.append({"site": jobs[job], "error": f"{type(exc).__name__}: {exc}"})
    weather = pd.concat(results, ignore_index=True) if results else pd.DataFrame()
    weather.to_csv(OUT, index=False)
    h = hashlib.sha256(OUT.read_bytes()).hexdigest().upper()
    meta = {"dataset_id": "EA_OPENMETEO_WEATHER_PANEL_Q1_2024", "data_origin": "AUTHENTIC_OBSERVED", "source": API, "records": int(len(weather)), "sites_requested": int(len(coords)), "sites_returned": int(weather["samplingPoint.notation"].nunique()) if not weather.empty else 0, "errors": errors, "join_keys": ["samplingPoint.notation", "UTC calendar date"], "coordinate_crs": "EPSG:27700 to EPSG:4326", "sha256": h, "downloaded_at_utc": datetime.now(timezone.utc).isoformat(), "claim_boundary": "Observed weather covariates for England surface-water samples; not drinking-network or E. coli truth."}
    META.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
