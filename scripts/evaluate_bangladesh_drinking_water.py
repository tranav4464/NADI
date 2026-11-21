"""District-held-out MICS endpoint benchmark; no network or temporal claims."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, average_precision_score, brier_score_loss, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from nadi.microbial_risk.bangladesh import binary_ecoli


# Household attributes known before the biological result. No WQ result, derived
# e_coli label, source-water assay, or sample collection outcome is a feature.
FEATURES = (
    "HH6", "HH7", "HC3", "HC17", "WS1", "WS3", "WS7", "WS9",
    "WS11", "WS14", "WS15", "HW1", "windex10", "HHAGE",
)
NUMERIC = ("HC3", "HHAGE")


def _scores(y: np.ndarray, p: np.ndarray, threshold: float) -> dict:
    prediction = p >= threshold
    tn, fp, fn, tp = confusion_matrix(y, prediction, labels=[0, 1]).ravel()
    return {
        "n": len(y), "prevalence": float(y.mean()), "threshold": threshold,
        "accuracy": float(accuracy_score(y, prediction)),
        "precision": float(precision_score(y, prediction, zero_division=0)),
        "recall": float(recall_score(y, prediction, zero_division=0)),
        "positive_f1": float(f1_score(y, prediction, zero_division=0)),
        "roc_auc": float(roc_auc_score(y, p)),
        "average_precision": float(average_precision_score(y, p)),
        "brier": float(brier_score_loss(y, p)),
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
    }


def _threshold(y: np.ndarray, p: np.ndarray) -> float:
    grid = np.linspace(0.05, 0.95, 181)
    return float(max(grid, key=lambda t: (f1_score(y, p >= t), -t)))


def _estimator(kind: str, categorical: list[str]) -> Pipeline:
    preprocess = ColumnTransformer([
        ("cat", Pipeline([("impute", SimpleImputer(strategy="most_frequent")),
                           ("onehot", OneHotEncoder(handle_unknown="ignore"))]), categorical),
        ("num", SimpleImputer(strategy="median"), list(NUMERIC)),
    ])
    model = LogisticRegression(max_iter=1500) if kind == "logistic" else RandomForestClassifier(
        n_estimators=250, min_samples_leaf=10, n_jobs=-1, random_state=20261118
    )
    return Pipeline([("preprocess", preprocess), ("model", model)])


def run(path: Path) -> dict:
    raw, metadata = pyreadstat.read_sav(str(path))
    # Hold entire districts out, preventing an area's household records from
    # appearing in both model fitting and final evaluation.
    groups = raw["HH7A"].astype(str)
    split = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=20261118)
    train_cal_index, test_index = next(split.split(raw, groups=groups))
    splitter = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=20261119)
    train_local, cal_local = next(splitter.split(raw.iloc[train_cal_index], groups=groups.iloc[train_cal_index]))
    partitions = {
        "train": train_cal_index[train_local],
        "calibration": train_cal_index[cal_local],
        "test": test_index,
    }
    assert all(not (set(groups.iloc[partitions[a]]) & set(groups.iloc[partitions[b]]))
               for a, b in (("train", "calibration"), ("train", "test"), ("calibration", "test")))
    report = {
        "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest().upper(),
        "rows": metadata.number_rows,
        "split": "district-held-out 60/20/20 approximately; fixed seeds; calibration chooses model and threshold",
        "feature_columns": list(FEATURES),
        "excluded_from_features": ["WQ26", "WQ27", "WQ29", "e_coli", "ecoli", "HH7A"],
        "districts_by_partition": {name: sorted(set(groups.iloc[index])) for name, index in partitions.items()},
        "endpoints": {},
        "claim_boundary": "Bangladesh cross-sectional household/source water only; no Delhi, pipeline, or forecast validation.",
    }
    x = raw.loc[:, FEATURES].copy()
    categorical = [name for name in FEATURES if name not in NUMERIC]
    for name in categorical:
        x[name] = x[name].astype("string").fillna("MISSING").astype(str)
    for name in NUMERIC:
        x[name] = pd.to_numeric(x[name], errors="coerce")
    for endpoint, column in (("source", "WQ27"), ("household", "WQ26")):
        labels = np.array([binary_ecoli(value) for value in raw[column]], dtype=object)
        valid = np.array([value is not None for value in labels])
        indices = {name: index[valid[index]] for name, index in partitions.items()}
        y = {name: np.asarray(labels[index], dtype=int) for name, index in indices.items()}
        candidates = {}
        for kind in ("logistic", "random_forest"):
            model = _estimator(kind, categorical)
            model.fit(x.iloc[indices["train"]], y["train"])
            cal_p = model.predict_proba(x.iloc[indices["calibration"]])[:, 1]
            t = _threshold(y["calibration"], cal_p)
            candidates[kind] = {"calibration": _scores(y["calibration"], cal_p, t), "model": model}
        selected = max(candidates, key=lambda name: candidates[name]["calibration"]["positive_f1"])
        threshold = candidates[selected]["calibration"]["threshold"]
        test_p = candidates[selected]["model"].predict_proba(x.iloc[indices["test"]])[:, 1]
        report["endpoints"][endpoint] = {
            "label_column": column,
            "valid_rows_by_partition": {name: len(index) for name, index in indices.items()},
            "calibration_candidates": {name: value["calibration"] for name, value in candidates.items()},
            "selected_model": selected,
            "untouched_district_test": _scores(y["test"], test_p, threshold),
            "test_always_negative": _scores(y["test"], np.zeros(len(y["test"])), 0.5),
            "test_always_positive": _scores(y["test"], np.ones(len(y["test"])), 0.5),
        }
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("results/bangladesh_district_heldout.json"))
    args = parser.parse_args()
    result = run(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for endpoint, value in result["endpoints"].items():
        print(endpoint, value["selected_model"], value["untouched_district_test"])


if __name__ == "__main__":
    main()
