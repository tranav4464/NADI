from __future__ import annotations

import numpy as np

from nadi.authentic.models import classification_metrics, expected_calibration_error


def test_classification_metrics_expose_imbalance_safe_measures() -> None:
    labels = np.array([0, 0, 1, 1])
    probabilities = np.array([0.1, 0.4, 0.6, 0.9])
    result = classification_metrics(labels, probabilities, 0.5)
    assert result["balanced_accuracy"] == 1.0
    assert result["mcc"] == 1.0
    assert result["confusion_matrix"] == {"tn": 2, "fp": 0, "fn": 0, "tp": 2}


def test_calibration_error_is_zero_for_matching_bins() -> None:
    labels = np.array([0, 1])
    probabilities = np.array([0.0, 1.0])
    assert expected_calibration_error(labels, probabilities, 2) == 0.0
