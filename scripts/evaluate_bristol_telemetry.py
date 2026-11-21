"""Audit Bristol POU operational telemetry without inventing biological labels.

The dataset has no E. coli/event ground truth. This script therefore reports
coverage, missingness, cadence and a chronological unsupervised operational
anomaly score; it deliberately does not report accuracy or microbial F1.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler

from nadi.telemetry.normal import fit_local_normals

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / "nadi_resources" / "datasets" / "Bristol_POU_Telemetry" / "extracted" / "data" / "pou-dwts_operationaltelemetrydata_uk_nov2019-sep2022_1.csv"
OUT = ROOT / "results" / "bristol_telemetry_audit_v1.json"
FEATURES = ["Flow_Rate", "Discharge_Pressure", "TMP", "ORP", "FAC", "Filtration_Flux", "UF_ MP"]


def _robust_score(frame: pd.DataFrame, train: pd.DataFrame) -> np.ndarray:
    med = train[FEATURES].median()
    mad = (train[FEATURES] - med).abs().median().replace(0, np.nan)
    z = ((frame[FEATURES] - med).abs() / (1.4826 * mad)).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    missing = frame[FEATURES].isna().sum(axis=1).to_numpy(dtype=float)
    return z.max(axis=1).to_numpy(dtype=float) + 0.25 * missing


def main() -> dict:
    raw = SOURCE.read_bytes()
    df = pd.read_csv(SOURCE)
    # The source uses day/month/year; preserve the raw text and make UTC-naive
    # ordering explicit for the operational audit.
    df["timestamp"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    df = df.sort_values("timestamp", kind="mergesort").reset_index(drop=True)
    # Hour-of-day is an operational regime proxy for this dataset, which does
    # not expose a hydraulic node identifier. Fit regimes on training data
    # only; this is not a biological label and is never used as one.
    df["operating_hour"] = df["timestamp"].dt.hour.astype("Int64")
    train_end = int(len(df) * 0.60)
    cal_end = int(len(df) * 0.80)
    train, calibration, test = df.iloc[:train_end], df.iloc[train_end:cal_end], df.iloc[cal_end:]
    score_train = _robust_score(train, train)
    score_cal = _robust_score(calibration, train)
    score_test = _robust_score(test, train)
    threshold = float(np.quantile(score_cal, 0.995))
    local_model = fit_local_normals(train, FEATURES, group_column="operating_hour", min_group_count=20)
    local_cal = local_model.transform(calibration[FEATURES + ["operating_hour"]])
    local_test = local_model.transform(test[FEATURES + ["operating_hour"]])
    local_cal_score = local_cal.abs().max(axis=1, skipna=True).fillna(0.0).to_numpy()
    local_test_score = local_test.abs().max(axis=1, skipna=True).fillna(0.0).to_numpy()
    local_threshold = float(np.quantile(local_cal_score, 0.995))
    # An independent unsupervised comparator; no labels are inferred from it.
    iso = Pipeline([
        ("impute", SimpleImputer(strategy="median", add_indicator=True)),
        ("scale", RobustScaler()),
        ("model", IsolationForest(n_estimators=200, contamination="auto", random_state=20261117)),
    ])
    iso.fit(train[FEATURES])
    iso_cal = -iso.decision_function(calibration[FEATURES])
    iso_test = -iso.decision_function(test[FEATURES])
    iso_threshold = float(np.quantile(iso_cal, 0.995))
    gaps = df["timestamp"].diff().dt.total_seconds().dropna() / 60.0
    report = {
        "protocol_id": "BRISTOL-POU-OPERATIONAL-AUDIT-V1",
        "source_sha256": hashlib.sha256(raw).hexdigest().upper(),
        "rows": int(len(df)),
        "columns": FEATURES,
        "time_range": [str(df["timestamp"].min()), str(df["timestamp"].max())],
        "partition": {"train": train_end, "calibration": cal_end - train_end, "test": len(test)},
        "missing_fraction_by_feature": {c: float(df[c].isna().mean()) for c in FEATURES},
        "cadence_minutes": {
            "median": float(gaps.median()), "p05": float(gaps.quantile(.05)),
            "p95": float(gaps.quantile(.95)), "duplicate_or_nonpositive_fraction": float((gaps <= 0).mean()),
        },
        "robust_distance": {
            "calibration_threshold_q995": threshold,
            "test_flag_rate": float((score_test >= threshold).mean()),
            "test_flag_count": int((score_test >= threshold).sum()),
        },
        "location_adaptive_normalisation": {
            "group": "operating_hour",
            "training_only": True,
            "calibration_threshold_q995": local_threshold,
            "test_flag_rate": float((local_test_score >= local_threshold).mean()),
            "test_flag_count": int((local_test_score >= local_threshold).sum()),
            "claim_boundary": "Regime-adaptive operational anomaly evidence only; no E. coli label or accuracy/F1 claim.",
        },
        "isolation_forest": {
            "calibration_threshold_q995": iso_threshold,
            "test_flag_rate": float((iso_test >= iso_threshold).mean()),
            "test_flag_count": int((iso_test >= iso_threshold).sum()),
        },
        "claim_boundary": "Operational telemetry audit and unsupervised anomaly evidence only; no E. coli labels, no accuracy/F1 claim, no hydraulic-network validation.",
        "next_use": "Use anomaly scores only as typed proxy evidence after sensor-health and domain-support gating.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    main()
