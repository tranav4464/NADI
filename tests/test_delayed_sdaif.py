from nadi.sdaif.delayed import delayed_test_sequence
from nadi.sdaif.engine import AdaptiveSDAIF


def test_delayed_results_are_unavailable_until_ready_and_budget_is_enforced():
    vertices = [
        {"vertex_id": "a", "risk": 1.0, "affected": ["A"]},
        {"vertex_id": "b", "risk": 1.0, "affected": ["B"]},
    ]
    result = delayed_test_sequence(AdaptiveSDAIF(), ["A", "B", "C"], vertices,
                                   {"A": 1.0, "B": 1.0, "C": 1.0}, 2, {"B"}, 2)
    assert len(result["selected"]) == 2
    assert len(set(result["selected"])) == 2
    assert all(not row["observed_before_selection"] for row in result["timeline"])
    assert all(row["evidence_mode"] == "PENDING_BEYOND_DECISION_DEADLINE"
               for row in result["timeline"])


def test_immediate_next_round_result_can_update_compatible_scenarios():
    vertices = [
        {"vertex_id": "a", "risk": 1.0, "affected": ["A"]},
        {"vertex_id": "b", "risk": 1.0, "affected": ["B"]},
    ]
    result = delayed_test_sequence(AdaptiveSDAIF(), ["A", "B", "C"], vertices,
                                   {"A": 1.0, "B": 1.0, "C": 1.0}, 2, {"B"}, 0)
    first = result["selected"][0]
    assert result["timeline"][1]["observed_before_selection"] == {"%s" % first: first == "B"}
