"""Six-family reconstruction of the 2024 ISEF urban-stream weather method."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier, GradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, average_precision_score, brier_score_loss, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier

from nadi.ingestion.wqp_weather import _load_noaa
from nadi.microbial_risk.weather_model import expected_calibration_error
from nadi.paths import INTERIM_ROOT


def _score(y: np.ndarray, p: np.ndarray, threshold: float) -> dict:
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
        "ece_10": expected_calibration_error(y, p),
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
    }


def _threshold(y: np.ndarray, p: np.ndarray) -> float:
    grid = np.unique(np.r_[np.linspace(0.01, 0.99, 99), np.quantile(p, np.linspace(0.01, 0.99, 99))])
    return float(max(grid, key=lambda t: (f1_score(y, p >= t, zero_division=0), t)))


def _models() -> dict[str, Pipeline]:
    seed = 20261118
    return {
        "logistic_regression": Pipeline([
            ("impute", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
            ("model", LogisticRegression(max_iter=2000, random_state=seed)),
        ]),
        "random_forest": Pipeline([
            ("impute", SimpleImputer(strategy="median")),
            ("model", RandomForestClassifier(n_estimators=180, min_samples_leaf=8,
                                              random_state=seed, n_jobs=-1)),
        ]),
        "extra_trees": Pipeline([
            ("impute", SimpleImputer(strategy="median")),
            ("model", ExtraTreesClassifier(n_estimators=180, min_samples_leaf=8,
                                           random_state=seed, n_jobs=-1)),
        ]),
        "decision_tree": Pipeline([
            ("impute", SimpleImputer(strategy="median")),
            ("model", DecisionTreeClassifier(max_depth=6, min_samples_leaf=20,
                                             random_state=seed)),
        ]),
        "gradient_boosting": Pipeline([
            ("impute", SimpleImputer(strategy="median")),
            ("model", GradientBoostingClassifier(n_estimators=120, learning_rate=0.05,
                                                  max_depth=3, random_state=seed)),
        ]),
        "xgb_classifier": Pipeline([
            ("impute", SimpleImputer(strategy="median")),
            ("model", XGBClassifier(n_estimators=160, learning_rate=0.05, max_depth=3,
                                    subsample=0.9, colsample_bytree=0.9, eval_metric="logloss",
                                    random_state=seed, n_jobs=2)),
        ]),
    }


def run(config: dict) -> dict:
    sample_path = INTERIM_ROOT / "wqp_marion_weather.csv"
    sample = pd.read_csv(sample_path, parse_dates=["date"])
    weather = _load_noaa().sort_values("date").copy()
    for days in (10, 15):
        weather[f"prcp_max_prev_{days}d"] = weather["PRCP"].shift(1).rolling(days, min_periods=1).max()
        weather[f"cdd10_prev_{days}d"] = (weather["TAVG"] - 10.0).clip(lower=0).shift(1).rolling(days, min_periods=1).sum()
    derived = weather[["date", "prcp_max_prev_10d", "prcp_max_prev_15d",
                       "cdd10_prev_10d", "cdd10_prev_15d"]]
    data = sample.merge(derived, on="date", how="left", validate="many_to_one")
    features = config["features"]
    data = data.dropna(subset=features).copy()
    train = data[data.date <= config["train_end"]]
    calibration = data[(data.date > config["train_end"]) & (data.date <= config["validation_end"])]
    test = data[(data.date > config["validation_end"]) & (data.date <= config["test_end"])]
    if min(len(train), len(calibration), len(test)) == 0:
        raise ValueError("Empty reconstruction split")
    if train.date.max() >= calibration.date.min() or calibration.date.max() >= test.date.min():
        raise ValueError("Temporal leakage between partitions")
    y_train = train.elevated_ecoli.to_numpy(dtype=int)
    y_cal = calibration.elevated_ecoli.to_numpy(dtype=int)
    y_test = test.elevated_ecoli.to_numpy(dtype=int)
    model_map = _models()
    validation = {}
    for name in config["model_families"]:
        model = model_map[name]
        model.fit(train[features], y_train)
        probability = model.predict_proba(calibration[features])[:, 1]
        threshold = _threshold(y_cal, probability)
        validation[name] = _score(y_cal, probability, threshold)
    chosen = max(config["model_families"], key=lambda name: validation[name]["positive_f1"])
    p_test = model_map[chosen].predict_proba(test[features])[:, 1]
    report = {
        "protocol": config,
        "source_sha256": hashlib.sha256(sample_path.read_bytes()).hexdigest().upper(),
        "split_rows": {"train": len(train), "calibration": len(calibration), "test": len(test)},
        "split_positive_counts": {"train": int(y_train.sum()), "calibration": int(y_cal.sum()), "test": int(y_test.sum())},
        "validation_model_comparison": validation,
        "selected_model": chosen,
        "test_of_selected_model": _score(y_test, p_test, validation[chosen]["threshold"]),
        "test_always_negative_accuracy": float((y_test == 0).mean()),
        "claim_boundary": config["claim_boundary"],
    }
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("configs/isef_weather_reconstruction_v1.json"))
    parser.add_argument("--output", type=Path, default=Path("results/isef_weather_reconstruction_v1.json"))
    args = parser.parse_args()
    report = run(json.loads(args.config.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"selected": report["selected_model"], "test": report["test_of_selected_model"]}, indent=2))


if __name__ == "__main__":
    main()
