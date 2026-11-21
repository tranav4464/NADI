"""Semantic invariants for the canonical authentic and decision tracks."""
from __future__ import annotations

import json

import pandas as pd

from nadi.core.layout import ROOT, sha256


def _authentic_frame() -> pd.DataFrame:
    return pd.read_csv(ROOT / "data_processed/ea_authentic_site_rounds_2024.csv", parse_dates=["round_date", "feature_cutoff"])


def test_authentic_processed_table_is_unique_past_only_and_observed():
    frame = _authentic_frame()
    assert len(frame) == 13405
    assert frame[["round_date", "samplingPoint.notation"]].duplicated().sum() == 0
    assert (frame["feature_cutoff"] < frame["round_date"]).all()
    assert set(frame["data_origin"]) == {"AUTHENTIC_OBSERVED"}
    assert set(frame["high_500"].unique()) <= {0, 1}


def test_chronological_partitions_do_not_overlap_and_locked_records_are_later():
    frame = _authentic_frame()
    train = frame[frame.round_date <= "2024-05-31"]
    calibration = frame[(frame.round_date >= "2024-06-01") & (frame.round_date <= "2024-07-15")]
    validation = frame[(frame.round_date >= "2024-07-16") & (frame.round_date <= "2024-09-30")]
    locked = frame[frame.round_date >= "2024-10-01"]
    assert max(train.round_date) < min(calibration.round_date) < min(validation.round_date) < min(locked.round_date)
    assert set(train.index).isdisjoint(calibration.index)
    assert set(calibration.index).isdisjoint(validation.index)
    assert set(validation.index).isdisjoint(locked.index)


def test_authentic_policy_events_share_rounds_budget_and_fixed_artifact_hashes():
    base = ROOT / "results/canonical/authentic/audit_20261120_07"
    manifest = json.loads((base / "run_manifest.json").read_text(encoding="utf-8"))
    events_path = base / "authentic_test_events.csv"
    summary_path = base / "authentic_test_summary.csv"
    assert sha256(events_path) == manifest["outputs_sha256"][events_path.name]
    assert sha256(summary_path) == manifest["outputs_sha256"][summary_path.name]
    events = pd.read_csv(events_path)
    sizes = events.groupby("round_id")["policy"].nunique()
    assert sizes.nunique() == 1
    assert (events["budget"] == 3).all()
    assert (events["selected_sites"].str.split("|").str.len() <= events["budget"]).all()
    assert events.groupby("round_id")["available_sites"].nunique().eq(1).all()
    assert events.groupby("round_id")["available_positives"].nunique().eq(1).all()


def test_unseen_site_subgroup_is_disjoint_from_training_sites():
    frame = _authentic_frame()
    train_sites = set(frame.loc[frame.round_date <= "2024-05-31", "samplingPoint.notation"].astype(str))
    locked = frame[frame.round_date >= "2024-10-01"]
    unseen = locked[~locked["samplingPoint.notation"].astype(str).isin(train_sites)]
    assert len(unseen) == 50
    assert set(unseen["samplingPoint.notation"].astype(str)).isdisjoint(train_sites)
