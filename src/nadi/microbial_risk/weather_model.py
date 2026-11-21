from __future__ import annotations

import json
import math
import hashlib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.ensemble import ExtraTreesClassifier, GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, average_precision_score, brier_score_loss, f1_score, log_loss, precision_score, recall_score, roc_auc_score
from sklearn.tree import DecisionTreeClassifier
try:
    from xgboost import XGBClassifier
except Exception:  # optional dependency; the remaining families remain usable
    XGBClassifier = None
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from ..paths import INTERIM_ROOT, PROCESSED_ROOT
from ..types import RiskEstimate

FORECAST_FEATURES = [
    "prcp_prev_1d", "prcp_prev_3d", "prcp_prev_10d", "prcp_prev_15d",
    "tavg_prev_1d", "tavg_prev_3d", "tavg_prev_10d", "tavg_prev_15d",
    "month_sin", "month_cos",
]
NOWCAST_FEATURES = FORECAST_FEATURES + ["prcp_same_day", "tavg_same_day"]


def expected_calibration_error(y: np.ndarray, p: np.ndarray, bins: int = 10) -> float:
    edges = np.linspace(0.0, 1.0, bins + 1)
    total = len(y)
    value = 0.0
    for low, high in zip(edges[:-1], edges[1:]):
        mask = (p >= low) & (p < high if high < 1 else p <= high)
        if mask.any():
            value += mask.mean() * abs(float(y[mask].mean()) - float(p[mask].mean()))
    return float(value)


def _metrics(y: np.ndarray, p: np.ndarray) -> dict[str, float | None]:
    return {
        "n": int(len(y)),
        "positives": int(y.sum()),
        "prevalence": float(y.mean()),
        "brier": float(brier_score_loss(y, p)),
        "log_loss": float(log_loss(y, np.clip(p, 1e-8, 1 - 1e-8), labels=[0, 1])),
        "roc_auc": float(roc_auc_score(y, p)) if len(np.unique(y)) == 2 else None,
        "average_precision": float(average_precision_score(y, p)) if y.sum() else None,
        "ece_10": expected_calibration_error(y, p),
    }


def _logit(p: np.ndarray) -> np.ndarray:
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p)).reshape(-1, 1)


def _candidate_models() -> dict[str, Pipeline]:
    """Model families disclosed by the ISEF reconstruction, kept in one selector.

    Selection is performed on the calibration partition only; the final test is
    never used to choose a family or a threshold.
    """
    common = {"imputer": SimpleImputer(strategy="median", add_indicator=True)}
    candidates = {
        "logistic": Pipeline([("impute", common["imputer"]), ("scale", StandardScaler()),
                              ("model", LogisticRegression(max_iter=2000, class_weight="balanced", C=0.5, random_state=20261117))]),
        "random_forest": Pipeline([("impute", common["imputer"]),
                                    ("model", RandomForestClassifier(n_estimators=300, min_samples_leaf=3, class_weight="balanced_subsample", random_state=20261117, n_jobs=-1))]),
        "extra_trees": Pipeline([("impute", SimpleImputer(strategy="median", add_indicator=True)),
                                  ("model", ExtraTreesClassifier(n_estimators=300, min_samples_leaf=2, class_weight="balanced", random_state=20261117, n_jobs=-1))]),
        "decision_tree": Pipeline([("impute", SimpleImputer(strategy="median", add_indicator=True)),
                                    ("model", DecisionTreeClassifier(max_depth=6, min_samples_leaf=8, class_weight="balanced", random_state=20261117))]),
        "gradient_boosting": Pipeline([("impute", SimpleImputer(strategy="median", add_indicator=True)),
                                        ("model", GradientBoostingClassifier(n_estimators=200, learning_rate=0.04, max_depth=2, random_state=20261117))]),
    }
    if XGBClassifier is not None:
        candidates["xgboost"] = Pipeline([("impute", SimpleImputer(strategy="median", add_indicator=True)),
                                           ("model", XGBClassifier(n_estimators=160, learning_rate=0.05, max_depth=3,
                                                                    subsample=0.85, colsample_bytree=0.85,
                                                                    eval_metric="logloss", random_state=20261117,
                                                                    n_jobs=1, tree_method="hist"))])
    return candidates


def _f1_threshold(y: np.ndarray, p: np.ndarray) -> float:
    thresholds = np.unique(np.concatenate(([0.05], np.linspace(0.05, 0.95, 181), [0.95])))
    scores = [(f1_score(y, p >= threshold, zero_division=0), -threshold, float(threshold)) for threshold in thresholds]
    return float(max(scores)[2])


def _thresholded_metrics(y: np.ndarray, p: np.ndarray, threshold: float) -> dict[str, float | int]:
    prediction = p >= threshold
    tp = int(np.sum((y == 1) & prediction))
    tn = int(np.sum((y == 0) & ~prediction))
    fp = int(np.sum((y == 0) & prediction))
    fn = int(np.sum((y == 1) & ~prediction))
    return {
        "threshold": float(threshold),
        "accuracy": float(accuracy_score(y, prediction)),
        "precision": float(precision_score(y, prediction, zero_division=0)),
        "recall": float(recall_score(y, prediction, zero_division=0)),
        "positive_f1": float(f1_score(y, prediction, zero_division=0)),
        "n": int(len(y)), "positives": int(y.sum()), "prevalence": float(y.mean()),
        "tn": tn, "fp": fp, "fn": fn, "tp": tp,
    }


@dataclass
class CalibratedRiskHead:
    mode: str
    features: list[str]
    base: Any
    calibrator: Any
    calibration_radius: float
    support_low: dict[str, float]
    support_high: dict[str, float]
    endpoint: str
    version: str
    selected_model: str = "logistic"

    def _frame(self, record: dict[str, Any]) -> pd.DataFrame:
        return pd.DataFrame([{name: record.get(name, np.nan) for name in self.features}])

    def predict(self, record: dict[str, Any]) -> RiskEstimate:
        frame = self._frame(record)
        raw = self.base.predict_proba(frame)[:, 1]
        probability = float(self.calibrator.predict_proba(_logit(raw))[:, 1][0])
        observed = 0
        supported = 0
        for name in self.features:
            value = record.get(name)
            if value is None or not np.isfinite(float(value)):
                continue
            observed += 1
            supported += self.support_low[name] <= float(value) <= self.support_high[name]
        completeness = observed / len(self.features)
        range_support = supported / observed if observed else 0.0
        support = float(completeness * range_support)
        inflation = (1.0 - support) * 0.25
        radius = min(0.49, self.calibration_radius + inflation)
        abstain = support < 0.55
        reason = None if not abstain else f"OUT_OF_SUPPORT: score={support:.3f} < 0.550"
        return RiskEstimate(
            probability=probability,
            lower=max(0.0, probability - radius),
            upper=min(1.0, probability + radius),
            endpoint=self.endpoint,
            horizon_hours=24 if self.mode == "forecast" else 0,
            evidence_domain="SURFACE_WATER_CONTEXT",
            calibrated=True,
            model_version=self.version,
            support_score=support,
            abstain=abstain,
            abstention_reason=reason,
            features={name: float(record[name]) for name in self.features if record.get(name) is not None and np.isfinite(float(record[name]))},
        )


def _fit_head(train: pd.DataFrame, calibration: pd.DataFrame, test: pd.DataFrame, features: list[str], mode: str, endpoint: str) -> tuple[CalibratedRiskHead, dict]:
    y_train = train["elevated_ecoli"].to_numpy(dtype=int)
    y_cal = calibration["elevated_ecoli"].to_numpy(dtype=int)
    y_test = test["elevated_ecoli"].to_numpy(dtype=int)
    comparisons: dict[str, dict[str, float | None]] = {}
    fitted: dict[str, tuple[Pipeline, LogisticRegression, np.ndarray, float]] = {}
    for name, candidate in _candidate_models().items():
        candidate.fit(train[features], y_train)
        p_cal_raw = candidate.predict_proba(calibration[features])[:, 1]
        calibrator_candidate = LogisticRegression(C=1e6, max_iter=1000, random_state=20261117)
        calibrator_candidate.fit(_logit(p_cal_raw), y_cal)
        p_cal_candidate = calibrator_candidate.predict_proba(_logit(p_cal_raw))[:, 1]
        threshold = _f1_threshold(y_cal, p_cal_candidate)
        metrics = _metrics(y_cal, p_cal_candidate)
        metrics["positive_f1"] = float(f1_score(y_cal, p_cal_candidate >= threshold, zero_division=0))
        metrics["f1_threshold"] = threshold
        comparisons[name] = metrics
        fitted[name] = (candidate, calibrator_candidate, p_cal_candidate, threshold)
    selected_model = max(comparisons, key=lambda name: (float(comparisons[name]["positive_f1"] or 0.0), -float(comparisons[name]["brier"] or 1.0), name == "logistic"))
    base, calibrator, p_cal, selected_threshold = fitted[selected_model]
    p_test = calibrator.predict_proba(_logit(base.predict_proba(test[features])[:, 1]))[:, 1]
    # This is uncertainty for the calibrated probability, not a prediction
    # interval for the future binary outcome.  The latter would be nearly
    # vacuous for Bernoulli data.  We combine a conservative binomial standard
    # error at p=.5 with observed validation calibration error.
    calibration_ece = expected_calibration_error(y_cal, p_cal)
    radius = float(min(0.49, 1.96 * math.sqrt(0.25 / len(y_cal)) + calibration_ece))
    head = CalibratedRiskHead(
        mode=mode,
        features=list(features),
        base=base,
        calibrator=calibrator,
        calibration_radius=radius,
        support_low={name: float(train[name].quantile(0.01)) for name in features},
        support_high={name: float(train[name].quantile(0.99)) for name in features},
        endpoint=endpoint,
        version=f"wqp-weather-{mode}-{selected_model}-v2",
        selected_model=selected_model,
    )
    report = {
        "mode": mode,
        "features": features,
        "model_comparison": comparisons,
        "selected_model": selected_model,
        "selected_validation_threshold": selected_threshold,
        "calibration": _metrics(y_cal, p_cal),
        "untouched_test": _metrics(y_test, p_test),
        "untouched_test_thresholded": _thresholded_metrics(y_test, p_test, selected_threshold),
        "probability_uncertainty_radius": radius,
        "uncertainty_method": "1.96*sqrt(0.25/n_calibration) + validation ECE; probability uncertainty, not a Bernoulli outcome interval",
        "claim_boundary": "Surface-water E. coli context model; not direct sensor detection and not drinking-network validation",
    }
    return head, report


def train(config: dict) -> dict:
    source = INTERIM_ROOT / "wqp_marion_weather.csv"
    if not source.exists():
        raise FileNotFoundError("Run `nadi prepare` before training the risk model")
    data = pd.read_csv(source, parse_dates=["date"])
    train_end = pd.Timestamp(config["risk_model"]["train_end"])
    calibration_end = pd.Timestamp(config["risk_model"]["calibration_end"])
    test_end = pd.Timestamp(config["risk_model"]["test_end"])
    development = data[data["date"] <= train_end].copy()
    calibration = data[(data["date"] > train_end) & (data["date"] <= calibration_end)].copy()
    test = data[(data["date"] > calibration_end) & (data["date"] <= test_end)].copy()
    if min(len(development), len(calibration), len(test)) == 0:
        raise ValueError("Temporal split produced an empty partition")
    endpoint = config["risk_endpoint"]
    nowcast, now_report = _fit_head(development, calibration, test, NOWCAST_FEATURES, "nowcast", endpoint)
    forecast, forecast_report = _fit_head(development, calibration, test, FORECAST_FEATURES, "forecast", endpoint)
    sites = sorted(data["site_id"].dropna().astype(str).unique())
    heldout_sites = {
        site for site in sites
        if int(hashlib.sha256(f"NADI-SITE-HOLDOUT:{site}".encode()).hexdigest()[:8], 16) % 5 == 0
    }
    geo_development = development[~development["site_id"].astype(str).isin(heldout_sites)].copy()
    geo_calibration = calibration[~calibration["site_id"].astype(str).isin(heldout_sites)].copy()
    geo_test = test[test["site_id"].astype(str).isin(heldout_sites)].copy()
    geographic_audit: dict[str, Any]
    if min(len(geo_development), len(geo_calibration), len(geo_test)) > 0 and geo_test["elevated_ecoli"].nunique() == 2:
        _, geo_report = _fit_head(
            geo_development, geo_calibration, geo_test,
            FORECAST_FEATURES, "forecast-geographic-audit", endpoint,
        )
        geographic_audit = {
            "status": "COMPLETED",
            "partition_rule": "SHA256(site_id) modulo 5 equals 0; fixed before fitting",
            "heldout_site_count": len(heldout_sites),
            "heldout_sites_sha256": hashlib.sha256("\n".join(sorted(heldout_sites)).encode()).hexdigest().upper(),
            "development_rows": len(geo_development),
            "calibration_rows": len(geo_calibration),
            "test_rows": len(geo_test),
            "metrics": geo_report["untouched_test"],
            "claim_boundary": "Later samples from unseen Marion County surface-water sites; not cross-city or drinking-network validation",
        }
    else:
        geographic_audit = {
            "status": "NOT_ESTIMABLE",
            "reason": "Deterministic site/date holdout lacked sufficient rows and both endpoint classes",
            "heldout_site_count": len(heldout_sites),
        }
    PROCESSED_ROOT.mkdir(parents=True, exist_ok=True)
    joblib.dump({"nowcast": nowcast, "forecast": forecast}, PROCESSED_ROOT / "risk_bundle.joblib")
    report = {
        "schema_version": "0.1.0",
        "split": {
            "train": [str(development.date.min().date()), str(development.date.max().date()), int(len(development))],
            "calibration": [str(calibration.date.min().date()), str(calibration.date.max().date()), int(len(calibration))],
            "untouched_test": [str(test.date.min().date()), str(test.date.max().date()), int(len(test))],
        },
        "nowcast": now_report,
        "forecast_24h": forecast_report,
        "geographic_transfer_audit": geographic_audit,
        "negative_result_rule": "A head is not promoted for claims solely because it has higher AUC; calibration and decision value govern.",
    }
    (PROCESSED_ROOT / "risk_model_card.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def load_bundle(path: Path | None = None) -> dict[str, CalibratedRiskHead]:
    return joblib.load(path or PROCESSED_ROOT / "risk_bundle.joblib")

