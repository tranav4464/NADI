"""Reproduce chronological drinking-water event detection baselines on GECCO."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, average_precision_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler


def _read(path: Path, features: list[str]) -> tuple[pd.DataFrame, np.ndarray]:
    frame = pd.read_csv(path, parse_dates=["Time"])
    if not frame["Time"].is_monotonic_increasing:
        raise ValueError(f"Nonmonotonic GECCO time: {path}")
    return frame[features], frame["Event"].astype(bool).to_numpy()


def _threshold(y: np.ndarray, score: np.ndarray) -> float:
    grid = np.unique(np.quantile(score, np.linspace(0.001, 0.999, 500)))
    return float(max(grid, key=lambda t: (f1_score(y, score >= t, zero_division=0), t)))


def _metrics(y: np.ndarray, score: np.ndarray, threshold: float) -> dict:
    pred = score >= threshold
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[False, True]).ravel()
    # A true event is a contiguous run of marked minutes. This event-level
    # recall complements point F1 and prevents one long event dominating.
    starts = np.flatnonzero(y & ~np.r_[False, y[:-1]])
    event_detected = 0
    for start in starts:
        next_negative = np.flatnonzero(~y[start:])
        end = start + int(next_negative[0]) if len(next_negative) else len(y)
        event_detected += bool(pred[start:end].any())
    return {
        "rows": len(y), "positive_rows": int(y.sum()), "prevalence": float(y.mean()),
        "threshold": threshold, "accuracy": float(accuracy_score(y, pred)),
        "precision": float(precision_score(y, pred, zero_division=0)),
        "recall": float(recall_score(y, pred, zero_division=0)),
        "positive_f1": float(f1_score(y, pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y, score)),
        "average_precision": float(average_precision_score(y, score)),
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
        "true_event_runs": len(starts), "event_runs_with_any_alert": event_detected,
        "event_recall": event_detected / len(starts) if len(starts) else None,
    }


def run(directory: Path, protocol: dict) -> dict:
    paths = {
        "train": directory / "gecco2019_train_water_quality.csv",
        "validation": directory / "gecco2019_valid_water_qulity.csv",
        "test": directory / "gecco2019_test_water_quality.csv",
    }
    data = {name: _read(path, protocol["features"]) for name, path in paths.items()}
    x_train, y_train = data["train"]
    x_val, y_val = data["validation"]
    x_test, y_test = data["test"]
    imputer = SimpleImputer(strategy="median")
    scaler = RobustScaler()
    normal = scaler.fit_transform(imputer.fit_transform(x_train.loc[~y_train]))
    val = scaler.transform(imputer.transform(x_val))
    test = scaler.transform(imputer.transform(x_test))
    median = np.median(normal, axis=0)
    mad = np.median(np.abs(normal - median), axis=0)
    distance = lambda z: np.max(np.abs(z - median) / np.maximum(mad, 1e-4), axis=1)
    rng = np.random.default_rng(20261118)
    subset = rng.choice(len(normal), size=min(40000, len(normal)), replace=False)
    iso = IsolationForest(n_estimators=150, max_samples=512, contamination="auto", random_state=20261118, n_jobs=-1)
    iso.fit(normal[subset])
    supervised = Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("model", RandomForestClassifier(n_estimators=180, min_samples_leaf=3,
                                          class_weight="balanced_subsample", random_state=20261118, n_jobs=-1)),
    ])
    supervised.fit(x_train, y_train)
    scores = {
        "robust_distance": (distance(val), distance(test)),
        "isolation_forest": (-iso.score_samples(val), -iso.score_samples(test)),
        "random_forest": (supervised.predict_proba(x_val)[:, 1], supervised.predict_proba(x_test)[:, 1]),
    }
    calibration = {}
    for name in protocol["models"]:
        val_score, _ = scores[name]
        t = _threshold(y_val, val_score)
        calibration[name] = _metrics(y_val, val_score, t)
    selected = max(protocol["models"], key=lambda name: calibration[name]["positive_f1"])
    test_score = scores[selected][1]
    test_result = _metrics(y_test, test_score, calibration[selected]["threshold"])
    return {
        "protocol": protocol,
        "files_sha256": {name: hashlib.sha256(path.read_bytes()).hexdigest().upper() for name, path in paths.items()},
        "calibration": calibration,
        "selected_model": selected,
        "untouched_test": test_result,
        "always_negative_test_accuracy": float((~y_test).mean()),
        "claim_boundary": protocol["claim_boundary"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=Path("configs/gecco_event_v1.json"))
    parser.add_argument("--output", type=Path, default=Path("results/gecco_event_v1.json"))
    args = parser.parse_args()
    result = run(args.directory, json.loads(args.config.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"selected_model": result["selected_model"], "test": result["untouched_test"]}, indent=2))


if __name__ == "__main__":
    main()
