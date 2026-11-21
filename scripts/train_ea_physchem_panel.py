"""Evaluate authentic, sample-matched EA physicochemical features."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, average_precision_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

try:
    from xgboost import XGBClassifier
except ImportError:  # keep the authentic baseline runnable in minimal envs
    XGBClassifier = None

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT.parent / "nadi_resources" / "datasets" / "EA_ECOLI_AUTHENTIC" / "ea_ecoli_physchem_panel_q1_2024.csv"
OUT = ROOT / "results" / "ea_ecoli_physchem_panel_v1.json"


def metrics(y, p):
    pred = (p >= 0.5).astype(int)
    return {
        "accuracy": float(accuracy_score(y, pred)),
        "precision": float(precision_score(y, pred, zero_division=0)),
        "recall": float(recall_score(y, pred, zero_division=0)),
        "f1": float(f1_score(y, pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y, p)) if len(np.unique(y)) > 1 else None,
        "average_precision": float(average_precision_score(y, p)),
    }


def main() -> None:
    df = pd.read_csv(PANEL)
    t = pd.to_datetime(df["phenomenonTime"], utc=True)
    # Use only columns that are actually present in the downloaded panel.  The
    # EA API does not guarantee that every determinand has a sample-matched
    # result in a bounded period; absent determinands must remain documented
    # as unavailable rather than being silently imputed as observations.
    requested_feature_cols = ["ph_0061", "temperature_0076", "conductivity_0077", "ammoniacal_n_0111"]
    feature_cols = [c for c in requested_feature_cols if c in df.columns]
    missing_feature_cols = [c for c in requested_feature_cols if c not in df.columns]
    if not feature_cols:
        raise RuntimeError("No sample-matched physicochemical columns are present in the authentic panel")
    X = df[feature_cols].apply(pd.to_numeric, errors="coerce")
    X["month"] = t.dt.month
    X["day_of_year"] = t.dt.dayofyear
    X["easting_km"] = pd.to_numeric(df["samplingPoint.easting"], errors="coerce") / 1000
    X["northing_km"] = pd.to_numeric(df["samplingPoint.northing"], errors="coerce") / 1000
    y_detect = df["ecoli_detected"].astype(int)
    # The open RDMAI workflow uses a 500 CFU/100 ml risk threshold. Keep this
    # endpoint separate from the laboratory detection endpoint above.
    raw_result = df["ecoli_result_raw"].astype(str)
    numeric_result = pd.to_numeric(raw_result.str.replace(",", "", regex=False), errors="coerce")
    y_high = ((numeric_result >= 500) & numeric_result.notna()).astype(int)
    order = t.sort_values().index
    cut = int(len(order) * 0.8)
    train, test = order[:cut], order[cut:]
    feature_sets = {
        "physicochemical_only": feature_cols,
        "context_only": ["month", "day_of_year", "easting_km", "northing_km"],
        "combined": list(X.columns),
    }
    scores = {"laboratory_detection": {}, "high_risk_500_cfu_per_100ml": {}}
    for endpoint, y in [("laboratory_detection", y_detect), ("high_risk_500_cfu_per_100ml", y_high)]:
        for feature_set_name, cols in feature_sets.items():
            models = {
                "logistic": make_pipeline(SimpleImputer(strategy="median", add_indicator=True), StandardScaler(), LogisticRegression(max_iter=2000, class_weight="balanced")),
                "hist_gradient_boosting": make_pipeline(SimpleImputer(strategy="median", add_indicator=True), HistGradientBoostingClassifier(max_iter=120, learning_rate=0.06, max_leaf_nodes=10, random_state=20261118)),
            }
            if XGBClassifier is not None:
                models["xgb_prior_art_reproduction"] = make_pipeline(
                    SimpleImputer(strategy="median", add_indicator=True),
                    XGBClassifier(
                        n_estimators=220, max_depth=4, learning_rate=0.05,
                        subsample=0.85, colsample_bytree=0.85,
                        objective="binary:logistic", eval_metric="logloss",
                        random_state=20261118, n_jobs=1,
                    ),
                )
            scores[endpoint][feature_set_name] = {}
            for name, model in models.items():
                model.fit(X.loc[train, cols], y.loc[train])
                scores[endpoint][feature_set_name][name] = metrics(y.loc[test], model.predict_proba(X.loc[test, cols])[:, 1])
    result = {"dataset": "EA_ECOLI_AUTHENTIC_PHYSCHEM_PANEL", "data_origin": "AUTHENTIC_OBSERVED", "records": int(len(df)), "positive_prevalence": {"laboratory_detection": float(y_detect.mean()), "high_risk_500_cfu_per_100ml": float(y_high.mean())}, "requested_feature_columns": requested_feature_cols, "available_feature_columns": feature_cols, "missing_feature_columns": missing_feature_cols, "matched_feature_availability": {c: float(X[c].notna().mean()) for c in feature_cols}, "split": {"type": "temporal", "train_fraction": 0.8, "ordered_by": "phenomenonTime"}, "models": scores, "limitations": ["England surface-water samples only; no drinking-network telemetry.", "Only 648 E. coli samples in this bounded quarter and substantial missing physicochemical coverage.", "The 500 CFU/100 ml endpoint is a prior-art bathing-water convention, not a drinking-water standard.", "This does not establish direct sensor detection or Delhi-NCR transfer.", "Some requested determinands had no sample-matched observations in this bounded quarter and were not treated as measured data."]}
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
