from __future__ import annotations

from nadi.authentic.policy import AuthenticSDAIF, authentic_sdaif_sequence, update_model_weights


PREDICTIONS = {
    "m1": {"A": 0.8, "B": 0.2, "C": 0.5},
    "m2": {"A": 0.3, "B": 0.7, "C": 0.4},
}


def test_authentic_outcome_updates_model_weights() -> None:
    before, _ = update_model_weights(PREDICTIONS, {"m1": 0.5, "m2": 0.5}, {})
    after, _ = update_model_weights(PREDICTIONS, {"m1": 0.5, "m2": 0.5}, {"A": True})
    assert before != after
    assert after["m1"] > after["m2"]


def test_authentic_sdaif_never_reads_unselected_truth() -> None:
    truth = {"A": True, "B": False, "C": True}
    result = authentic_sdaif_sequence(PREDICTIONS, {"m1": 0.5, "m2": 0.5}, truth, budget=2, robustness_weight=0.25)
    assert len(result["selected"]) == 2
    assert set(result["observed"]) == set(result["selected"])
    assert all("posterior_before_result" in step for step in result["steps"])
    assert all("selected_site_information_value" in step for step in result["steps"])


def test_authentic_sdaif_returns_one_next_site() -> None:
    result = AuthenticSDAIF(0.25).recommend(PREDICTIONS, {"m1": 0.5, "m2": 0.5}, budget=2)
    assert result["status"] == "OK"
    assert len(result["selected_tests"]) == 1


def test_first_authentic_decision_is_invariant_to_hidden_future_outcomes() -> None:
    # Before the first laboratory result arrives, changing unrevealed labels
    # must not change the recommendation. This guards against retrospective
    # ranking leakage in the authentic replay.
    engine = AuthenticSDAIF(0.25)
    first = engine.recommend(PREDICTIONS, {"m1": 0.5, "m2": 0.5}, budget=2)
    sequence_a = authentic_sdaif_sequence(
        PREDICTIONS, {"m1": 0.5, "m2": 0.5}, {"A": True, "B": False, "C": False}, 2, 0.25
    )
    sequence_b = authentic_sdaif_sequence(
        PREDICTIONS, {"m1": 0.5, "m2": 0.5}, {"A": True, "B": True, "C": True}, 2, 0.25
    )
    assert sequence_a["selected"][0] == first["selected_tests"][0]
    assert sequence_b["selected"][0] == first["selected_tests"][0]
