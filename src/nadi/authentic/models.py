from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    matthews_corrcoef,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBClassifier


NUMERIC_FEATURES = [
    "easting_km", "northing_km", "day_sin", "day_cos", "month",
    "site_prior_samples", "site_prior_positive_rate",
    "site_prior_mean_log_count", "site_last_positive",
    "days_since_site_sample", "region_prior_samples",
    "region_prior_positive_rate", "global_prior_samples",
    "global_prior_positive_rate",
]
CATEGORICAL_FEATURES = ["region", "material", "sampling_purpose"]
TARGET = "high_500"


class ProbabilityCalibrator:
    """A small Platt calibrator fitted only on the chronological calibration set."""

    def __init__(self) -> None:
        self.model = LogisticRegression(C=1e6, solver="lbfgs")

    @staticmethod
    def _logit(probabilities: np.ndarray) -> np.ndarray:
        clipped = np.clip(np.asarray(probabilities, dtype=float), 1e-6, 1 - 1e-6)
        return np.log(clipped / (1.0 - clipped)).reshape(-1, 1)

    def fit(self, probabilities: np.ndarray, labels: np.ndarray) -> "ProbabilityCalibrator":
        self.model.fit(self._logit(probabilities), np.asarray(labels, dtype=int))
        return self

    def predict(self, probabilities: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(self._logit(probabilities))[:, 1]


@dataclass
class CalibratedAuthenticModel:
    name: str
    estimator: Any
    calibrator: ProbabilityCalibrator | None = None

    def fit(self, train: pd.DataFrame, calibration: pd.DataFrame) -> "CalibratedAuthenticModel":
        self.estimator.fit(train[NUMERIC_FEATURES + CATEGORICAL_FEATURES], train[TARGET].astype(int))
        raw = self.estimator.predict_proba(calibration[NUMERIC_FEATURES + CATEGORICAL_FEATURES])[:, 1]
        self.calibrator = ProbabilityCalibrator().fit(raw, calibration[TARGET].to_numpy())
        return self

    def predict_proba(self, frame: pd.DataFrame) -> np.ndarray:
        raw = self.estimator.predict_proba(frame[NUMERIC_FEATURES + CATEGORICAL_FEATURES])[:, 1]
        return self.calibrator.predict(raw) if self.calibrator else raw


def _preprocessor(scale: bool) -> ColumnTransformer:
    numeric_steps: list[tuple[str, Any]] = [("impute", SimpleImputer(strategy="median"))]
    if scale:
        numeric_steps.append(("scale", StandardScaler()))
    return ColumnTransformer([
        ("numeric", Pipeline(numeric_steps), NUMERIC_FEATURES),
        ("categorical", Pipeline([
            ("impute", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]), CATEGORICAL_FEATURES),
    ])


def model_family(random_state: int = 2026) -> dict[str, CalibratedAuthenticModel]:
    logistic = Pipeline([
        ("features", _preprocessor(scale=True)),
        ("model", LogisticRegression(max_iter=1500, class_weight="balanced", C=0.5, random_state=random_state)),
    ])
    xgb = Pipeline([
        ("features", _preprocessor(scale=False)),
        ("model", XGBClassifier(
            n_estimators=350, max_depth=4, learning_rate=0.035,
            subsample=0.85, colsample_bytree=0.85, min_child_weight=4,
            reg_alpha=0.15, reg_lambda=2.0, eval_metric="logloss",
            random_state=random_state, n_jobs=4,
        )),
    ])
    # The histogram model intentionally uses only continuous past-only fields;
    # it provides a structurally different uncertainty vertex.
    hist = Pipeline([
        ("features", ColumnTransformer([
            ("numeric", Pipeline([("impute", SimpleImputer(strategy="median"))]), NUMERIC_FEATURES),
        ])),
        ("model", HistGradientBoostingClassifier(
            max_iter=300, learning_rate=0.055, max_leaf_nodes=20,
            min_samples_leaf=25, l2_regularization=1.0, random_state=random_state,
        )),
    ])
    return {
        "logistic": CalibratedAuthenticModel("logistic", logistic),
        "xgboost": CalibratedAuthenticModel("xgboost", xgb),
        "hist_gradient": CalibratedAuthenticModel("hist_gradient", hist),
    }


def expected_calibration_error(labels: np.ndarray, probabilities: np.ndarray, bins: int = 10) -> float:
    labels = np.asarray(labels, dtype=int)
    probabilities = np.asarray(probabilities, dtype=float)
    edges = np.linspace(0.0, 1.0, bins + 1)
    total = len(labels)
    value = 0.0
    for low, high in zip(edges[:-1], edges[1:]):
        mask = (probabilities >= low) & (probabilities < high if high < 1 else probabilities <= high)
        if mask.any():
            value += mask.sum() / total * abs(labels[mask].mean() - probabilities[mask].mean())
    return float(value)


def classification_metrics(labels: np.ndarray, probabilities: np.ndarray, threshold: float) -> dict[str, Any]:
    labels = np.asarray(labels, dtype=int)
    probabilities = np.asarray(probabilities, dtype=float)
    predicted = (probabilities >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(labels, predicted, labels=[0, 1]).ravel()
    return {
        "n": int(len(labels)), "prevalence": float(labels.mean()), "threshold": float(threshold),
        "f1": float(f1_score(labels, predicted, zero_division=0)),
        "sensitivity": float(recall_score(labels, predicted, zero_division=0)),
        "specificity": float(tn / (tn + fp)) if tn + fp else 0.0,
        "precision": float(precision_score(labels, predicted, zero_division=0)),
        "npv": float(tn / (tn + fn)) if tn + fn else 0.0,
        "balanced_accuracy": float(balanced_accuracy_score(labels, predicted)),
        "mcc": float(matthews_corrcoef(labels, predicted)),
        "roc_auc": float(roc_auc_score(labels, probabilities)),
        "pr_auc": float(average_precision_score(labels, probabilities)),
        "brier": float(brier_score_loss(labels, probabilities)),
        "ece_10": expected_calibration_error(labels, probabilities, 10),
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
    }


def select_threshold(labels: np.ndarray, probabilities: np.ndarray) -> float:
    """Choose a validation-only threshold by balanced accuracy, then F1."""
    labels = np.asarray(labels, dtype=int)
    probabilities = np.asarray(probabilities, dtype=float)
    candidates = np.linspace(0.05, 0.95, 181)
    best = None
    for threshold in candidates:
        predicted = (probabilities >= threshold).astype(int)
        tn, fp, fn, tp = confusion_matrix(labels, predicted, labels=[0, 1]).ravel()
        sensitivity = tp / (tp + fn) if tp + fn else 0.0
        specificity = tn / (tn + fp) if tn + fp else 0.0
        balanced = (sensitivity + specificity) / 2.0
        f1 = 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.0
        key = (balanced, f1, -abs(float(threshold) - 0.5))
        if best is None or key > best[0]:
            best = (key, float(threshold))
    return best[1]
