from __future__ import annotations

import random
from typing import Any

from ..sdaif.engine import robust_plan


def _top(scores: dict[str, float], budget: int) -> list[str]:
    return [node for node, _ in sorted(scores.items(), key=lambda item: (-item[1], item[0]))[:budget]]


def select_all(
    candidates: list[str],
    reach_probability: dict[str, float],
    consequence: dict[str, float],
    vertices: list[dict[str, Any]],
    budget: int,
    seed: int,
    test_cost: float,
    sampling_propensity: dict[str, float] | None = None,
) -> dict[str, list[str]]:
    rng = random.Random(seed)
    random_order = list(candidates)
    rng.shuffle(random_order)
    routine = sorted(candidates)[:budget]
    risk_only = sorted(candidates, key=lambda node: node)[:budget]
    hydraulic = _top(reach_probability, budget)
    population = _top(consequence, budget)
    bayes_score = {node: reach_probability[node] * consequence[node] for node in candidates}
    bayesian = _top(bayes_score, budget)
    sampling_propensity = sampling_propensity or {node: 1.0 for node in candidates}
    ipw_score = {node: bayes_score[node] / max(0.05, sampling_propensity[node]) for node in candidates}
    ipw = _top(ipw_score, budget)
    robust, _, _ = robust_plan(candidates, vertices, consequence, budget, test_cost)
    return {
        "random": random_order[:budget],
        "routine": routine,
        "risk_only": risk_only,
        "context_only": risk_only,
        "anomaly_only": routine,
        "hydraulic_only": hydraulic,
        "population_only": population,
        "bayesian": bayesian,
        "inverse_probability_weighted": ipw,
        "non_adaptive_robust": robust,
    }


def adaptive_bayesian_sequence(
    candidates: list[str],
    vertices: list[dict[str, Any]],
    consequence: dict[str, float],
    budget: int,
    hidden_affected: set[str],
) -> list[str]:
    """Sequential Bayes-value comparator with the same result access as SDAIF.

    Vertices receive equal prior mass because the benchmark supplies no
    externally justified scenario prior.  After each selected test, only
    vertices consistent with the revealed result remain.
    """
    compatible = list(vertices)
    selected: list[str] = []
    for _ in range(budget):
        available = [node for node in candidates if node not in selected]
        if not available or not compatible:
            break
        scores = {}
        for node in available:
            expected = sum(float(v["risk"]) * (node in v["affected"]) for v in compatible) / len(compatible)
            scores[node] = expected * consequence[node]
        node = _top(scores, 1)[0]
        selected.append(node)
        result = node in hidden_affected
        compatible = [v for v in compatible if (node in v["affected"]) == result]
    return selected

