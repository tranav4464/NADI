from nadi.decision.actions import rank_protective_actions


def test_action_ranking_is_bounded_and_requires_review():
    rows = rank_protective_actions([{"probability": 0.8, "consequence_weight": 2.0}], 0.9)
    assert rows
    assert all(row["requires_operator_review"] for row in rows)
    assert rows[0]["decision_score"] >= rows[-1]["decision_score"]
