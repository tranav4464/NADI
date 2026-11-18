from __future__ import annotations

from dataclasses import replace

from ..types import RiskEstimate


def enforce_domain(estimate: RiskEstimate, requested_domain: str, allow_simulated_bridge: bool = False) -> RiskEstimate:
    if requested_domain == estimate.evidence_domain:
        return estimate
    if allow_simulated_bridge and requested_domain == "SIMULATED_NETWORK_EVENT":
        return replace(
            estimate,
            evidence_domain="SIMULATED_NETWORK_EVENT",
            lower=max(0.0, estimate.lower - 0.10),
            upper=min(1.0, estimate.upper + 0.10),
            model_version=estimate.model_version + "+simulated-bridge",
        )
    return replace(
        estimate,
        abstain=True,
        abstention_reason=(
            f"DOMAIN_MISMATCH: calibrated for {estimate.evidence_domain}; "
            f"requested {requested_domain}. Local biological calibration is required."
        ),
        lower=0.0,
        upper=1.0,
        support_score=0.0,
    )

