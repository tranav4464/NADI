from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Iterable


@dataclass(frozen=True)
class EvidenceInterval:
    name: str
    probability: float
    lower: float
    upper: float
    reliability: float = 1.0
    support: float = 1.0
    available_at: str | None = None
    domain: str = "UNKNOWN"


@dataclass(frozen=True)
class FusedEvidence:
    probability: float
    lower: float
    upper: float
    support: float
    contributors: list[dict]
    dominant_uncertainty: str

    def to_dict(self) -> dict:
        return asdict(self)


def fuse_evidence(intervals: Iterable[EvidenceInterval]) -> FusedEvidence:
    """Fuse typed intervals conservatively, retaining support and provenance.

    Reliable supported estimates receive greater weight, while interval width
    is widened by disagreement. This is a transparent evidence combiner, not a
    replacement for endpoint-specific calibration or a biological assay.
    """
    rows = list(intervals)
    if not rows:
        return FusedEvidence(0.5, 0.0, 1.0, 0.0, [], "no evidence")
    weights = [max(0.0, min(1.0, float(r.reliability) * float(r.support))) for r in rows]
    total = sum(weights)
    if total <= 0:
        return FusedEvidence(0.5, 0.0, 1.0, 0.0, [asdict(r) for r in rows], "unsupported evidence")
    probability = sum(w * max(0.0, min(1.0, r.probability)) for w, r in zip(weights, rows)) / total
    lower = sum(w * max(0.0, min(1.0, r.lower)) for w, r in zip(weights, rows)) / total
    upper = sum(w * max(0.0, min(1.0, r.upper)) for w, r in zip(weights, rows)) / total
    disagreement = max(abs(r.probability - probability) for r in rows)
    lower = max(0.0, lower - disagreement * 0.5)
    upper = min(1.0, upper + disagreement * 0.5)
    dominant = max(rows, key=lambda r: (r.upper - r.lower) + (1.0 - r.support)).name
    return FusedEvidence(
        probability=float(probability), lower=float(lower), upper=float(upper),
        support=float(min(1.0, total / len(rows))), contributors=[asdict(r) for r in rows],
        dominant_uncertainty=dominant,
    )
