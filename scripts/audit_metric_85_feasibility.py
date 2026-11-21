"""Audit whether a common classification threshold can meet an 0.85 metric gate.

This is a diagnostic audit, not model selection.  It deliberately operates on
the already-evaluated locked-test predictions and therefore MUST NOT be used to
choose the deployed threshold or to replace the preregistered locked result.
Its purpose is to prevent an impossible multi-metric target from encouraging
test-set tuning or selective reporting.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "results" / "authentic_locked" / "authentic_locked_site_predictions_and_zones.csv"
OUTPUT = ROOT / "results" / "authentic_locked" / "metric_85_feasibility_audit.json"
TARGET = 0.85


def threshold_metrics(y: np.ndarray, probability: np.ndarray, threshold: float) -> dict[str, float]:
    prediction = probability >= threshold
    return {
        "accuracy": float(accuracy_score(y, prediction)),
        "balanced_accuracy": float(balanced_accuracy_score(y, prediction)),
        "f1": float(f1_score(y, prediction, zero_division=0)),
        "precision": float(precision_score(y, prediction, zero_division=0)),
        "sensitivity": float(recall_score(y, prediction, zero_division=0)),
    }


def main() -> None:
    frame = pd.read_csv(INPUT)
    y = frame["high_500"].astype(int).to_numpy()
    probability = frame["probability_xgboost"].astype(float).to_numpy()
    rows = []
    for threshold in np.linspace(0.0, 1.0, 1001):
        metrics = threshold_metrics(y, probability, float(threshold))
        rows.append({
            "threshold": float(threshold),
            **metrics,
            "minimum_core_metric": min(metrics.values()),
        })

    core = ["accuracy", "balanced_accuracy", "f1", "precision", "sensitivity"]
    best_f1 = max(rows, key=lambda row: row["f1"])
    best_balanced = max(rows, key=lambda row: row["balanced_accuracy"])
    best_worst_case = max(rows, key=lambda row: row["minimum_core_metric"])
    feasible = [row for row in rows if all(row[name] >= TARGET for name in core)]
    report = {
        "status": "DIAGNOSTIC_ONLY_TEST_LABELS_ALREADY_SEEN",
        "target": TARGET,
        "model": "preregistered authentic-locked XGBoost probabilities",
        "records": int(len(frame)),
        "threshold_independent_roc_auc": float(roc_auc_score(y, probability)),
        "all_core_metrics_at_or_above_target_is_feasible": bool(feasible),
        "number_of_feasible_thresholds": len(feasible),
        "core_metrics": core,
        "oracle_best_f1": best_f1,
        "oracle_best_balanced_accuracy": best_balanced,
        "oracle_maximin_threshold": best_worst_case,
        "interpretation": (
            "No value in this file may replace the validation-selected threshold. "
            "The oracle rows quantify the separability limit of the existing locked scores."
        ),
    }
    OUTPUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
