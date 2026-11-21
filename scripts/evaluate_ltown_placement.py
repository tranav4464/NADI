"""Compare original and greedy source-discrimination placement on L-TOWN."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from nadi.evaluation.metrics import testing_metrics
from nadi.hydraulics.ensemble import HydraulicEnsemble, _stable_weight, load_reference_ensemble
from nadi.hydraulics.generate import _simulate
from nadi.hydraulics.localize import source_consistency
from nadi.hydraulics.placement import balanced_source_placement, distinguishable_cross_source_pairs, greedy_source_discrimination
from nadi.pipeline.demo import _adaptive_sequence
from nadi.sdaif.engine import AdaptiveSDAIF


def run(config: dict) -> dict:
    ensemble = load_reference_ensemble(config["candidate_budget"], Path(config["reference_ensemble"]))
    hidden_cases = json.loads(Path(config["hidden_protocol"]).read_text(encoding="utf-8"))["hidden_cases"]
    placements = {
        "original_round_robin": list(ensemble.candidates),
        "greedy_cross_source_pair_cover": greedy_source_discrimination(ensemble.scenarios, config["candidate_budget"]),
    }
    if "balanced_source_and_coverage" in config["strategies"]:
        placements["balanced_source_and_coverage"] = balanced_source_placement(
            ensemble.scenarios, config["candidate_budget"])
    hidden = [_simulate(**case, network=Path(config["network_path"]),
                        label_override=f"placement-hidden-{i:02d}-{case['source']}-{case['demand_multiplier']}")
              for i, case in enumerate(hidden_cases)]
    rows = []
    summary = {}
    for strategy, nodes in placements.items():
        weights = {node: _stable_weight(node) for node in nodes}
        placed = HydraulicEnsemble(ensemble.network, ensemble.scenarios, tuple(nodes), weights, ensemble.source_hash)
        pairs = distinguishable_cross_source_pairs(ensemble.scenarios, nodes)
        vertices = [{"vertex_id": scenario.scenario_id, "risk": 1.0,
                     "affected": sorted(scenario.affected.intersection(nodes))}
                    for scenario in ensemble.scenarios]
        for case, truth in zip(hidden_cases, hidden):
            affected = set(truth["affected"]).intersection(nodes)
            engine = AdaptiveSDAIF(0.15, 0.02)
            selected, _, _, final = _adaptive_sequence(engine, nodes, vertices, weights,
                                                        config["testing_budget"], affected)
            evidence = {node: node in affected for node in selected}
            localization = source_consistency(placed, evidence)
            top_source = localization["ranked_sources"][0]["source"] if localization["ranked_sources"] else None
            rows.append({"strategy": strategy, "hidden_case": case,
                         "affected_candidate_count": len(affected),
                         "selected": selected,
                         "coverage_at_3": testing_metrics(selected, affected, weights)["coverage_at_k"],
                         "source_top1_correct": top_source == case["source"],
                         "out_of_model": localization["status"] == "OUT_OF_MODEL",
                         "final_sdaif_status": final["status"]})
        own = [row for row in rows if row["strategy"] == strategy]
        valid = [row["coverage_at_3"] for row in own if row["coverage_at_3"] is not None]
        summary[strategy] = {"placement": nodes,
                             "cross_source_pairs_distinguished": pairs[0],
                             "cross_source_pairs_total": pairs[1],
                             "nonempty_hidden_cases": len(valid),
                             "mean_coverage_at_3_nonempty": sum(valid) / len(valid) if valid else None,
                             "source_top1_correct": sum(row["source_top1_correct"] for row in own),
                             "out_of_model_count": sum(row["out_of_model"] for row in own)}
    return {"protocol_id": config["protocol_id"], "summary": summary,
            "cases": rows, "claim_boundary": config["claim_boundary"]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("configs/ltown_placement_comparison_v1.json"))
    parser.add_argument("--output", type=Path, default=Path("results/ltown_placement_comparison_v1.json"))
    args = parser.parse_args()
    report = run(json.loads(args.config.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
    main()
