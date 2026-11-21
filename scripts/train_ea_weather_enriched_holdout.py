"""Evaluate Open E. coli-style weather enrichment on authentic EA data."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.pipeline import make_pipeline
from xgboost import XGBClassifier

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT.parent / "nadi_resources" / "datasets" / "EA_ECOLI_AUTHENTIC"
OUT = ROOT / "results" / "ea_weather_enriched_holdout_v1.json"


def main() -> None:
    panel = pd.read_csv(DATA / "ea_ecoli_physchem_panel_q1_2024.csv", dtype=str)
    weather = pd.read_csv(DATA / "ea_openmeteo_weather_panel_q1_2024.csv", dtype=str)
    panel["date"] = pd.to_datetime(panel["phenomenonTime"], utc=True).dt.date.astype(str)
    weather["date"] = weather["date"].astype(str)
    df = panel.merge(weather, on=["samplingPoint.notation", "date"], how="left", validate="many_to_one")
    base = [c for c in ["ph_0061", "temperature_0076", "conductivity_0077"] if c in df]
    weather_cols = [c for c in ["temperature_2m_mean", "precipitation_sum", "relative_humidity_2m_mean"] if c in df]
    features = base + weather_cols
    X = df[features].apply(pd.to_numeric, errors="coerce")
    result_numeric = pd.to_numeric(df["ecoli_result_raw"].str.replace(",", "", regex=False), errors="coerce")
    y = ((result_numeric >= 500) & result_numeric.notna()).astype(int)
    sites = df["samplingPoint.notation"].fillna("UNKNOWN").astype(str)
    test_sites = {s for s in sites.unique() if int(hashlib.sha256(s.encode()).hexdigest()[:8], 16) % 5 == 0}
    train_idx, test_idx = sites[~sites.isin(test_sites)].index, sites[sites.isin(test_sites)].index
    model = make_pipeline(SimpleImputer(strategy="median", add_indicator=True), XGBClassifier(n_estimators=220, max_depth=4, learning_rate=0.05, subsample=0.85, colsample_bytree=0.85, objective="binary:logistic", eval_metric="logloss", random_state=20261118, n_jobs=1))
    model.fit(X.loc[train_idx], y.loc[train_idx])
    p = model.predict_proba(X.loc[test_idx])[:, 1]
    pred = (p >= 0.5).astype(int)
    out = {"dataset": "EA_ECOLI_AUTHENTIC_PLUS_OPENMETEO", "data_origin": "AUTHENTIC_OBSERVED", "records": int(len(df)), "features": features, "weather_match_rate": float(df[weather_cols].notna().all(axis=1).mean()), "test_sites": int(len(test_sites)), "test_records": int(len(test_idx)), "split": "deterministic site-hash holdout", "endpoint": "E. coli >= 500 CFU/100 ml", "model": "XGBClassifier adapted from Open E. coli prior-art family", "metrics": {"accuracy": float(accuracy_score(y.loc[test_idx], pred)), "precision": float(precision_score(y.loc[test_idx], pred, zero_division=0)), "recall": float(recall_score(y.loc[test_idx], pred, zero_division=0)), "f1": float(f1_score(y.loc[test_idx], pred, zero_division=0)), "roc_auc": float(roc_auc_score(y.loc[test_idx], p))}, "claim_boundary": "Authentic England surface-water transfer check with observed weather covariates; not drinking-network validation, direct sensor detection or bit-for-bit full Open E. coli reproduction."}
    OUT.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
