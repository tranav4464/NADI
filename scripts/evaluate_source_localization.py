"""Evaluate source ranking using frozen simulated test lists and hidden cases."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from nadi.hydraulics.ensemble import load_reference_ensemble
from nadi.hydraulics.localize import source_consistency


def run(event_file: Path, ensemble_path: Path | None, candidate_count: int = 12) -> dict:
    events = json.loads(event_file.read_text(encoding="utf-8"))["events"]
    ensemble = load_reference_ensemble(candidate_count, ensemble_path)
    known_sources = {scenario.source for scenario in ensemble.scenarios}
    policies = ["adaptive_sdaif", "adaptive_bayesian", "hydraulic_only", "random"]
    records = []
    for event in events:
        true_source = event["hidden_case"]["source"]
        affected = set(event["affected_candidates"])
        for policy in policies:
            selected = event["policies"][policy]["selected"]
            for stage, tested_count in (("first", min(1, len(selected))),
                                        ("budget3", min(3, len(selected)))):
                observed = {node: node in affected for node in selected[:tested_count]}
                result = source_consistency(ensemble, observed)
                top = result["ranked_sources"][0]["source"] if result["ranked_sources"] else None
                records.append({"case": event["hidden_scenario_id"], "policy": policy,
                                "stage": stage, "tests": tested_count, "true_source": true_source,
                                "true_source_enumerated": true_source in known_sources,
                                "status": result["status"], "top_source": top,
                                "top1_correct": top == true_source,
                                "compatible_scenarios": result["compatible_scenarios"]})
    summary = {}
    for policy in policies:
        rows = [row for row in records if row["policy"] == policy and row["stage"] == "budget3"]
        known = [row for row in rows if row["true_source_enumerated"]]
        unknown = [row for row in rows if not row["true_source_enumerated"]]
        summary[policy] = {
            "cases": len(rows), "known_source_cases": len(known),
            "known_source_top1_correct": sum(row["top1_correct"] for row in known),
            "known_source_out_of_model": sum(row["status"] == "OUT_OF_MODEL" for row in known),
            "unseen_source_cases": len(unknown),
            "unseen_source_false_attribution": sum(row["status"] == "IN_MODEL" for row in unknown),
            "unseen_source_out_of_model": sum(row["status"] == "OUT_OF_MODEL" for row in unknown),
        }
    return {"ensemble_network": ensemble.network, "enumerated_sources": sorted(known_sources),
            "summary_after_three_tests": summary, "records": records,
            "claim_boundary": "Source ranking is conditional on simulated tracer outcomes and enumerated scenarios, not a field E. coli origin estimate."}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--ensemble", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.events, args.ensemble)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["summary_after_three_tests"], indent=2))


if __name__ == "__main__":
    main()
