from __future__ import annotations

from collections.abc import Mapping

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp

from ..sdaif.engine import plan_regrets


def update_model_weights(
    predictions: Mapping[str, Mapping[str, float]],
    prior: Mapping[str, float],
    observed: Mapping[str, bool],
) -> tuple[dict[str, float], float]:
    raw: dict[str, float] = {}
    for model, node_predictions in predictions.items():
        value = max(0.0, float(prior.get(model, 0.0)))
        for node, outcome in observed.items():
            p = min(1 - 1e-6, max(1e-6, float(node_predictions[node])))
            value *= p if outcome else 1.0 - p
        raw[model] = value
    normalizer = sum(raw.values())
    if normalizer <= 0:
        return {}, 0.0
    return {model: value / normalizer for model, value in raw.items()}, normalizer


def model_vertices(
    predictions: Mapping[str, Mapping[str, float]], weights: Mapping[str, float]
) -> list[dict]:
    return [
        {
            "vertex_id": f"authentic-model:{model}",
            "risk": 1.0,
            "affected": [],
            "node_risk": {node: float(value) for node, value in node_predictions.items()},
            "state_probability": float(weights.get(model, 0.0)),
            "origin": "MODEL_ESTIMATE_FROM_AUTHENTIC_DATA",
        }
        for model, node_predictions in predictions.items()
        if weights.get(model, 0.0) > 0
    ]


def posterior_robust_plan(
    candidates: list[str], vertices: list[dict], budget: int,
    robustness_weight: float, fixed: list[str] | tuple[str, ...] = (),
) -> tuple[list[str], float, float, dict]:
    if not 0 <= robustness_weight <= 1:
        raise ValueError("robustness_weight must lie in [0,1]")
    nodes = sorted(candidates)
    fixed_set = set(fixed)
    target_budget = min(int(budget), len(nodes))
    if len(fixed_set) > target_budget:
        raise ValueError("fixed tests exceed budget")
    model_count = len(vertices)
    risk = np.asarray([
        [float(vertex["node_risk"].get(node, 0.0)) for node in nodes]
        for vertex in vertices
    ])
    probabilities = np.asarray([float(vertex.get("state_probability", 1.0)) for vertex in vertices])
    probabilities /= probabilities.sum()
    oracle = np.sort(risk, axis=1)[:, -target_budget:].sum(axis=1)

    # Variables are x_1..x_n (binary site choices) and t (maximum regret).
    # This is the exact mixed-integer form of the posterior/robust objective,
    # avoiding an exponential enumeration of all testing lists.
    coefficients = np.zeros(len(nodes) + 1)
    coefficients[:-1] = -(1.0 - robustness_weight) * (probabilities @ risk)
    coefficients[-1] = robustness_weight
    rows = []
    upper = []
    lower = []
    budget_row = np.r_[np.ones(len(nodes)), 0.0]
    rows.append(budget_row); lower.append(target_budget); upper.append(target_budget)
    for model_index in range(model_count):
        # t >= oracle_m - sum_i risk_mi*x_i
        rows.append(np.r_[risk[model_index], 1.0])
        lower.append(oracle[model_index]); upper.append(np.inf)
    bounds_low = np.zeros(len(nodes) + 1)
    bounds_high = np.r_[np.ones(len(nodes)), np.inf]
    for node in fixed_set:
        index = nodes.index(node)
        bounds_low[index] = 1.0
        bounds_high[index] = 1.0
    result = milp(
        c=coefficients,
        integrality=np.r_[np.ones(len(nodes)), 0],
        bounds=Bounds(bounds_low, bounds_high),
        constraints=LinearConstraint(np.asarray(rows), np.asarray(lower), np.asarray(upper)),
        options={"time_limit": 10.0},
    )
    if not result.success or result.x is None:
        raise RuntimeError(f"SDAIF optimisation failed: {result.message}")
    plan = frozenset(node for node, selected in zip(nodes, result.x[:-1]) if selected >= 0.5)
    consequence = {node: 1.0 for node in nodes}
    regret_rows = plan_regrets(plan, vertices, consequence, target_budget, 0.0)
    total = sum(row["state_probability"] for row in regret_rows) or 1.0
    expected = sum(row["regret"] * row["state_probability"] for row in regret_rows) / total
    worst_row = max(regret_rows, key=lambda row: (row["regret"], row["vertex"]["vertex_id"]))
    worst = float(worst_row["regret"])
    objective = (1.0 - robustness_weight) * expected + robustness_weight * worst
    return sorted(plan), float(objective), float(worst), {
        "vertex_id": worst_row["vertex"]["vertex_id"], "regret": worst,
    }


class AuthenticSDAIF:
    """Adaptive model-uncertainty decision rule evaluated on real lab outcomes."""

    def __init__(self, robustness_weight: float = 0.25):
        self.robustness_weight = float(robustness_weight)

    def recommend(
        self,
        predictions: Mapping[str, Mapping[str, float]],
        prior_weights: Mapping[str, float],
        budget: int,
        observed: Mapping[str, bool] | None = None,
    ) -> dict:
        observed = dict(observed or {})
        posterior, marginal = update_model_weights(predictions, prior_weights, observed)
        if not posterior:
            return {"status": "ABSTAIN", "reason": "NO_MODEL_SUPPORT", "selected_tests": []}
        candidates = sorted(next(iter(predictions.values())))
        vertices = model_vertices(predictions, posterior)
        static_plan, static_objective, static_worst, witness = posterior_robust_plan(
            candidates, vertices, budget, self.robustness_weight, fixed=list(observed)
        )
        available = [node for node in candidates if node not in observed]
        if len(observed) >= budget or not available:
            return {
                "status": "OK", "selected_tests": [], "posterior": posterior,
                "static_fallback_plan": static_plan, "decision_objective": static_objective,
                "worst_case_regret": static_worst, "adversarial_model": witness,
                "marginal_evidence_likelihood": marginal,
            }
        posterior_mean = {
            node: sum(posterior[model] * predictions[model][node] for model in posterior)
            for node in candidates
        }
        # Execute the exact robust plan sequentially. Among sites already in
        # that plan, reveal first the result expected to be most informative
        # about which calibrated model is locally credible. After the real lab
        # result is revealed, the posterior and exact plan are recomputed.
        # This needs one MILP per step rather than counterfactual simulations.
        executable = [node for node in static_plan if node in available]
        if not executable:
            executable = available
        values = []
        for node in executable:
            model_values = np.asarray([predictions[model][node] for model in posterior], dtype=float)
            model_weights = np.asarray([posterior[model] for model in posterior], dtype=float)
            p = posterior_mean[node]
            disagreement = float(np.sum(model_weights * (model_values - p) ** 2))
            outcome_entropy_proxy = float(4.0 * p * (1.0 - p))
            information_value = disagreement * outcome_entropy_proxy
            values.append({
                "test": node,
                "predictive_positive_probability": p,
                "model_disagreement": disagreement,
                "information_value": information_value,
            })
        values.sort(key=lambda row: (-row["information_value"], -row["predictive_positive_probability"], row["test"]))
        return {
            "status": "OK", "selected_tests": [values[0]["test"]],
            "posterior": posterior, "static_fallback_plan": static_plan,
            "decision_objective": static_objective,
            "worst_case_regret": static_worst, "adversarial_model": witness,
            "marginal_evidence_likelihood": marginal, "next_evidence_value": values,
        }


def authentic_sdaif_sequence(
    predictions: Mapping[str, Mapping[str, float]],
    prior_weights: Mapping[str, float],
    authentic_truth: Mapping[str, bool], budget: int,
    robustness_weight: float,
) -> dict:
    engine = AuthenticSDAIF(robustness_weight)
    observed: dict[str, bool] = {}
    selected: list[str] = []
    steps = []
    for step in range(budget):
        result = engine.recommend(predictions, prior_weights, budget, observed)
        if result["status"] != "OK" or not result["selected_tests"]:
            break
        node = result["selected_tests"][0]
        outcome = bool(authentic_truth[node])
        next_value = next(
            item for item in result.get("next_evidence_value", [])
            if item["test"] == node
        )
        selected.append(node)
        steps.append({
            "step": step + 1, "selected_site": node,
            "authentic_lab_result_revealed_after_selection": outcome,
            "pre_result_objective": result["decision_objective"],
            "pre_result_worst_case_regret": result["worst_case_regret"],
            "posterior_before_result": result["posterior"],
            "robust_fallback_plan_before_result": result["static_fallback_plan"],
            "selected_site_predictive_positive_probability": next_value["predictive_positive_probability"],
            "selected_site_model_disagreement": next_value["model_disagreement"],
            "selected_site_information_value": next_value["information_value"],
            "adversarial_model": result["adversarial_model"],
        })
        observed[node] = outcome
    return {"selected": selected, "observed": observed, "steps": steps}
