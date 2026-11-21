from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable


@dataclass(frozen=True)
class ProtectiveAction:
    name: str
    coverage: float
    cost: float
    delay_hours: float
    reversibility: float
    operational_note: str


DEFAULT_ACTIONS = (
    ProtectiveAction("confirmatory_sampling", 0.25, 1.0, 1.0, 1.0, "Collect independent laboratory samples at ranked nodes."),
    ProtectiveAction("inspect_intrusion_path", 0.35, 1.5, 2.0, 0.9, "Inspect plausible leak, sewer-crossing or tank-entry pathways."),
    ProtectiveAction("targeted_flush", 0.55, 2.0, 2.5, 0.8, "Flush only the ranked branch under operator-approved procedure."),
    ProtectiveAction("temporary_isolation", 0.80, 3.0, 1.0, 0.5, "Isolate a bounded branch pending confirmation and operator review."),
    ProtectiveAction("precautionary_advisory", 1.00, 1.2, 0.25, 0.7, "Issue a bounded precautionary notice to the affected service area."),
)


def rank_protective_actions(
    affected_region: Iterable[dict[str, Any]],
    risk_upper: float,
    actions: Iterable[ProtectiveAction] = DEFAULT_ACTIONS,
) -> list[dict[str, Any]]:
    """Rank advisory actions using explicit consequence and uncertainty terms.

    This is decision support, not automatic actuation. `risk_upper` is used to
    avoid false reassurance; all outputs require operator and laboratory review.
    """
    rows = list(affected_region)
    total_consequence = sum(float(row.get("probability", 0.0)) * float(row.get("consequence_weight", 1.0)) for row in rows)
    risk_upper = max(0.0, min(1.0, float(risk_upper)))
    scored = []
    for action in actions:
        expected_benefit = risk_upper * total_consequence * action.coverage
        delay_penalty = 0.05 * action.delay_hours * risk_upper * total_consequence
        score = expected_benefit - action.cost - delay_penalty
        scored.append({
            **asdict(action),
            "expected_benefit": expected_benefit,
            "delay_penalty": delay_penalty,
            "decision_score": score,
            "requires_operator_review": True,
            "requires_confirmatory_testing": action.name != "precautionary_advisory",
        })
    return sorted(scored, key=lambda row: (-row["decision_score"], row["cost"], row["name"]))
