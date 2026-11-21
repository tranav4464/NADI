from __future__ import annotations

from typing import Any

from .engine import AdaptiveSDAIF


def delayed_test_sequence(
    engine: AdaptiveSDAIF, candidates: list[str], vertices: list[dict[str, Any]],
    weights: dict[str, float], budget: int, hidden_affected: set[str],
    extra_result_rounds: int,
) -> dict[str, Any]:
    """Select tests with a fixed synthetic result lag and a hard action deadline.

    Round 0's test returns before round 1 when extra_result_rounds=0. A result
    returning after round `budget-1` cannot inform another selection.
    """
    if extra_result_rounds < 0:
        raise ValueError("extra_result_rounds must be nonnegative")
    observed: dict[str, bool] = {}
    pending: dict[str, int] = {}
    selected: list[str] = []
    timeline = []
    for round_index in range(budget):
        for node, ready in list(pending.items()):
            if ready <= round_index:
                observed[node] = node in hidden_affected
                del pending[node]
        new_result_can_inform_selection = round_index + 1 + extra_result_rounds < budget
        decision = engine.recommend(
            candidates, vertices, weights, budget, observed=observed,
            pending=pending, feedback_available=new_result_can_inform_selection,
        )
        if decision["status"] != "OK" or not decision["selected_tests"]:
            timeline.append({"round": round_index, "status": decision["status"],
                             "observed": dict(observed), "pending": dict(pending)})
            break
        node = decision["selected_tests"][0]
        ready_round = round_index + 1 + extra_result_rounds
        pending[node] = ready_round
        selected.append(node)
        timeline.append({"round": round_index, "status": decision["status"],
                         "selected": node, "ready_round": ready_round,
                         "observed_before_selection": dict(observed),
                         "pending_after_selection": dict(pending),
                         "evidence_mode": decision.get("evidence_mode", "CONTINGENT")})
    return {"selected": selected, "timeline": timeline,
            "observed_by_deadline": dict(observed), "pending_at_deadline": dict(pending)}
