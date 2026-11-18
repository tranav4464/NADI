from __future__ import annotations

from nadi.policies.baselines import adaptive_bayesian_sequence


def test_adaptive_bayesian_uses_revealed_result_only_after_selection():
    candidates = ["A", "B"]
    vertices = [
        {"risk": 0.8, "affected": ["A"], "vertex_id": "a"},
        {"risk": 0.8, "affected": ["B"], "vertex_id": "b"},
    ]
    selected = adaptive_bayesian_sequence(candidates, vertices, {"A": 1.0, "B": 1.0}, 2, {"B"})
    assert selected == ["A", "B"]

