from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import Any, Iterable


def _loss(plan: frozenset[str], vertex: dict[str, Any], weights: dict[str, float], test_cost: float) -> float:
    node_risk = vertex.get("node_risk")
    if node_risk is not None:
        missed = sum(weights[node] * float(node_risk.get(node, 0.0)) for node in weights if node not in plan)
        return float(missed + test_cost * len(plan))
    affected = set(vertex["affected"])
    missed = sum(weights[node] for node in affected.difference(plan))
    return float(vertex["risk"] * missed + test_cost * len(plan))


def _oracle_loss(vertex: dict[str, Any], weights: dict[str, float], budget: int, test_cost: float) -> float:
    if vertex.get("node_risk") is not None:
        ranked = sorted(weights, key=lambda node: (-weights[node] * float(vertex["node_risk"].get(node, 0.0)), node))[:budget]
    else:
        ranked = sorted(vertex["affected"], key=lambda node: (-weights[node], node))[:budget]
    return _loss(frozenset(ranked), vertex, weights, test_cost)


def plan_regrets(plan: frozenset[str], vertices: list[dict[str, Any]], weights: dict[str, float], budget: int, test_cost: float) -> list[dict[str, Any]]:
    rows = []
    for vertex in vertices:
        value = _loss(plan, vertex, weights, test_cost) - _oracle_loss(vertex, weights, budget, test_cost)
        rows.append({
            "vertex": vertex,
            "regret": float(max(0.0, value)),
            "state_probability": float(vertex.get("state_probability", 1.0)),
        })
    return rows


def regret(plan: frozenset[str], vertices: list[dict[str, Any]], weights: dict[str, float], budget: int, test_cost: float) -> tuple[float, dict[str, Any]]:
    if not vertices:
        return 0.0, {"vertex_id": "EMPTY_COMPATIBLE_SET", "regret": 0.0}
    rows = plan_regrets(plan, vertices, weights, budget, test_cost)
    row = max(rows, key=lambda item: (item["regret"], item["vertex"]["vertex_id"]))
    value, witness = row["regret"], row["vertex"]
    return value, {"vertex_id": witness["vertex_id"], "risk": witness["risk"], "affected": witness["affected"], "regret": value}


def robust_plan(candidates: Iterable[str], vertices: list[dict[str, Any]], weights: dict[str, float], budget: int, test_cost: float, fixed: Iterable[str] = ()) -> tuple[list[str], float, dict[str, Any]]:
    candidates = tuple(sorted(set(candidates)))
    fixed_set = frozenset(fixed)
    remaining = tuple(node for node in candidates if node not in fixed_set)
    choose = max(0, min(budget - len(fixed_set), len(remaining)))
    best = None
    for extra in itertools.combinations(remaining, choose):
        plan = fixed_set.union(extra)
        bound, witness = regret(plan, vertices, weights, budget, test_cost)
        key = (bound, tuple(sorted(plan)))
        if best is None or key < best[0]:
            best = (key, plan, witness)
    assert best is not None
    return sorted(best[1]), float(best[0][0]), best[2]


@dataclass
class AdaptiveSDAIF:
    epsilon: float = 0.15
    test_cost: float = 0.02

    def recommend(
        self, candidates: list[str], vertices: list[dict[str, Any]], weights: dict[str, float],
        budget: int, observed: dict[str, bool] | None = None,
        pending: Iterable[str] = (), feedback_available: bool = True,
    ) -> dict[str, Any]:
        observed = dict(observed or {})
        pending_set = set(pending)
        if pending_set.intersection(observed):
            return {"status": "ABSTAIN", "reason": "PENDING_AND_OBSERVED_OVERLAP", "selected_tests": [], "certified": False}
        committed = set(observed).union(pending_set)
        compatible = [
            vertex for vertex in vertices
            if all((node in vertex["affected"]) == result for node, result in observed.items())
        ]
        if not compatible:
            return {
                "status": "ABSTAIN",
                "reason": "INCONSISTENT_EVIDENCE: no hydraulic-risk scenario matches revealed results",
                "selected_tests": [],
                "worst_case_regret": None,
                "certified": False,
                "model_mismatch": True,
                "response_guidance": [
                    "Escalate to a water-system operator; the enumerated routes cannot explain the observed result.",
                    "Request independent confirmatory sampling and inspect unmodelled sources, valve states, and sensor or sample error.",
                    "Do not use the previous scenario-bound certificate for protective action.",
                ],
                "adversarial_scenario": None,
                "next_evidence_value": [],
            }
        if len(committed) > budget:
            return {"status": "ABSTAIN", "reason": "COMMITTED_TESTS_EXCEED_BUDGET", "selected_tests": [], "certified": False}
        remaining_budget = budget - len(committed)
        available = [node for node in candidates if node not in committed]
        # Every conditional plan and oracle uses the original total budget.
        # Already performed tests remain committed in both the static and
        # contingent plans; the hindsight oracle retains the same budget.
        static_plan, static_regret, static_witness = robust_plan(
            candidates, compatible, weights, budget, self.test_cost, fixed=committed
        )
        if remaining_budget <= 0 or not available:
            return {
                "status": "OK",
                "selected_tests": [],
                "static_fallback_plan": static_plan,
                "contingent_next": {},
                "worst_case_regret": static_regret,
                "certified": static_regret <= self.epsilon,
                "adversarial_scenario": static_witness,
                "next_evidence_value": [],
                "compatible_scenarios": len(compatible),
            }
        if not feedback_available:
            # A result expected after the decision deadline cannot justify a
            # contingent branch. Commit the next node in the static plan.
            next_static = next(node for node in static_plan if node not in committed)
            return {
                "status": "OK",
                "selected_tests": [next_static],
                "static_fallback_plan": static_plan,
                "contingent_next": {},
                "worst_case_regret": static_regret,
                "pre_test_static_regret": static_regret,
                "certified": static_regret <= self.epsilon,
                "adversarial_scenario": static_witness,
                "next_evidence_value": [],
                "compatible_scenarios": len(compatible),
                "evidence_mode": "PENDING_BEYOND_DECISION_DEADLINE",
            }
        values = []
        for node in available:
            branch_rows = {}
            branch_worst = 0.0
            for result in (False, True):
                branch = [v for v in compatible if (node in v["affected"]) == result]
                if not branch:
                    continue
                plan, bound, witness = robust_plan(
                    candidates, branch, weights, budget, self.test_cost,
                    fixed=[*committed, node]
                )
                branch_rows[str(result).lower()] = {"plan": plan, "regret": bound, "witness": witness, "compatible": len(branch)}
                branch_worst = max(branch_worst, bound)
            values.append({
                "test": node,
                "worst_post_test_regret": branch_worst,
                "robust_regret_reduction": static_regret - branch_worst,
                "value_per_unit_cost": (static_regret - branch_worst) / max(self.test_cost, 1e-12),
                "branches": branch_rows,
            })
        values.sort(key=lambda row: (-row["robust_regret_reduction"], row["worst_post_test_regret"], row["test"]))
        chosen = values[0]
        return {
            "status": "OK",
            "selected_tests": [chosen["test"]],
            "static_fallback_plan": static_plan,
            "contingent_next": chosen["branches"],
            "worst_case_regret": chosen["worst_post_test_regret"],
            "pre_test_static_regret": static_regret,
            "certified": chosen["worst_post_test_regret"] <= self.epsilon,
            "adversarial_scenario": static_witness,
            "next_evidence_value": values,
            "compatible_scenarios": len(compatible),
        }

