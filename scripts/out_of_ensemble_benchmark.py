"""Frozen Net3 parameter-shift stress test for sequential test selection."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from nadi.evaluation.metrics import testing_metrics
from nadi.hydraulics.ensemble import load_reference_ensemble
from nadi.hydraulics.generate import _simulate
from nadi.pipeline.demo import _adaptive_sequence
from nadi.policies.baselines import adaptive_bayesian_sequence, select_all
from nadi.sdaif.engine import AdaptiveSDAIF
from nadi.sdaif.delayed import delayed_test_sequence


def run(protocol: dict) -> dict:
    ensemble_path = Path(protocol["ensemble_path"]) if "ensemble_path" in protocol else None
    network_path = Path(protocol["network_path"]) if "network_path" in protocol else None
    ensemble = load_reference_ensemble(protocol["candidate_count"], ensemble_path)
    candidates = list(ensemble.candidates)
    weights = ensemble.consequence_weights
    budget = protocol["budget"]
    vertices = [{"vertex_id": s.scenario_id, "risk": 1.0,
                 "affected": sorted(s.affected.intersection(candidates))}
                for s in ensemble.scenarios]
    known_signatures = {tuple(node in s.affected for node in candidates) for s in ensemble.scenarios}
    reach = {node: sum(node in s.affected for s in ensemble.scenarios) / len(ensemble.scenarios)
             for node in candidates}
    propensities = {node: 1.0 for node in candidates}
    events = []
    for index, case in enumerate(protocol["hidden_cases"]):
        # Label contains full-precision factors; the original frozen ensemble
        # and its output files are never overwritten.
        label = f"shift-{index:02d}-src-{case['source']}-d-{case['demand_multiplier']}-t-{case['tank_fraction']}-pipe-{case['closed_pipe']}"
        kwargs = {"network": network_path} if network_path is not None else {}
        hidden = _simulate(**case, label_override=label, **kwargs)
        affected = set(hidden["affected"]).intersection(candidates)
        signature = tuple(node in affected for node in candidates)
        engine = AdaptiveSDAIF(epsilon=0.15, test_cost=0.02)
        selected, steps, initial, final = _adaptive_sequence(engine, candidates, vertices, weights, budget, affected)
        baselines = select_all(candidates, reach, weights, vertices, budget, 20261118 + index, 0.02, propensities)
        plans = {
            "random": baselines["random"], "routine": baselines["routine"],
            "hydraulic_only": baselines["hydraulic_only"], "bayesian": baselines["bayesian"],
            "adaptive_bayesian": adaptive_bayesian_sequence(candidates, vertices, weights, budget, affected),
            "adaptive_sdaif": selected,
        }
        if "delayed_sdaif_1" in protocol["comparators"]:
            plans["delayed_sdaif_1"] = delayed_test_sequence(
                engine, candidates, vertices, weights, budget, affected,
                extra_result_rounds=1,
            )["selected"]
        events.append({
            "hidden_case": case,
            "hidden_scenario_id": hidden["scenario_id"],
            "affected_candidates": sorted(affected),
            "signature_in_reference_ensemble": signature in known_signatures,
            "initial_sdaif_certificate": initial.get("certified", False),
            "final_sdaif_status": final["status"],
            "sdaif_tests_before_stop": len(steps),
            "policies": {name: {"selected": plan, **testing_metrics(plan, affected, weights)} for name, plan in plans.items()},
        })
    summary = {
        "protocol_id": protocol["protocol_id"],
        "reference_scenarios": len(ensemble.scenarios),
        "hidden_cases": len(events),
        "nonempty_cases": sum(bool(e["affected_candidates"]) for e in events),
        "unrepresented_reach_signatures": sum(not e["signature_in_reference_ensemble"] for e in events),
        "sdaif_final_abstentions": sum(e["final_sdaif_status"] == "ABSTAIN" for e in events),
        "mean_coverage_nonempty": {
            name: float(np.mean([e["policies"][name]["coverage_at_k"] for e in events if e["affected_candidates"]]))
            for name in protocol["comparators"]
        },
        "events": events,
        "claim_boundary": protocol["claim_boundary"],
    }
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("configs/out_of_ensemble_v1.json"))
    parser.add_argument("--output", type=Path, default=Path("results/out_of_ensemble_v1.json"))
    args = parser.parse_args()
    protocol = json.loads(args.config.read_text(encoding="utf-8"))
    result = run(protocol)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "events"}, indent=2))


if __name__ == "__main__":
    main()
