from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

EvidenceKind = Literal["OBSERVED", "LAB_CONFIRMED", "MODEL_ESTIMATE", "SIMULATED", "ASSUMED"]


@dataclass(frozen=True)
class Evidence:
    name: str
    value: Any
    available_at: str
    kind: EvidenceKind
    source_id: str
    domain: str


@dataclass(frozen=True)
class RiskEstimate:
    probability: float
    lower: float
    upper: float
    endpoint: str
    horizon_hours: int
    evidence_domain: str
    calibrated: bool
    model_version: str
    support_score: float
    abstain: bool = False
    abstention_reason: str | None = None
    features: dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class ReachEstimate:
    node_id: str
    probability: float
    earliest_hours: float | None
    latest_hours: float | None
    consequence_weight: float
    kind: EvidenceKind = "SIMULATED"


@dataclass(frozen=True)
class DecisionCard:
    event_id: str
    selected_tests: list[str]
    alternative_policies: dict[str, list[str]]
    worst_case_regret: float | None
    epsilon: float
    certified: bool
    abstained: bool
    abstention_reason: str | None
    adversarial_scenario: dict[str, Any] | None
    next_evidence_value: list[dict[str, Any]]
    dominant_uncertainty: str
    evidence_labels: list[str]
    model_versions: dict[str, str]
    claim_boundary: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

