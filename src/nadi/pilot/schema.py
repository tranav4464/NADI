"""Fail-closed validation for a real, prospective NADI pilot.

This module intentionally does not generate events, outcomes, or topology.
It checks whether a partner's *observed* sampling and ranking records can
support the only honest prospective claim: that a frozen pre-laboratory ranking
was compared fairly with declared alternatives.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import pandas as pd


SAMPLE_COLUMNS = {
    "pilot_round_id", "location_id", "collected_at_utc", "result_available_at_utc",
    "ecoli_result", "ecoli_unit", "ecoli_method", "valid_result", "sampling_reason",
}
RANKING_COLUMNS = {
    "pilot_round_id", "location_id", "policy", "rank", "information_cutoff_utc",
    "ranking_frozen_at_utc", "risk_probability", "abstained",
}
REQUIRED_POLICIES = {"nadi_sdaif", "routine"}


@dataclass(frozen=True)
class PilotAudit:
    """Machine-readable result of a privacy-preserving prospective-pilot check."""

    status: str
    errors: tuple[str, ...]
    warnings: tuple[str, ...]
    rounds: int
    valid_samples: int
    ranked_samples: int
    policies: tuple[str, ...]
    claim_boundary: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "rounds": self.rounds,
            "valid_samples": self.valid_samples,
            "ranked_samples": self.ranked_samples,
            "policies": list(self.policies),
            "claim_boundary": self.claim_boundary,
        }


def _missing(frame: pd.DataFrame, required: set[str]) -> list[str]:
    return sorted(required.difference(frame.columns))


def _utc(frame: pd.DataFrame, column: str, errors: list[str]) -> pd.Series:
    value = pd.to_datetime(frame[column], utc=True, errors="coerce")
    if value.isna().any():
        errors.append(f"INVALID_TIMESTAMP:{column}:{int(value.isna().sum())}")
    return value


def audit_pilot_bundle(
    samples: pd.DataFrame,
    rankings: pd.DataFrame,
    *,
    endpoint_rule: Mapping[str, Any] | None = None,
) -> PilotAudit:
    """Verify prospective records without looking at biology during ranking.

    The expected data contain pseudonymous location identifiers only.  Every
    ranking must be frozen no later than its information cutoff; every valid
    laboratory result must arrive after that cutoff.  NADI and the declared
    routine policy must cover the same eligible round/location universe.
    """
    errors: list[str] = []
    warnings: list[str] = []
    missing_samples = _missing(samples, SAMPLE_COLUMNS)
    missing_rankings = _missing(rankings, RANKING_COLUMNS)
    if missing_samples:
        errors.append("MISSING_SAMPLE_COLUMNS:" + ",".join(missing_samples))
    if missing_rankings:
        errors.append("MISSING_RANKING_COLUMNS:" + ",".join(missing_rankings))
    if errors:
        return PilotAudit("REJECT", tuple(errors), tuple(warnings), 0, 0, 0, (),
                          "Schema is incomplete; no performance or public-health claim may be made.")

    s = samples.copy()
    r = rankings.copy()
    for frame in (s, r):
        for key in ("pilot_round_id", "location_id"):
            frame[key] = frame[key].astype(str)
    collected = _utc(s, "collected_at_utc", errors)
    available = _utc(s, "result_available_at_utc", errors)
    cutoff = _utc(r, "information_cutoff_utc", errors)
    frozen = _utc(r, "ranking_frozen_at_utc", errors)
    valid = s["valid_result"].astype(str).str.lower().isin({"true", "1", "yes"})
    if (available[valid] <= collected[valid]).any():
        errors.append("NONCAUSAL_LAB_RESULT_TIME")
    if (frozen > cutoff).any():
        errors.append("RANKING_NOT_FROZEN_BY_INFORMATION_CUTOFF")
    if r.duplicated(["pilot_round_id", "location_id", "policy", "rank"]).any():
        errors.append("DUPLICATE_POLICY_RANK")
    if (pd.to_numeric(r["rank"], errors="coerce") < 1).any():
        errors.append("INVALID_RANK")

    merged = r.merge(
        s[["pilot_round_id", "location_id", "result_available_at_utc", "valid_result"]],
        on=["pilot_round_id", "location_id"], how="left", validate="many_to_one",
    )
    merged_available = pd.to_datetime(merged["result_available_at_utc"], utc=True, errors="coerce")
    # A missing sample can be valid only if a predeclared policy did not select
    # that location.  A selected test must have a later independent result.
    selected = pd.to_numeric(merged["rank"], errors="coerce") >= 1
    if merged.loc[selected, "result_available_at_utc"].isna().any():
        errors.append("RANKED_LOCATION_LACKS_LAB_RECORD")
    if ((merged_available <= cutoff.loc[merged.index]) & merged_available.notna()).any():
        errors.append("LAB_OUTCOME_AVAILABLE_AT_OR_BEFORE_RANKING_CUTOFF")

    policies = set(r["policy"].astype(str))
    absent = sorted(REQUIRED_POLICIES.difference(policies))
    if absent:
        errors.append("MISSING_REQUIRED_POLICY:" + ",".join(absent))
    rounds = sorted(set(s["pilot_round_id"]).intersection(r["pilot_round_id"]))
    if not rounds:
        errors.append("NO_SHARED_PILOT_ROUNDS")
    for round_id in rounds:
        expected = set(s.loc[s["pilot_round_id"] == round_id, "location_id"])
        for policy in REQUIRED_POLICIES.intersection(policies):
            observed = set(r.loc[(r["pilot_round_id"] == round_id) & (r["policy"] == policy), "location_id"])
            if observed != expected:
                errors.append(f"UNEQUAL_ELIGIBLE_LOCATIONS:{round_id}:{policy}")

    if endpoint_rule is None:
        warnings.append("ENDPOINT_RULE_NOT_RECORDED: retain unit, method, detection limit and threshold in preregistration")
    else:
        required_endpoint = {"analyte", "threshold", "unit"}
        absent_endpoint = sorted(required_endpoint.difference(endpoint_rule))
        if absent_endpoint:
            errors.append("INCOMPLETE_ENDPOINT_RULE:" + ",".join(absent_endpoint))
    if not errors and len(rounds) < 10:
        warnings.append("SMALL_PROSPECTIVE_PILOT: report uncertainty; do not make a superiority claim from few independent rounds")

    return PilotAudit(
        "PASS" if not errors else "REJECT", tuple(sorted(set(errors)),), tuple(sorted(set(warnings))),
        len(rounds), int(valid.sum()), int(len(r)), tuple(sorted(policies)),
        "Passing this audit establishes a leakage-safe prospective comparison design only. "
        "It does not establish direct E. coli detection, pipeline localisation, illness reduction, or utility validation.",
    )
