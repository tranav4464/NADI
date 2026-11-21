"""Run prespecified SDAIF ablations on the locked simulated decision task.

The ablations change one mathematical ingredient at a time while keeping
hidden scenarios, seeds and test budget fixed. Results are tracer-reach
decision evidence, not biological validation.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from nadi.evaluation.metrics import testing_metrics
from nadi.hydraulics.ensemble import load_reference_ensemble, scenario_vertices
from nadi.microbial_risk.weather_model import load_bundle
from nadi.paths import INTERIM_ROOT, RESULTS_ROOT
from nadi.pipeline.demo import _adaptive_sequence, _input_record
from nadi.policies.baselines import select_all
from nadi.sdaif.engine import AdaptiveSDAIF, robust_plan
from nadi.transfer.gate import enforce_domain
from nadi.types import RiskEstimate

ROOT = Path(__file__).resolve().parents[1]
OUT = RESULTS_ROOT / "sdaif_ablations_v1.json"


def _point(risk: RiskEstimate, low: float, high: float) -> RiskEstimate:
    return RiskEstimate(
        probability=risk.probability, lower=low, upper=high, endpoint=risk.endpoint,
        horizon_hours=risk.horizon_hours, evidence_domain="SIMULATED_NETWORK_EVENT",
        calibrated=risk.calibrated, model_version=risk.model_version + "+ablation",
        support_score=risk.support_score, features=risk.features,
    )


def main() -> dict:
    config = json.loads((ROOT / "configs" / "default.json").read_text())
    bundle = load_bundle()
    ensemble = load_reference_ensemble(12)
    candidates = list(ensemble.candidates)
    full_weights = ensemble.consequence_weights
    uniform_weights = {node: 1.0 for node in candidates}
    frame = pd.read_csv(INTERIM_ROOT / "wqp_marion_weather.csv", parse_dates=["date"])
    cols = [c for c in frame.columns if c.startswith("prcp_") or c.startswith("tavg_")] + ["month_sin", "month_cos"]
    data = frame[(frame["date"] >= "2021-01-01") & (frame["date"] <= "2022-12-31")].dropna(subset=cols).reset_index(drop=True)
    variants = {"full": [], "point_risk": [], "wide_risk": [], "uniform_consequence": [], "single_network_scenario": [], "static_robust": []}
    seeds = [20261117, 20261118, 20261119]
    for seed in seeds:
        rng = np.random.default_rng(seed)
        offsets = rng.choice(len(data), size=40, replace=False)
        for offset in offsets:
            row = data.iloc[int(offset)]
            record = {key: float(row[key]) for key in row.index if key.startswith("prcp_") or key.startswith("tavg_") or key in ("month_sin", "month_cos")}
            risk = enforce_domain(bundle["forecast"].predict(record), "SIMULATED_NETWORK_EVENT", allow_simulated_bridge=True)
            hidden = ensemble.scenarios[int(rng.integers(0, len(ensemble.scenarios)))]
            affected = set(hidden.affected).intersection(candidates)
            definitions = {
                "full": (risk, full_weights, ensemble.scenarios),
                "point_risk": (_point(risk, risk.probability, risk.probability), full_weights, ensemble.scenarios),
                "wide_risk": (_point(risk, 0.0, 1.0), full_weights, ensemble.scenarios),
                "uniform_consequence": (risk, uniform_weights, ensemble.scenarios),
                "single_network_scenario": (risk, full_weights, (ensemble.scenarios[0],)),
            }
            for name, (variant_risk, weights, scenarios) in definitions.items():
                # Rebuild vertices from the selected scenario subset so this is
                # a true ablation, not a post-hoc metric change.
                vertices = []
                for probability in sorted(set([variant_risk.lower, variant_risk.upper])):
                    for scenario in scenarios:
                        vertices.append({"vertex_id": f"{name}:{probability}:{scenario.scenario_id}", "risk": probability,
                                         "scenario_id": scenario.scenario_id,
                                         "affected": sorted(set(scenario.affected).intersection(candidates)),
                                         "state_probability": 1.0 / len(scenarios), "origin": "SIMULATED"})
                if name == "static_robust":
                    continue
                engine = AdaptiveSDAIF(config["decision"]["epsilon_regret"], config["decision"]["test_cost"])
                selected, _, initial, _ = _adaptive_sequence(engine, candidates, vertices, weights, 3, affected)
                variants[name].append({"coverage": testing_metrics(selected, affected, weights)["coverage_at_k"],
                                       "regret": initial.get("worst_case_regret"),
                                       "certified": bool(initial.get("certified", False)),
                                       "empty": not bool(affected)})
            # Static robust uses the full uncertainty set and no result-adaptive branch.
            vertices = scenario_vertices(ensemble, risk)
            selected, bound, _ = robust_plan(candidates, vertices, full_weights, 3, config["decision"]["test_cost"])
            variants["static_robust"].append({"coverage": testing_metrics(selected, affected, full_weights)["coverage_at_k"],
                                               "regret": bound, "certified": bound <= config["decision"]["epsilon_regret"], "empty": not bool(affected)})
    summary = {"protocol_id": "SDAIF-ABLATION-V1", "events": len(variants["full"]), "variants": {}}
    for name, rows in variants.items():
        nonempty = [r for r in rows if not r["empty"]]
        summary["variants"][name] = {
            "nonempty_events": len(nonempty),
            "mean_coverage_at_3": float(np.mean([r["coverage"] for r in nonempty])) if nonempty else None,
            "mean_worst_case_regret": float(np.mean([r["regret"] for r in nonempty])) if nonempty else None,
            "certificate_rate": float(np.mean([r["certified"] for r in nonempty])) if nonempty else None,
        }
    summary["claim_boundary"] = "All outcomes are simulated EPANET/WNTR tracer reach; ablations test mathematical components, not E. coli detection or field performance."
    OUT.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    main()
