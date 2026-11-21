from __future__ import annotations

from nadi.sdaif.engine import AdaptiveSDAIF, regret, robust_plan


def fixture():
    candidates = ["A", "B", "C"]
    weights = {"A": 3.0, "B": 2.0, "C": 1.0}
    vertices = [
        {"vertex_id": "v1", "risk": 0.8, "affected": ["A"], "scenario_id": "s1"},
        {"vertex_id": "v2", "risk": 0.8, "affected": ["B", "C"], "scenario_id": "s2"},
    ]
    return candidates, weights, vertices


def test_robust_plan_is_deterministic():
    candidates, weights, vertices = fixture()
    a = robust_plan(candidates, vertices, weights, 1, 0.0)
    b = robust_plan(candidates, vertices, weights, 1, 0.0)
    assert a == b


def test_revealed_result_only_filters_matching_scenarios():
    candidates, weights, vertices = fixture()
    engine = AdaptiveSDAIF(epsilon=10, test_cost=0.0)
    result = engine.recommend(candidates, vertices, weights, budget=2, observed={"A": True})
    assert result["compatible_scenarios"] == 1


def test_inconsistent_evidence_abstains():
    candidates, weights, vertices = fixture()
    engine = AdaptiveSDAIF()
    result = engine.recommend(candidates, vertices, weights, budget=2, observed={"A": True, "B": True})
    assert result["status"] == "ABSTAIN"
    assert result["model_mismatch"] is True
    assert result["certified"] is False
    assert len(result["response_guidance"]) == 3


def test_more_compatible_uncertainty_cannot_reduce_static_regret():
    candidates, weights, vertices = fixture()
    _, narrow, _ = robust_plan(candidates, vertices[:1], weights, 1, 0.0)
    _, broad, _ = robust_plan(candidates, vertices, weights, 1, 0.0)
    assert broad >= narrow


def test_conditional_plans_keep_prior_tests_and_total_budget():
    candidates, weights, vertices = fixture()
    engine = AdaptiveSDAIF(epsilon=10, test_cost=0.0)
    result = engine.recommend(candidates, vertices, weights, budget=2, observed={"A": True})
    assert "A" in result["static_fallback_plan"]
    assert len(result["static_fallback_plan"]) == 2
    for entry in result["next_evidence_value"]:
        for branch in entry["branches"].values():
            assert set(("A", entry["test"])).issubset(branch["plan"])
            assert len(branch["plan"]) == 2


def test_exhausted_budget_retains_committed_regret():
    candidates, weights, vertices = fixture()
    engine = AdaptiveSDAIF(epsilon=0, test_cost=0.0)
    result = engine.recommend(candidates, vertices, weights, budget=1, observed={"B": False})
    assert result["selected_tests"] == []
    assert result["static_fallback_plan"] == ["B"]
    assert result["worst_case_regret"] > 0


def test_pending_lab_test_consumes_budget_without_revealing_result():
    candidates, weights, vertices = fixture()
    engine = AdaptiveSDAIF(epsilon=10, test_cost=0.0)
    result = engine.recommend(candidates, vertices, weights, budget=2, pending=["A"])
    assert result["status"] == "OK"
    assert result["compatible_scenarios"] == 2
    assert result["selected_tests"][0] != "A"
    assert len(result["static_fallback_plan"]) == 2
    assert "A" in result["static_fallback_plan"]


def test_result_beyond_deadline_uses_static_plan_without_contingency():
    candidates, weights, vertices = fixture()
    engine = AdaptiveSDAIF(epsilon=10, test_cost=0.0)
    result = engine.recommend(candidates, vertices, weights, budget=2, feedback_available=False)
    assert result["status"] == "OK"
    assert result["selected_tests"][0] in result["static_fallback_plan"]
    assert result["contingent_next"] == {}
    assert result["next_evidence_value"] == []
    assert result["worst_case_regret"] == result["pre_test_static_regret"]


def test_pending_and_observed_same_test_rejected():
    candidates, weights, vertices = fixture()
    result = AdaptiveSDAIF().recommend(candidates, vertices, weights, budget=2,
                                       observed={"A": True}, pending=["A"])
    assert result["status"] == "ABSTAIN"

