"""Resolve a pinned, hash-verified authentic replay for the dashboard."""
from __future__ import annotations

import json
from pathlib import Path

from nadi.core.layout import ROOT, sha256


REQUIRED = (
    "authentic_experiment_report.json",
    "authentic_locked_site_predictions_and_zones.csv",
    "authentic_test_events.csv",
    "authentic_test_summary.csv",
)


def authentic_run(config_path: Path | None = None) -> tuple[Path, dict]:
    config_path = config_path or ROOT / "configs" / "canonical" / "dashboard.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    run_id = config["authentic_run_id"]
    if not run_id or any(char not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for char in run_id):
        raise ValueError("Invalid pinned authentic run ID")
    base = ROOT / "results" / "canonical" / "authentic" / run_id
    manifest = json.loads((base / "run_manifest.json").read_text(encoding="utf-8"))
    if manifest.get("status") != "PASS" or manifest.get("workflow") != "authentic_xylem":
        raise ValueError("Pinned run did not pass the authentic workflow")
    for field, key in (("evidence_class", "authentic_evidence_class"), ("domain", "authentic_domain")):
        if manifest.get(field) != config[key]:
            raise ValueError(f"Pinned run has a different {field}")
    products = manifest.get("outputs_sha256", {})
    for name in REQUIRED:
        path = base / name
        if not path.is_file() or sha256(path) != products.get(name):
            raise ValueError(f"Pinned authentic artifact failed hash verification: {name}")
    return base, manifest
