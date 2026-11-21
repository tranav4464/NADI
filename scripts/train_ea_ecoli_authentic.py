"""Train a small, leakage-safe baseline on authentic EA E. coli observations.

This is a surface-water laboratory replication track.  It is not a drinking
network model and deliberately defines detection from the laboratory result
qualifier rather than inventing a sensor label.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import accuracy_score, average_precision_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT.parent / "nadi_resources" / "datasets" / "EA_ECOLI_AUTHENTIC" / "ea_ecoli_confirmed_mf_2024.csv"
OUT = ROOT / "results" / "ea_ecoli_authentic_baseline_v1.json"


def main() -> None:
    df = pd.read_csv(RAW, dtype=str)
    t = pd.to_datetime(df["phenomenonTime"], utc=True)
    numeric = pd.to_numeric(df["result"].str.replace(",", "", regex=False), errors="coerce")
    # A leading '<' is the laboratory non-detect qualifier; all other numeric
    # confirmed results are detections for this explicitly defined endpoint.
    y = (~df["result"].str.strip().str.startswith("<")) & numeric.notna()
    d = pd.DataFrame(
        {
            "month": t.dt.month,
            "day_of_year": t.dt.dayofyear,
            "hour": t.dt.hour,
            "easting_km": pd.to_numeric(df["samplingPoint.easting"], errors="coerce") / 1000.0,
            "northing_km": pd.to_numeric(df["samplingPoint.northing"], errors="coerce") / 1000.0,
        }
    ).dropna()
    keep = d.index
    d = d.loc[keep]
    y = y.loc[keep].astype(int)
    order = t.loc[keep].sort_values().index
    cut = int(len(order) * 0.8)
    train_idx, test_idx = order[:cut], order[cut:]
    models = {
        "logistic": make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, class_weight="balanced")),
        "hist_gradient_boosting": HistGradientBoostingClassifier(max_iter=180, learning_rate=0.06, max_leaf_nodes=15, random_state=20261118),
    }
    scores = {}
    for name, model in models.items():
        model.fit(d.loc[train_idx], y.loc[train_idx])
        p = model.predict_proba(d.loc[test_idx])[:, 1]
        pred = (p >= 0.5).astype(int)
        scores[name] = {
            "accuracy": float(accuracy_score(y.loc[test_idx], pred)),
            "precision": float(precision_score(y.loc[test_idx], pred, zero_division=0)),
            "recall": float(recall_score(y.loc[test_idx], pred, zero_division=0)),
            "f1": float(f1_score(y.loc[test_idx], pred, zero_division=0)),
            "roc_auc": float(roc_auc_score(y.loc[test_idx], p)) if len(np.unique(y.loc[test_idx])) > 1 else None,
            "average_precision": float(average_precision_score(y.loc[test_idx], p)),
        }
    result = {
        "dataset": "EA_ECOLI_AUTHENTIC",
        "data_origin": "AUTHENTIC_OBSERVED",
        "domain": "surface_water_laboratory_observations",
        "endpoint": "confirmed_numeric_E_coli_detection_vs_lab_non_detect_qualifier",
        "records": int(len(d)),
        "positive_prevalence": float(y.mean()),
        "temporal_split": {"train_fraction": 0.8, "test_fraction": 0.2, "ordered_by": "phenomenonTime"},
        "models": scores,
        "limitations": [
            "No drinking-water network telemetry or E. coli paired sensor stream.",
            "Features are time and sampling coordinates only; this is a reproducibility baseline, not causal inference.",
            "Do not transfer this threshold or metric to Delhi-NCR without local labels.",
        ],
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
