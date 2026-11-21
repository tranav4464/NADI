"""Create a hash-anchored reproducibility manifest for the NADI build."""
from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "reproducibility_manifest_v1.json"

FILES = [
    "configs/locked_benchmark_v4.json",
    "configs/benchmark_v5_no_placeholders.json",
    "data_processed/risk_model_card.json",
    "data_processed/hydraulic_ensemble.json",
    "results/locked/benchmark_v5_no_placeholders_summary.json",
    "results/locked/benchmark_v5_no_placeholders_aggregate.csv",
    "results/locked/benchmark_v5_no_placeholders_events.csv",
    "results/bristol_telemetry_audit_v1.json",
    "results/performance_matrix_v1.json",
    "results/sdaif_ablations_v1.json",
    "results/prior_art_repository_audit_v1.json",
    "results/authentic_prior_art_replication_v1.json",
    "results/open_ecoli_real_data_reconstruction_v1.json",
    "results/ea_ecoli_authentic_baseline_v1.json",
    "results/ea_ecoli_physchem_panel_v1.json",
    "results/authentic_build_status_v1.json",
    "results/lira_piped_water_audit.json",
    "results/authentic_locked/authentic_experiment_report.json",
    "results/authentic_locked/authentic_test_summary.csv",
    "results/authentic_locked/authentic_test_events.csv",
    "results/authentic_locked/authentic_locked_site_predictions_and_zones.csv",
    "results/wdseventdb_event_holdout_v1.json",
    "results/open_ecoli_prior_art_adaptation_v1.json",
    "results/ea_ecoli_physchem_geographic_holdout_v1.json",
    "provenance/resource_manifest.json",
    "../nadi_resources/datasets/EA_ECOLI_AUTHENTIC/ea_ecoli_confirmed_mf_2024.csv",
    "../nadi_resources/datasets/EA_ECOLI_AUTHENTIC/ea_ecoli_confirmed_mf_2024.json",
    "../nadi_resources/datasets/EA_ECOLI_AUTHENTIC/ea_ecoli_physchem_panel_q1_2024.csv",
    "../nadi_resources/datasets/EA_ECOLI_AUTHENTIC/ea_ecoli_physchem_panel_q1_2024.json",
    "../nadi_resources/datasets/EA_ECOLI_AUTHENTIC/ecoli_2348_q1_2024.csv",
    "../nadi_resources/datasets/EA_ECOLI_AUTHENTIC/ph_0061_q1_2024.csv",
    "../nadi_resources/datasets/EA_ECOLI_AUTHENTIC/temperature_0076_q1_2024.csv",
    "../nadi_resources/datasets/EA_ECOLI_AUTHENTIC/conductivity_0077_q1_2024.csv",
    "../nadi_resources/datasets/EA_ECOLI_AUTHENTIC/ea_openmeteo_weather_panel_q1_2024.csv",
    "../nadi_resources/datasets/EA_ECOLI_AUTHENTIC/ea_openmeteo_weather_panel_q1_2024.json",
    "results/ea_weather_enriched_holdout_v1.json",
    "results/texas_physical_pressure_v1.json",
    "../nadi_resources/datasets/EA_ECOLI_AUTHENTIC/ammoniacal_n_0111_q1_2024.csv",
    "src/nadi/sdaif/engine.py",
    "src/nadi/sdaif/fusion.py",
    "src/nadi/telemetry/normal.py",
    "src/nadi/hazards/intrusion.py",
    "src/nadi/hydraulics/pressure_features.py",
    "src/nadi/decision/actions.py",
    "src/nadi/authentic/models.py",
    "src/nadi/authentic/policy.py",
    "src/nadi/authentic/benchmark.py",
    "src/nadi/pilot/schema.py",
    "src/nadi/microbial_risk/lira.py",
    "scripts/run_authentic_xylem_experiment.py",
    "scripts/audit_lira_piped_water.py",
    "scripts/audit_xylem_submission_pack.py",
    "scripts/audit_prospective_pilot_bundle.py",
    "scripts/evaluate_texas_physical_pressure.py",
    "app/server.py",
    "app/templates/authentic.html",
    "app/static/authentic.js",
    "docs/MATHEMATICAL_ASSURANCE_CASE.md",
    "docs/XYLEM_APPLICATION_DRAFT.md",
    "docs/XYLEM_EVIDENCE_PACK.md",
    "docs/XYLEM_FINAL_HANDOFF.md",
    "docs/PROSPECTIVE_AUTHENTIC_PILOT_PROTOCOL.md",
    "docs/AUTHENTIC_BUILD_COMPLETION_AUDIT.md",
    "docs/TEXAS_PHYSICAL_NETWORK_EVIDENCE.md",
    "docs/FINAL_GOAL_REQUIREMENTS_AUDIT.md",
    "docs/PARTNER_DATA_REQUEST.md",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def main() -> dict:
    files = {}
    missing = []
    for relative in FILES:
        path = ROOT / relative
        if path.exists():
            files[relative] = {"bytes": path.stat().st_size, "sha256": sha256(path)}
        else:
            missing.append(relative)
    # Exclude this self-referential check: the manifest does not exist with a
    # current green status until this command completes.
    # Meta-tests consume this manifest, so exclude them while rebuilding it;
    # the subsequent full-suite run verifies they pass against the fresh file.
    completed = subprocess.run(
        [str(ROOT / ".venv" / "Scripts" / "python.exe"), "-m", "pytest", "-q",
         "--ignore", "tests/test_repro_manifest.py", "--ignore", "tests/test_dashboard.py",
         "--ignore", "tests/test_claim_boundaries.py"],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    manifest = {
        "manifest_id": "NADI-REPRODUCIBILITY-V1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "test_command": ".venv/Scripts/python.exe -m pytest -q --ignore tests/test_repro_manifest.py --ignore tests/test_dashboard.py --ignore tests/test_claim_boundaries.py",
        "test_exit_code": completed.returncode,
        "test_summary": completed.stdout.strip().splitlines()[-1] if completed.stdout.strip() else "",
        "files": files,
        "missing_expected_files": missing,
        "claim_boundary": "Hashes prove artifact identity and test reproducibility only; they do not establish field or biological validity.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return manifest


if __name__ == "__main__":
    main()
