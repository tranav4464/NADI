"""Guarded wrapper for the audited retrospective EA experiment."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from nadi.core.layout import load_layout, sha256  # noqa: E402


SOURCES = [
    "scripts/canonical/run_authentic.py",
    "scripts/run_authentic_xylem_experiment.py",
    "src/nadi/core/layout.py",
    "src/nadi/canonical_cli.py",
    "src/nadi/authentic/models.py",
    "src/nadi/authentic/benchmark.py",
    "src/nadi/authentic/policy.py",
    "src/nadi/authentic/spatial.py",
    "src/nadi/sdaif/engine.py",
]


def run(config: Path, run_id: str) -> Path:
    layout = load_layout(config)
    expected = {
        "workflow": "authentic_xylem",
        "input": "data_processed/ea_authentic_site_rounds_2024.csv",
        "output_root": "results/canonical/authentic",
        "input_sha256": "5b2b9f0388a2a713eb31c961f05dc1f64142a65b06ad267714a60d38acf295da",
        "preparation_manifest": "results/canonical/preparation/audit_20261120_01/run_manifest.json",
        "calibration_manifest": "results/canonical/risk_calibration/audit_20261120_01/run_manifest.json",
        "seed": 2026,
        "budget": 3,
        "endpoint": "E_COLI_GE_500_PER_100ML_PROJECT_HIGH_COUNT",
        "result_timing": "HISTORICAL_SAME_ROUND_REVEAL_ONLY",
        "train_through": "2024-05-31",
        "calibration": ["2024-06-01", "2024-07-15"],
        "validation": ["2024-07-16", "2024-09-30"],
        "test": ["2024-10-01", "2024-12-31"],
    }
    for key, value in expected.items():
        if layout.raw.get(key) != value:
            raise ValueError(f"The current audited implementation requires {key}={value!r}")
    if layout.evidence_class != "LAB_CONFIRMED" or layout.domain != "UK_EA_MIXED_ENVIRONMENTAL_WATER_ECOLI":
        raise ValueError("This runner accepts only the audited mixed EA environmental-water domain")
    if layout.input_sha256 != expected["input_sha256"]:
        raise ValueError("The audited processed input has changed; do not reuse this experiment label")
    upstream_path = ROOT / layout.raw["preparation_manifest"]
    upstream = json.loads(upstream_path.read_text(encoding="utf-8"))
    if upstream.get("status") != "PASS" or upstream.get("command") != "prepare-authentic":
        raise ValueError("The pinned preparation run did not pass")
    processed_name = "ea_authentic_site_rounds_2024.csv"
    prepared_path = Path(upstream["output_dir"]) / processed_name
    if (not prepared_path.is_file() or upstream.get("outputs_sha256", {}).get(processed_name) != layout.input_sha256
            or sha256(prepared_path) != layout.input_sha256):
        raise ValueError("The prepared table differs from the evaluation input")
    calibration_manifest_path = ROOT / layout.raw["calibration_manifest"]
    calibration_manifest = json.loads(calibration_manifest_path.read_text(encoding="utf-8"))
    bundle_name = "calibrated_models.joblib"
    bundle_path = Path(calibration_manifest["output_dir"]) / bundle_name
    if (calibration_manifest.get("command") != "calibrate-risk" or calibration_manifest.get("status") != "PASS"
            or calibration_manifest.get("input_sha256") != layout.input_sha256
            or not bundle_path.is_file()
            or calibration_manifest.get("outputs_sha256", {}).get(bundle_name) != sha256(bundle_path)):
        raise ValueError("The pinned calibrated model bundle did not pass verification")

    output = layout.create_output(run_id)
    command = [sys.executable, str(ROOT / "scripts" / "run_authentic_xylem_experiment.py"),
               "--input", str(layout.input_path), "--output-dir", str(output),
               "--budget", str(layout.raw["budget"]), "--model-bundle", str(bundle_path)]
    started = datetime.now(timezone.utc).isoformat()
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    (output / "stdout.log").write_text(completed.stdout, encoding="utf-8")
    (output / "stderr.log").write_text(completed.stderr, encoding="utf-8")
    products = {
        path.name: sha256(path)
        for path in sorted(output.iterdir()) if path.is_file() and path.name not in {"run_manifest.json"}
    }
    manifest = {
        "canonical_command": "evaluate-authentic",
        "workflow": "authentic_xylem",
        "status": "PASS" if completed.returncode == 0 else "FAILED",
        "started_utc": started,
        "finished_utc": datetime.now(timezone.utc).isoformat(),
        "run_id": run_id,
        "command": command,
        "returncode": completed.returncode,
        "evidence_class": layout.evidence_class,
        "domain": layout.domain,
        "result_timing": layout.raw["result_timing"],
        "input_path": str(layout.input_path),
        "input_sha256": layout.input_sha256,
        "preparation_manifest_path": str(upstream_path),
        "preparation_manifest_sha256": sha256(upstream_path),
        "calibration_manifest_path": str(calibration_manifest_path),
        "calibration_manifest_sha256": sha256(calibration_manifest_path),
        "calibration_bundle_path": str(bundle_path),
        "calibration_bundle_sha256": sha256(bundle_path),
        "config_path": str(layout.config_path),
        "config_sha256": layout.config_sha256,
        "seed": layout.seed,
        "source_sha256": {name: sha256(ROOT / name) for name in SOURCES},
        "output_dir": str(output),
        "outputs_sha256": products,
        "claim_boundary": "Retrospective UK EA mixed environmental-water testing priority; no drinking-pipe biological validation.",
    }
    (output / "run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    if completed.returncode:
        raise RuntimeError(f"Authentic run failed; inspect {output / 'stderr.log'}")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    print(run(args.config, args.run_id))


if __name__ == "__main__":
    main()
