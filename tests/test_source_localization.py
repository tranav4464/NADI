from nadi.hydraulics.ensemble import HydraulicEnsemble, HydraulicScenario
from nadi.hydraulics.localize import source_consistency


def _ensemble():
    scenarios = (
        HydraulicScenario("a1", "A", 1.0, frozenset({"x"}), {}),
        HydraulicScenario("a2", "A", 1.0, frozenset({"x", "y"}), {}),
        HydraulicScenario("b1", "B", 1.0, frozenset({"y"}), {}),
    )
    return HydraulicEnsemble("test", scenarios, ("x", "y"), {"x": 1.0, "y": 1.0}, "test")


def test_source_consistency_filters_only_revealed_tracer_results():
    result = source_consistency(_ensemble(), {"x": True, "y": False})
    assert result["status"] == "IN_MODEL"
    assert result["ranked_sources"][0]["source"] == "A"
    assert result["compatible_scenarios"] == 1
    assert result["certificate_valid"] is False
    assert result["unique_among_enumerated"] is True
    assert result["unknown_source_not_excluded"] is True


def test_inconsistent_reach_does_not_invent_source_probability():
    result = source_consistency(_ensemble(), {"x": False, "y": False})
    assert result["status"] == "OUT_OF_MODEL"
    assert result["ranked_sources"] == []
