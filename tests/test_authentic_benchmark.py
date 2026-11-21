from __future__ import annotations

import numpy as np
import pandas as pd

from nadi.authentic.benchmark import evaluate_authentic_rounds, paired_bootstrap_difference


def test_round_benchmark_reveals_only_authentic_outcomes() -> None:
    frame = pd.DataFrame({
        "round_id": ["R1"] * 5,
        "samplingPoint.notation": list("ABCDE"),
        "high_500": [1, 0, 1, 0, 0],
        "site_prior_samples": [5, 4, 3, 2, 1],
        "site_prior_positive_rate": [.2, .3, .4, .1, .2],
    })
    probabilities = {
        "m1": np.array([.8, .2, .7, .1, .3]),
        "m2": np.array([.6, .4, .8, .2, .1]),
    }
    events, summary = evaluate_authentic_rounds(
        frame, probabilities, {"m1": .5, "m2": .5}, "m1", budget=2, max_sites=10
    )
    assert set(events["data_origin"]) == {"AUTHENTIC_OBSERVED"}
    assert "adaptive_sdaif" in set(summary["policy"])
    assert events["positives_found"].max() <= 2
    comparison = paired_bootstrap_difference(events, "adaptive_sdaif", "random", "positives_found", replicates=50)
    assert comparison["rounds"] == 1
