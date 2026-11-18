from __future__ import annotations

from nadi.transfer.gate import enforce_domain
from nadi.types import RiskEstimate


def estimate():
    return RiskEstimate(0.4, 0.2, 0.6, "test endpoint", 24, "SURFACE_WATER_CONTEXT", True, "v1", 0.9)


def test_real_drinking_network_transfer_abstains():
    result = enforce_domain(estimate(), "DELHI_DRINKING_NETWORK")
    assert result.abstain
    assert result.lower == 0.0 and result.upper == 1.0


def test_simulated_bridge_is_explicit_and_wider():
    original = estimate()
    result = enforce_domain(original, "SIMULATED_NETWORK_EVENT", allow_simulated_bridge=True)
    assert not result.abstain
    assert result.lower <= original.lower and result.upper >= original.upper
    assert "simulated-bridge" in result.model_version

