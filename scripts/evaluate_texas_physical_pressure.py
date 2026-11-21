"""Leak/no-leak pressure-wave audit on a real controlled pipe-network dataset.

This is deliberately a *hydraulic-only* validation track. Labels describe
controlled physical leak conditions encoded by the experiment files, not
E. coli, sewage intrusion, or consumer exposure.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, average_precision_score, balanced_accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from nadi.hydraulics.pressure_features import pressure_wave_features  # noqa: E402

DATA = ROOT.parent / "nadi_resources" / "datasets" / "NADI_NETWORK_PRIORITY_2026_11_19" / "texas_physical_pipe_testbed_tbrnp6vrnj" / "dynamic_pressure_extracted" / "Dynamic Pressure Sensor"
OUT = ROOT / "results" / "texas_physical_pressure_v1.json"


def _condition_key(path: Path) -> str:
    return path.stem.replace("_P1", "").replace("_P2", "")


def _rows() -> pd.DataFrame:
    # Sensor P1 is prespecified to avoid treating the paired P1/P2 recordings
    # from a single physical run as independent train and test samples.
    rows = []
    for path in sorted(DATA.rglob("*_P1.csv")):
        waveform = pd.read_csv(path, usecols=["Sample", "Value"])
        samples = waveform["Sample"].to_numpy(dtype=float)
        interval = float(np.median(np.diff(samples)))
        row = pressure_wave_features(waveform["Value"].to_numpy(dtype=float), interval)
        condition = _condition_key(path)
        row.update({
            "file": str(path.relative_to(DATA)),
            "condition_group": condition,
            "configuration": path.parts[-3],
            "leak_type": path.parts[-2],
            "leak_present": int("_NL_" not in condition),
        })
        rows.append(row)
    if not rows:
        raise FileNotFoundError(f"No physical pressure P1 files found under {DATA}")
    return pd.DataFrame(rows)


def _metrics(y: np.ndarray, probability: np.ndarray, threshold: float = 0.5) -> dict[str, float | int]:
    predicted = probability >= threshold
    return {
        "records": int(len(y)), "positive_leak_conditions": int(y.sum()), "prevalence": float(y.mean()),
        "threshold": threshold, "accuracy": float(accuracy_score(y, predicted)),
        "precision": float(precision_score(y, predicted, zero_division=0)),
        "recall": float(recall_score(y, predicted, zero_division=0)),
        "f1": float(f1_score(y, predicted, zero_division=0)),
        "balanced_accuracy": float(balanced_accuracy_score(y, predicted)),
        "roc_auc": float(roc_auc_score(y, probability)),
        "average_precision": float(average_precision_score(y, probability)),
    }


def main() -> dict:
    frame = _rows()
    features = [c for c in frame.columns if c.startswith("pressure_") or c.startswith("spectral_")]
    y = frame["leak_present"].to_numpy(dtype=int)
    probability = np.zeros(len(frame), dtype=float)
    fold_rows = []
    splitter = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=20261119)
    for fold, (train, test) in enumerate(splitter.split(frame[features], y, frame["condition_group"])):
        model = RandomForestClassifier(
            n_estimators=400, class_weight="balanced", random_state=20261119 + fold, n_jobs=1,
        )
        model.fit(frame.loc[train, features], y[train])
        probability[test] = model.predict_proba(frame.loc[test, features])[:, 1]
        fold_rows.append({
            "fold": fold, "train_conditions": int(len(train)), "test_conditions": int(len(test)),
            "test_positive_conditions": int(y[test].sum()),
            "test_group_sha256": hashlib.sha256("\n".join(sorted(frame.loc[test, "condition_group"])).encode()).hexdigest().upper(),
        })
    baseline = np.ones_like(y, dtype=bool)
    report = {
        "dataset": "TEXAS_PHYSICAL_PIPE_NETWORK_DYNAMIC_PRESSURE",
        "data_origin": "AUTHENTIC_OBSERVED_CONTROLLED_PHYSICAL_TESTBED",
        "files": int(len(frame)), "features": features,
        "endpoint": "Controlled leak-present versus no-leak physical run; label from experimental file condition",
        "split": "5-fold StratifiedGroupKFold across whole physical-run condition groups; P1 only, so paired P1/P2 signals never cross folds",
        "folds": fold_rows,
        "out_of_fold_metrics": _metrics(y, probability),
        "always_leak_baseline": {
            "accuracy": float(accuracy_score(y, baseline)), "f1": float(f1_score(y, baseline)),
            "balanced_accuracy": float(balanced_accuracy_score(y, baseline)),
        },
        "claim_boundary": (
            "This verifies pressure-wave discrimination on a controlled physical pipe network only. "
            "It is not E. coli detection, a microbial-risk model, a drinking-water field validation, "
            "a municipal topology model, or evidence of avoided exposure."
        ),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    main()
