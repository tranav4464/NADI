"""Fail closed if generated NADI artefacts lose their evidence boundaries."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def main() -> int:
    checks = {
        "performance_matrix": _load("results/performance_matrix_v1.json"),
        "benchmark": _load("results/locked/benchmark_v5_no_placeholders_summary.json"),
        "bristol": _load("results/bristol_telemetry_audit_v1.json"),
        "manifest": _load("results/reproducibility_manifest_v1.json"),
        "prior_art": _load("results/prior_art_repository_audit_v1.json"),
        "replication": _load("results/authentic_prior_art_replication_v1.json"),
        "open_ecoli": _load("results/open_ecoli_real_data_reconstruction_v1.json"),
    }
    failures: list[str] = []
    matrix_boundary = checks["performance_matrix"].get("global_claim_boundary", "")
    if "direct E. coli" not in matrix_boundary or "field performance" not in matrix_boundary:
        failures.append("performance matrix boundary is incomplete")
    for name in ("benchmark", "bristol"):
        boundary = checks[name].get("claim_boundary", "")
        if not boundary:
            failures.append(f"{name} has no claim boundary")
    if checks["manifest"].get("test_exit_code") != 0:
        failures.append("reproducibility manifest records a failed core test run")
    for name, row in checks["prior_art"].get("repositories", {}).items():
        if row.get("status") != "DOWNLOADED" or row.get("replication_status") != "ACQUIRED_NOT_REPRODUCED":
            failures.append(f"prior-art status is ambiguous for {name}")
    if checks["replication"].get("tracks", {}).get("battledim_wntr", {}).get("status") != "REPRODUCED_SMOKE":
        failures.append("authentic BattLeDIM/WNTR smoke replication did not pass")
    if checks["open_ecoli"].get("original_workflow_status") != "NOT_BIT_FOR_BIT_REPRODUCED":
        failures.append("Open E. coli workflow boundary is ambiguous")
    if failures:
        for item in failures:
            print(f"FAIL: {item}")
        return 1
    print("PASS: generated artefacts retain explicit evidence and claim boundaries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
