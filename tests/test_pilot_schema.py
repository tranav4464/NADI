from __future__ import annotations

import pandas as pd

from nadi.pilot import audit_pilot_bundle


def _samples() -> pd.DataFrame:
    return pd.DataFrame([
        {"pilot_round_id": "r1", "location_id": location, "collected_at_utc": "2026-01-01T09:00:00Z",
         "result_available_at_utc": "2026-01-02T09:00:00Z", "ecoli_result": value,
         "ecoli_unit": "CFU/100mL", "ecoli_method": "partner_method", "valid_result": True,
         "sampling_reason": "prospective_pilot"}
        for location, value in (("A", 0), ("B", 1), ("C", 0))
    ])


def _rankings() -> pd.DataFrame:
    rows = []
    for policy, order in (("nadi_sdaif", ("B", "A", "C")), ("routine", ("A", "B", "C"))):
        for rank, location in enumerate(order, 1):
            rows.append({"pilot_round_id": "r1", "location_id": location, "policy": policy, "rank": rank,
                         "information_cutoff_utc": "2026-01-01T08:00:00Z",
                         "ranking_frozen_at_utc": "2026-01-01T07:59:00Z",
                         "risk_probability": 0.8 if location == "B" else 0.2, "abstained": False})
    return pd.DataFrame(rows)


def test_valid_pilot_schema_passes_with_preregistered_endpoint() -> None:
    result = audit_pilot_bundle(_samples(), _rankings(), endpoint_rule={"analyte": "E. coli", "threshold": 1, "unit": "CFU/100mL"})
    assert result.status == "PASS"
    assert result.rounds == 1
    assert "SMALL_PROSPECTIVE_PILOT" in result.warnings[0]


def test_pilot_schema_rejects_lab_leakage() -> None:
    rankings = _rankings()
    rankings.loc[0, "information_cutoff_utc"] = "2026-01-03T08:00:00Z"
    result = audit_pilot_bundle(_samples(), rankings, endpoint_rule={"analyte": "E. coli", "threshold": 1, "unit": "CFU/100mL"})
    assert result.status == "REJECT"
    assert "LAB_OUTCOME_AVAILABLE_AT_OR_BEFORE_RANKING_CUTOFF" in result.errors
