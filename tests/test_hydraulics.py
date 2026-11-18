from __future__ import annotations

from nadi.hydraulics.ensemble import load_reference_ensemble, scenario_vertices
from nadi.types import RiskEstimate


def test_reference_ensemble_is_reproducible_and_simulated():
    a = load_reference_ensemble(12)
    b = load_reference_ensemble(12)
    assert a.candidates == b.candidates
    assert len(a.scenarios) >= 6
    assert all(s.origin == "SIMULATED" for s in a.scenarios)
    assert any(s.affected for s in a.scenarios)
    assert len({tuple(sorted(s.affected)) for s in a.scenarios}) > 1


def test_risk_bounds_expand_vertex_set():
    ensemble = load_reference_ensemble(8)
    risk = RiskEstimate(0.5, 0.2, 0.8, "endpoint", 24, "SIMULATED_NETWORK_EVENT", True, "v", 1.0)
    vertices = scenario_vertices(ensemble, risk)
    assert len(vertices) == 2 * len(ensemble.scenarios)
    assert {v["risk"] for v in vertices} == {0.2, 0.8}

