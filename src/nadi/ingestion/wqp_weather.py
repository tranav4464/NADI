from __future__ import annotations

import gzip
import json
import math
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

from ..paths import INTERIM_ROOT, RESOURCE_ROOT
from ..provenance import sha256

WQP_ZIP = RESOURCE_ROOT / "datasets" / "WQP_Marion_IN_Ecoli_2003_2022" / "wqp_marion_in_ecoli_2003_2022.zip"
NOAA_GZ = RESOURCE_ROOT / "datasets" / "NOAA_Indianapolis_GHCND" / "USW00093819.csv.gz"


def _load_wqp() -> pd.DataFrame:
    with zipfile.ZipFile(WQP_ZIP) as archive:
        with archive.open("result.csv") as handle:
            data = pd.read_csv(handle, low_memory=False)
    data["date"] = pd.to_datetime(data["ActivityStartDate"], errors="coerce")
    data["ecoli_count"] = pd.to_numeric(data["ResultMeasureValue"], errors="coerce")
    unit = data["ResultMeasure/MeasureUnitCode"].fillna("").str.lower()
    valid_unit = unit.isin(["mpn/100ml", "cfu/100ml"])
    data = data.loc[valid_unit & data["date"].notna() & data["ecoli_count"].notna() & (data["ecoli_count"] >= 0)].copy()
    data["site_id"] = data["MonitoringLocationIdentifier"].astype(str)
    data["log_ecoli"] = np.log1p(data["ecoli_count"])
    return data[["date", "site_id", "ecoli_count", "log_ecoli", "ResultDetectionConditionText", "ProviderName"]]


def _load_noaa() -> pd.DataFrame:
    names = ["station", "date", "element", "value", "mflag", "qflag", "sflag", "obs_time"]
    with gzip.open(NOAA_GZ, "rt", encoding="utf-8") as handle:
        long = pd.read_csv(handle, header=None, names=names, dtype={"date": str})
    long = long[long["element"].isin(["PRCP", "TMAX", "TMIN", "TAVG"])].copy()
    long["date"] = pd.to_datetime(long["date"], format="%Y%m%d", errors="coerce")
    long.loc[long["qflag"].fillna("").astype(str).str.len() > 0, "value"] = np.nan
    wide = long.pivot_table(index="date", columns="element", values="value", aggfunc="first").sort_index()
    for name in ["PRCP", "TMAX", "TMIN", "TAVG"]:
        if name not in wide:
            wide[name] = np.nan
    # GHCN-D values are tenths of mm or degrees Celsius.
    wide[["PRCP", "TMAX", "TMIN", "TAVG"]] = wide[["PRCP", "TMAX", "TMIN", "TAVG"]] / 10.0
    wide["TAVG"] = wide["TAVG"].fillna((wide["TMAX"] + wide["TMIN"]) / 2.0)
    wide["PRCP"] = wide["PRCP"].fillna(0.0)
    for window in [1, 3, 10, 15]:
        # shift(1) makes these forecast-safe at the start of the target day.
        wide[f"prcp_prev_{window}d"] = wide["PRCP"].shift(1).rolling(window, min_periods=1).sum()
        wide[f"tavg_prev_{window}d"] = wide["TAVG"].shift(1).rolling(window, min_periods=1).mean()
    wide["prcp_same_day"] = wide["PRCP"]
    wide["tavg_same_day"] = wide["TAVG"]
    return wide.reset_index()


def prepare(threshold: float = 1000.0) -> dict:
    wqp = _load_wqp()
    weather = _load_noaa()
    merged = wqp.merge(weather, on="date", how="left", validate="many_to_one")
    merged["elevated_ecoli"] = (merged["ecoli_count"] >= threshold).astype(int)
    month = merged["date"].dt.month
    merged["month_sin"] = np.sin(2 * np.pi * month / 12.0)
    merged["month_cos"] = np.cos(2 * np.pi * month / 12.0)
    merged = merged.sort_values(["date", "site_id", "ecoli_count"]).reset_index(drop=True)
    target = INTERIM_ROOT / "wqp_marion_weather.csv"
    merged.to_csv(target, index=False, lineterminator="\n")
    summary = {
        "schema_version": "0.1.0",
        "rows": int(len(merged)),
        "sites": int(merged["site_id"].nunique()),
        "date_min": str(merged["date"].min().date()),
        "date_max": str(merged["date"].max().date()),
        "endpoint": f"E. coli count >= {threshold:g} per 100 mL; non-regulatory surface-water context endpoint",
        "positive_rate": float(merged["elevated_ecoli"].mean()),
        "missing_weather_fraction": float(merged["TAVG"].isna().mean()),
        "raw_hashes": {"wqp": sha256(WQP_ZIP), "noaa": sha256(NOAA_GZ)},
        "processed_sha256": sha256(target),
        "evidence_boundary": "LAB_CONFIRMED surface-water E. coli joined to OBSERVED weather by date; not drinking-network field validation",
    }
    (INTERIM_ROOT / "wqp_marion_weather_card.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary

