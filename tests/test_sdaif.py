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


def test_more_compatible_uncertainty_cannot_reduce_static_regret():
    candidates, weights, vertices = fixture()
    _, narrow, _ = robust_plan(candidates, vertices[:1], weights, 1, 0.0)
    _, broad, _ = robust_plan(candidates, vertices, weights, 1, 0.0)
    assert broad >= narrow

