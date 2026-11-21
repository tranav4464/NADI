"""Run the Open E. coli model's core XGBoost classification idea on an
authentic, sample-matched EA subset.

This is an explicit controlled adaptation, not a claim of bit-for-bit
reproduction: the repository's full EA/NRW/SEPA + weather/land-cover/MODIS
tables are not bundled, so the available official EA panel is used and every
domain/input difference is recorded.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.pipeline import make_pipeline
from xgboost import XGBClassifier

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT.parent / "nadi_resources" / "datasets" / "EA_ECOLI_AUTHENTIC" / "ea_ecoli_physchem_panel_q1_2024.csv"
OUT = ROOT / "results" / "open_ecoli_prior_art_adaptation_v1.json"


def main() -> None:
    df = pd.read_csv(PANEL, dtype=str)
    t = pd.to_datetime(df["phenomenonTime"], utc=True)
    features = [c for c in ["ph_0061", "temperature_0076", "conductivity_0077"] if c in df]
    X = df[features].apply(pd.to_numeric, errors="coerce")
    result_numeric = pd.to_numeric(df["ecoli_result_raw"].str.replace(",", "", regex=False), errors="coerce")
    y = ((result_numeric >= 500) & result_numeric.notna()).astype(int)
    order = t.sort_values().index
    cut = int(len(order) * 0.8)
    train, test = order[:cut], order[cut:]
    model = make_pipeline(SimpleImputer(strategy="median", add_indicator=True), XGBClassifier(n_estimators=220, max_depth=4, learning_rate=0.05, subsample=0.85, colsample_bytree=0.85, objective="binary:logistic", eval_metric="logloss", random_state=20261118, n_jobs=1))
    model.fit(X.loc[train, features], y.loc[train])
    p = model.predict_proba(X.loc[test, features])[:, 1]
    pred = (p >= 0.5).astype(int)
    yt = y.loc[test]
    metrics = {"accuracy": float(accuracy_score(yt, pred)), "precision": float(precision_score(yt, pred, zero_division=0)), "recall": float(recall_score(yt, pred, zero_division=0)), "f1": float(f1_score(yt, pred, zero_division=0)), "roc_auc": float(roc_auc_score(yt, p))}
    out = {"replication_id": "OPEN-ECOLI-XGB-AUTHENTIC-SUBSET-V1", "data_origin": "AUTHENTIC_OBSERVED", "repository": "Cognizant-RDMAI/Open-Ecoli-Models", "repository_commit": "4bca9807a0b62ee83df97d68b52430a3b1cda3b9", "records": int(len(df)), "feature_columns": features, "endpoint": "E. coli >= 500 CFU/100 ml", "split": "ordered temporal 80/20", "model": "XGBClassifier (core prior-art family)", "metrics": metrics, "status": "CONTROLLED_AUTHENTIC_SUBSET_ADAPTATION", "differences_from_full_prior_art": ["Uses 648 official EA Q1-2024 surface-water samples rather than the repository's full multi-agency EA/NRW/SEPA corpus.", "Uses sample-matched pH, water temperature and conductivity only; weather, CORINE and MODIS features are unavailable in this bounded panel.", "500 CFU/100 ml is a recreational-water convention, not a drinking-water standard."], "claim_boundary": "Demonstrates the prior-art XGBoost method on authentic EA observations; it is not bit-for-bit reproduction, direct sensor detection or Delhi-NCR drinking-network validation."}
    OUT.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
