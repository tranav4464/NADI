"""Evaluate authentic WDSEventDB event labels without treating them as E. coli.

The database is an operational water-distribution testbed (clean, leakage,
cyberattack and sensor-failure events).  We use event-file holdouts so rows
from one event cannot leak into both training and testing.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.pipeline import make_pipeline

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT.parent / "nadi_resources" / "datasets" / "existing_verified" / "WDSEventDB_extracted" / "WDSEventDB"
OUT = ROOT / "results" / "wdseventdb_event_holdout_v1.json"


def main() -> None:
    paths = sorted(p for p in DATA.rglob("*.xlsx") if p.name != "CleanData.xlsx")
    frames = []
    for p in paths:
        d = pd.read_excel(p)
        d["event_file"] = str(p.relative_to(DATA))
        d["event_family"] = p.parent.name
        frames.append(d)
    all_data = pd.concat(frames, ignore_index=True)
    target = "Labels"
    features = [c for c in all_data.columns if c not in {target, "event_file", "event_family"}]
    results = []
    for holdout in sorted(all_data.event_file.unique()):
        train = all_data[all_data.event_file != holdout]
        test = all_data[all_data.event_file == holdout]
        model = make_pipeline(SimpleImputer(strategy="median", add_indicator=True), HistGradientBoostingClassifier(max_iter=160, learning_rate=0.06, max_leaf_nodes=12, random_state=20261118))
        model.fit(train[features], train[target])
        p = model.predict_proba(test[features])[:, 1]
        pred = (p >= 0.5).astype(int)
        y = test[target].to_numpy()
        results.append({"holdout": holdout, "rows": int(len(test)), "positive_rate": float(y.mean()), "accuracy": float(accuracy_score(y, pred)), "precision": float(precision_score(y, pred, zero_division=0)), "recall": float(recall_score(y, pred, zero_division=0)), "f1": float(f1_score(y, pred, zero_division=0)), "roc_auc": float(roc_auc_score(y, p)) if len(np.unique(y)) > 1 else None})
    result = {"dataset": "WDSEventDB", "data_origin": "AUTHENTIC_OBSERVED_TESTBED", "records": int(len(all_data)), "event_files": int(len(paths)), "features": features, "split": "event-file holdout", "holdouts": results, "macro_f1": float(np.mean([x["f1"] for x in results])), "macro_roc_auc": float(np.mean([x["roc_auc"] for x in results if x["roc_auc"] is not None])), "use": "operational anomaly and sensor-failure robustness benchmark", "claim_boundary": "WDSEventDB labels are leakage/cyberattack/sensor-failure testbed events, not E. coli or fecal contamination labels."}
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
