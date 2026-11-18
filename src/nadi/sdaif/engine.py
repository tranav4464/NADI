from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import Any, Iterable


def _loss(plan: frozenset[str], vertex: dict[str, Any], weights: dict[str, float], test_cost: float) -> float:
    affected = set(vertex["affected"])
    missed = sum(weights[node] for node in affected.difference(plan))
    return float(vertex["risk"] * missed + test_cost * len(plan))


def _oracle_loss(vertex: dict[str, Any], weights: dict[str, float], budget: int, test_cost: float) -> float:
    ranked = sorted(vertex["affected"], key=lambda node: (-weights[node], node))[:budget]
    return _loss(frozenset(ranked), vertex, weights, test_cost)


def regret(plan: frozenset[str], vertices: list[dict[str, Any]], weights: dict[str, float], budget: int, test_cost: float) -> tuple[float, dict[str, Any]]:
    if not vertices:
        return 0.0, {"vertex_id": "EMPTY_COMPATIBLE_SET", "regret": 0.0}
    rows = []
    for vertex in vertices:
        value = _loss(plan, vertex, weights, test_cost) - _oracle_loss(vertex, weights, budget, test_cost)
        rows.append((float(max(0.0, value)), vertex))
    value, witness = max(rows, key=lambda row: (row[0], row[1]["vertex_id"]))
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

    def recommend(self, candidates: list[str], vertices: list[dict[str, Any]], weights: dict[str, float], budget: int, observed: dict[str, bool] | None = None) -> dict[str, Any]:
        observed = dict(observed or {})
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
                "adversarial_scenario": None,
                "next_evidence_value": [],
            }
        remaining_budget = max(0, budget - len(observed))
        available = [node for node in candidates if node not in observed]
        static_plan, static_regret, static_witness = robust_plan(
            available, compatible, weights, remaining_budget, self.test_cost
        ) if remaining_budget else ([], 0.0, {"vertex_id": "BUDGET_EXHAUSTED", "regret": 0.0})
        if remaining_budget <= 0 or not available:
            return {
                "status": "OK",
                "selected_tests": [],
                "contingent_next": {},
                "worst_case_regret": static_regret,
                "certified": static_regret <= self.epsilon,
                "adversarial_scenario": static_witness,
                "next_evidence_value": [],
                "compatible_scenarios": len(compatible),
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
                    [x for x in available if x != node], branch, weights,
                    remaining_budget, self.test_cost, fixed=[node]
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

