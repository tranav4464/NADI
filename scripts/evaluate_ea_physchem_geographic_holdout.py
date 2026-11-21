"""Unseen-location holdout for the authentic EA physicochemical panel."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.pipeline import make_pipeline
from xgboost import XGBClassifier

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT.parent / "nadi_resources" / "datasets" / "EA_ECOLI_AUTHENTIC" / "ea_ecoli_physchem_panel_q1_2024.csv"
OUT = ROOT / "results" / "ea_ecoli_physchem_geographic_holdout_v1.json"


def score(y, p):
    pred = (p >= 0.5).astype(int)
    return {"accuracy": float(accuracy_score(y, pred)), "precision": float(precision_score(y, pred, zero_division=0)), "recall": float(recall_score(y, pred, zero_division=0)), "f1": float(f1_score(y, pred, zero_division=0)), "roc_auc": float(roc_auc_score(y, p)) if len(np.unique(y)) > 1 else None}


def main() -> None:
    df = pd.read_csv(PANEL, dtype=str)
    features = [c for c in ["ph_0061", "temperature_0076", "conductivity_0077"] if c in df]
    X = df[features].apply(pd.to_numeric, errors="coerce")
    result_numeric = pd.to_numeric(df["ecoli_result_raw"].str.replace(",", "", regex=False), errors="coerce")
    y = ((result_numeric >= 500) & result_numeric.notna()).astype(int)
    sites = df["samplingPoint.notation"].fillna("UNKNOWN").astype(str)
    # Deterministic site hash avoids selecting test locations by target value.
    test_sites = {s for s in sites.unique() if int(hashlib.sha256(s.encode()).hexdigest()[:8], 16) % 5 == 0}
    train_idx = sites[~sites.isin(test_sites)].index
    test_idx = sites[sites.isin(test_sites)].index
    models = {
        "hist_gradient_boosting": HistGradientBoostingClassifier(max_iter=160, learning_rate=0.06, max_leaf_nodes=12, random_state=20261118),
        "xgb_prior_art_reproduction": XGBClassifier(n_estimators=220, max_depth=4, learning_rate=0.05, subsample=0.85, colsample_bytree=0.85, objective="binary:logistic", eval_metric="logloss", random_state=20261118, n_jobs=1),
    }
    scores = {}
    for name, estimator in models.items():
        model = make_pipeline(SimpleImputer(strategy="median", add_indicator=True), estimator)
        model.fit(X.loc[train_idx], y.loc[train_idx])
        scores[name] = score(y.loc[test_idx], model.predict_proba(X.loc[test_idx])[:, 1])
    out = {"dataset": "EA_ECOLI_AUTHENTIC_PHYSCHEM_PANEL", "data_origin": "AUTHENTIC_OBSERVED", "endpoint": "E. coli >= 500 CFU/100 ml", "records": int(len(df)), "unique_sites": int(sites.nunique()), "train_sites": int(len(set(sites.loc[train_idx]))), "test_sites": int(len(test_sites)), "test_records": int(len(test_idx)), "features": features, "split": "deterministic site-hash holdout; no site appears in both partitions", "models": scores, "claim_boundary": "Unseen-location surface-water transfer check only; 500 CFU/100 ml is a recreational-water convention and this does not validate Delhi-NCR drinking-network performance."}
    OUT.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
