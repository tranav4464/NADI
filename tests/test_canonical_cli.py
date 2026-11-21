import json
from dataclasses import replace
from pathlib import Path

import pytest
import pandas as pd

import nadi.canonical_cli as cli
from nadi.core.layout import ROOT, load_layout, sha256


def test_verify_data_checks_causal_rows_and_writes_auditable_manifest(tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "ROOT", tmp_path)
    output = cli.verify_data(ROOT / "configs/canonical/authentic_xylem.json", "test_read")
    result = json.loads((output / "data_verification.json").read_text(encoding="utf-8"))
    manifest = json.loads((output / "run_manifest.json").read_text(encoding="utf-8"))
    assert result["status"] == "PASS"
    assert result["checks"]["rows"] == 13405
    assert result["checks"]["duplicate_site_dates"] == 0
    assert result["checks"]["feature_cutoff_on_or_after_round"] == 0
    assert manifest["outputs_sha256"]["data_verification.json"]
    with pytest.raises(FileExistsError):
        cli.verify_data(ROOT / "configs/canonical/authentic_xylem.json", "test_read")


def test_verify_data_rejects_changed_input_identity_before_writing(tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "ROOT", tmp_path)
    config = json.loads((ROOT / "configs/canonical/authentic_xylem.json").read_text(encoding="utf-8"))
    config["input_sha256"] = "0" * 64
    config_path = tmp_path / "changed.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")
    with pytest.raises(ValueError, match="Input bytes differ"):
        cli.verify_data(config_path, "changed")
    assert not (tmp_path / "results/canonical/audit/changed").exists()


def test_preparation_matches_pinned_raw_and_processed_data():
    config = ROOT / "configs/canonical/prepare_authentic.json"
    layout = load_layout(config)
    assert layout.input_sha256 == layout.raw["input_sha256"]


def test_preparation_reproduces_processed_table_in_isolated_run(tmp_path, monkeypatch):
    config = ROOT / "configs/canonical/prepare_authentic.json"
    layout = load_layout(config)
    isolated = replace(layout, output_root=tmp_path / "results/canonical/preparation")
    monkeypatch.setattr(cli, "ROOT", tmp_path)
    monkeypatch.setattr(cli, "load_layout", lambda _: isolated)
    output = cli.prepare_authentic(config, "test_prepare")
    manifest = json.loads((output / "run_manifest.json").read_text(encoding="utf-8"))
    processed = output / "ea_authentic_site_rounds_2024.csv"
    assert sha256(processed) == sha256(ROOT / "data_processed/ea_authentic_site_rounds_2024.csv")
    assert manifest["outputs_sha256"][processed.name] == sha256(processed)
    with pytest.raises(FileExistsError):
        cli.prepare_authentic(config, "test_prepare")


def test_canonical_training_and_calibration_artifacts_have_linked_identity():
    training = ROOT / "results/canonical/risk_training/audit_20261120_01/run_manifest.json"
    calibration = ROOT / "results/canonical/risk_calibration/audit_20261120_01/run_manifest.json"
    train = json.loads(training.read_text(encoding="utf-8"))
    calibrated = json.loads(calibration.read_text(encoding="utf-8"))
    bundle = Path(calibrated["output_dir"]) / "calibrated_models.joblib"
    assert train["command"] == "train-risk"
    assert calibrated["command"] == "calibrate-risk"
    assert calibrated["input_sha256"] == train["input_sha256"]
    assert calibrated["training_manifest_sha256"] == sha256(training)
    assert calibrated["outputs_sha256"][bundle.name] == sha256(bundle)


def test_random_permutation_baseline_is_reproducible_and_respects_budget():
    table = pd.DataFrame({
        "round_id": ["r1"] * 4 + ["r2"] * 4,
        "samplingPoint.notation": list("abcd") + list("efgh"),
        "high_500": [1, 1, 0, 0, 1, 0, 0, 0],
    })
    first = cli._random_permutation_totals(table, ["r1", "r2"], budget=2, repetitions=50, seed=2026)
    second = cli._random_permutation_totals(table, ["r1", "r2"], budget=2, repetitions=50, seed=2026)
    assert (first == second).all()
    assert first.min() >= 0
    assert first.max() <= 3
