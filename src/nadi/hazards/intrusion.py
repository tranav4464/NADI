from __future__ import annotations

from dataclasses import dataclass, asdict
from math import exp
from typing import Any, Mapping


def _clip(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def _sigmoid(value: float) -> float:
    value = max(-30.0, min(30.0, float(value)))
    return 1.0 / (1.0 + exp(-value))


@dataclass(frozen=True)
class IntrusionEvidence:
    score: float
    lower: float
    upper: float
    support: float
    abstain: bool
    contributors: dict[str, float]
    claim_boundary: str = "Heuristic intrusion-hazard context; not E. coli detection or proof of entry."

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def estimate_intrusion_hazard(observation: Mapping[str, Any]) -> IntrusionEvidence:
    """Compute monotone, interpretable intrusion-context evidence.

    This is intentionally not trained on biological labels. It turns available
    operational/context observations into a bounded hazard signal. Missing
    inputs widen the interval and may trigger abstention.
    """
    values: dict[str, float] = {}
    contributors: dict[str, float] = {}
    if observation.get("min_pressure") is not None:
        values["low_pressure"] = _clip((1.0 - float(observation["min_pressure"]) / max(float(observation.get("reference_pressure", 1.0)), 1e-9)))
    if observation.get("pressure_drop") is not None:
        values["pressure_drop"] = _clip(float(observation["pressure_drop"]))
    # Location-adaptive inputs are preferred when available. They are robust
    # scores produced by the causal local-normal layer, so the hazard function
    # does not impose a city-independent raw-unit threshold.
    if observation.get("pressure_low_z") is not None:
        values["low_pressure"] = _sigmoid(-float(observation["pressure_low_z"]))
    if observation.get("pressure_drop_z") is not None:
        values["pressure_drop"] = _sigmoid(float(observation["pressure_drop_z"]))
    if observation.get("sewage_distance_m") is not None:
        values["sewage_proximity"] = exp(-max(0.0, float(observation["sewage_distance_m"])) / 50.0)
    for key in ("flooding", "pipe_defect", "intermittent_restart"):
        if observation.get(key) is not None:
            values[key] = _clip(float(observation[key]))
    if observation.get("chlorine_drop") is not None:
        values["chlorine_drop"] = _clip(float(observation["chlorine_drop"]))
    if observation.get("turbidity_spike") is not None:
        values["turbidity_spike"] = _clip(float(observation["turbidity_spike"]))
    if observation.get("chlorine_drop_z") is not None:
        values["chlorine_drop"] = _sigmoid(float(observation["chlorine_drop_z"]))
    if observation.get("turbidity_spike_z") is not None:
        values["turbidity_spike"] = _sigmoid(float(observation["turbidity_spike_z"]))
    weights = {
        "low_pressure": 0.22, "pressure_drop": 0.14, "sewage_proximity": 0.16,
        "flooding": 0.12, "pipe_defect": 0.14, "intermittent_restart": 0.08,
        "chlorine_drop": 0.08, "turbidity_spike": 0.06,
    }
    for key, value in values.items():
        contributors[key] = weights[key] * value
    # No single proxy dominates; independent evidence accumulates with
    # diminishing returns and remains bounded in [0,1].
    score = 1.0
    for contribution in contributors.values():
        score *= 1.0 - contribution
    score = 1.0 - score
    support = len(values) / len(weights)
    missing = 1.0 - support
    lower = max(0.0, score - 0.15 * missing)
    upper = min(1.0, score + 0.35 * missing)
    return IntrusionEvidence(
        score=float(score), lower=float(lower), upper=float(upper), support=float(support),
        abstain=not values or support < 0.25, contributors=contributors,
    )
