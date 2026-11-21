"""Fail closed if the Xylem narrative drifts from NADI's locked evidence."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def main() -> dict:
    required = [
        "docs/XYLEM_APPLICATION_DRAFT.md",
        "docs/XYLEM_2MIN_PITCH.md",
        "docs/XYLEM_3_TO_4_MINUTE_VIDEO_SCRIPT.md",
        "docs/MATHEMATICAL_ASSURANCE_CASE.md",
        "docs/PROSPECTIVE_AUTHENTIC_PILOT_PROTOCOL.md",
        "docs/XYLEM_FINAL_HANDOFF.md",
        "docs/XYLEM_EVIDENCE_PACK.md",
        "results/authentic_locked/authentic_experiment_report.json",
        "results/authentic_locked/authentic_test_summary.csv",
    ]
    missing = [name for name in required if not (ROOT / name).exists()]
    if missing:
        raise RuntimeError(f"Xylem pack is incomplete: {missing}")
    report = json.loads((ROOT / "results/authentic_locked/authentic_experiment_report.json").read_text(encoding="utf-8"))
    if report["data_policy"].get("synthetic_records_used") or report["data_policy"].get("simulated_records_used"):
        raise RuntimeError("Xylem authentic pack cannot use synthetic or simulated records")
    summary = pd.read_csv(ROOT / "results/authentic_locked/authentic_test_summary.csv").set_index("policy")
    counts = {
        "adaptive": int(summary.loc["adaptive_sdaif", "total_positives_found"]),
        "random": int(summary.loc["random", "total_positives_found"]),
        "routine": int(summary.loc["routine_sampling_frequency", "total_positives_found"]),
    }
    if counts != {"adaptive": 114, "random": 80, "routine": 84}:
        raise RuntimeError(f"Locked result differs from approved submission values: {counts}")
    application = (ROOT / "docs/XYLEM_APPLICATION_DRAFT.md").read_text(encoding="utf-8")
    required_phrases = (
        "**114**", "**80**", "**84**", "does **not** establish direct E. coli detection",
        "drinking-water-pipeline tracing", "Delhi-NCR performance", "illness reduction",
    )
    absent = [phrase for phrase in required_phrases if phrase not in application]
    if absent:
        raise RuntimeError(f"Application narrative lost required result/boundary language: {absent}")
    handoff = (ROOT / "docs/XYLEM_FINAL_HANDOFF.md").read_text(encoding="utf-8")
    if "1:00 PM ET, 20 November 2026" not in handoff:
        raise RuntimeError("Final handoff lacks conservative deadline")
    evidence_pack = (ROOT / "docs/XYLEM_EVIDENCE_PACK.md").read_text(encoding="utf-8")
    canonical_phrases = (
        "## Canonical locked authentic results",
        "F1 0.838; ROC-AUC 0.866; PR-AUC 0.916",
        "114 confirmed high results",
        "80 confirmed high results",
        "84 confirmed high results",
        "not pooled with the canonical experiment",
    )
    absent = [phrase for phrase in canonical_phrases if phrase not in evidence_pack]
    if absent:
        raise RuntimeError(f"Evidence pack lost canonical-experiment separation: {absent}")
    return {
        "status": "PASS",
        "authentic_only": True,
        "locked_counts": counts,
        "required_files": len(required),
        "claim_boundary_verified": True,
    }


if __name__ == "__main__":
    print(json.dumps(main(), indent=2))
