from nadi.hydraulics.ensemble import HydraulicScenario
from nadi.hydraulics.placement import balanced_source_placement, distinguishable_cross_source_pairs, greedy_source_discrimination


def test_greedy_placement_covers_source_pair_when_one_test_can():
    scenarios = (
        HydraulicScenario("a", "A", 1.0, frozenset({"common", "informative"}), {}),
        HydraulicScenario("b", "B", 1.0, frozenset({"common"}), {}),
    )
    chosen = greedy_source_discrimination(scenarios, 1)
    assert chosen == ["informative"]
    assert distinguishable_cross_source_pairs(scenarios, chosen) == (1, 1)


def test_balanced_placement_adds_monitor_for_uncovered_source_branch():
    scenarios = (
        HydraulicScenario("a", "A", 1.0, frozenset({"A1", "A2"}), {}),
        HydraulicScenario("b", "B", 1.0, frozenset({"B1", "B2"}), {}),
    )
    chosen = balanced_source_placement(scenarios, 2)
    assert len(chosen) == 2
    assert any(node.startswith("A") for node in chosen)
    assert any(node.startswith("B") for node in chosen)
