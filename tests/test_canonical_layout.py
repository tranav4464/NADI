from dataclasses import replace
from pathlib import Path

import pytest

from nadi.core.layout import ROOT, load_layout, sha256


def test_canonical_config_identifies_input_and_domain():
    layout = load_layout(ROOT / "configs" / "canonical" / "authentic_xylem.json")
    assert layout.input_sha256 == sha256(layout.input_path)
    assert layout.domain == "UK_EA_MIXED_ENVIRONMENTAL_WATER_ECOLI"
    assert layout.evidence_class == "LAB_CONFIRMED"
    assert layout.output_root == ROOT / "results" / "canonical" / "authentic"
    assert layout.input_sha256 == layout.raw["input_sha256"]


def test_run_directory_must_be_new_and_inside_owned_root(tmp_path: Path):
    layout = load_layout(ROOT / "configs" / "canonical" / "authentic_xylem.json")
    isolated = replace(layout, output_root=tmp_path)
    created = isolated.create_output("audit_001")
    assert created.is_dir()
    with pytest.raises(FileExistsError):
        isolated.create_output("audit_001")
    with pytest.raises(ValueError):
        isolated.create_output("../results/locked")


def test_config_rejects_noncanonical_output(tmp_path: Path):
    config = tmp_path / "unsafe.json"
    config.write_text(
        '{"input":"data_processed/ea_authentic_site_rounds_2024.csv",'
        '"output_root":"results/authentic_locked",'
        '"evidence_class":"LAB_CONFIRMED","domain":"EA","seed":2026}',
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="results/canonical"):
        load_layout(config)
