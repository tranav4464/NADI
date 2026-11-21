from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from ..evaluation.metrics import testing_metrics
from ..hydraulics.ensemble import load_reference_ensemble, scenario_vertices
from ..microbial_risk.weather_model import load_bundle
from ..paths import INTERIM_ROOT, RESULTS_ROOT
from ..policies.baselines import select_all
from ..decision.actions import rank_protective_actions
from ..hazards.intrusion import estimate_intrusion_hazard
from ..sdaif.fusion import EvidenceInterval, fuse_evidence
from ..sdaif.engine import AdaptiveSDAIF
from ..transfer.gate import enforce_domain
from ..types import DecisionCard


def _input_record(seed: int) -> tuple[str, dict]:
    frame = pd.read_csv(INTERIM_ROOT / "wqp_marion_weather.csv", parse_dates=["date"])
    test = frame[(frame["date"] >= "2021-01-01") & (frame["date"] <= "2022-12-31")].copy()
    test = test.dropna(subset=["prcp_prev_1d", "prcp_prev_3d", "prcp_prev_10d", "prcp_prev_15d", "tavg_prev_1d", "month_sin", "month_cos"])
    row = test.iloc[seed % len(test)]
    record = {key: float(row[key]) for key in row.index if key.startswith("prcp_") or key.startswith("tavg_") or key in ("month_sin", "month_cos")}
    return f"WQP-{row['site_id']}-{row['date'].date()}", record


def _adaptive_sequence(engine: AdaptiveSDAIF, candidates: list[str], vertices: list[dict], weights: dict[str, float], budget: int, hidden_affected: set[str]) -> tuple[list[str], list[dict], dict, dict]:
    observed: dict[str, bool] = {}
    selected: list[str] = []
    steps = []
    result = {}
    initial = engine.recommend(candidates, vertices, weights, budget, observed)
    for step in range(budget):
        result = initial if step == 0 else engine.recommend(candidates, vertices, weights, budget, observed)
        if result["status"] != "OK" or not result["selected_tests"]:
            break
        node = result["selected_tests"][0]
        if node in observed:
            break
        outcome = node in hidden_affected
        selected.append(node)
        steps.append({
            "step": step + 1,
            "selected_test": node,
            "result_revealed_after_selection": outcome,
            "pre_result_worst_case_regret": result["worst_case_regret"],
            "compatible_scenarios_before": result["compatible_scenarios"],
        })
        observed[node] = outcome
    final = engine.recommend(candidates, vertices, weights, budget, observed)
    return selected, steps, initial, final


def run_demo(config: dict, seed: int, budget: int, requested_domain: str = "SIMULATED_NETWORK_EVENT") -> dict:
    event_id, record = _input_record(seed)
    bundle = load_bundle()
    nowcast = bundle["nowcast"].predict(record)
    forecast = bundle["forecast"].predict(record)
    risk = enforce_domain(forecast, requested_domain, allow_simulated_bridge=requested_domain == "SIMULATED_NETWORK_EVENT")
    # No sewage/pipe-defect observations are supplied by the public benchmark;
    # expose the optional hazard layer as unsupported rather than inventing it.
    intrusion_hazard = estimate_intrusion_hazard({})
    fusion_inputs = [EvidenceInterval(
        name="calibrated_weather_risk", probability=forecast.probability,
        lower=forecast.lower, upper=forecast.upper, reliability=1.0,
        support=forecast.support_score, domain=forecast.evidence_domain,
    )]
    if intrusion_hazard.support > 0:
        fusion_inputs.append(EvidenceInterval(
            name="intrusion_hazard", probability=intrusion_hazard.score,
            lower=intrusion_hazard.lower, upper=intrusion_hazard.upper,
            reliability=0.6, support=intrusion_hazard.support, domain="HAZARD_CONTEXT",
        ))
    fused_evidence = fuse_evidence(fusion_inputs)
    ensemble = load_reference_ensemble(config["hydraulics"]["candidate_count"])
    vertices = scenario_vertices(ensemble, risk)
    reach = ensemble.reach_estimates()
    reach_probability = {item.node_id: item.probability for item in reach}
    candidates = list(ensemble.candidates)
    propensities = {node: 0.2 + 0.6 * (index + 1) / len(candidates) for index, node in enumerate(candidates)}
    baselines = select_all(
        candidates, reach_probability, ensemble.consequence_weights, vertices,
        budget, seed, config["decision"]["test_cost"], propensities,
    )
    if risk.abstain:
        card = DecisionCard(
            event_id=event_id, selected_tests=[], alternative_policies=baselines,
            worst_case_regret=None, epsilon=config["decision"]["epsilon_regret"], certified=False,
            abstained=True, abstention_reason=risk.abstention_reason, adversarial_scenario=None,
            next_evidence_value=[], dominant_uncertainty="domain transfer",
            evidence_labels=["LAB_CONFIRMED:source dataset", "MODEL_ESTIMATE:risk", "SIMULATED:network"],
            model_versions={"nowcast": nowcast.model_version, "forecast": forecast.model_version, "hydraulics": ensemble.source_hash[:12], "decision": "adaptive-sdaif-v1"},
            claim_boundary="No action recommendation is issued outside calibrated support.",
            response_guidance=["Request independent microbiological confirmation and review the unsupported domain before using this model."],
        )
        payload = {
            "schema_version": "0.1.0",
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "seed": seed,
            "budget": budget,
            "event_origin": "SIMULATED",
            "input_reference": event_id,
            "decision_card": card.to_dict(),
            "nowcast": asdict(nowcast),
            "forecast": asdict(forecast),
            "risk_after_transfer_gate": asdict(risk),
            "intrusion_hazard": intrusion_hazard.to_dict(),
            "fused_evidence": fused_evidence.to_dict(),
            "affected_region": [],
            "protective_actions": rank_protective_actions([], risk.upper),
            "adaptive_steps": [],
        }
    else:
        rng = np.random.default_rng(seed)
        hidden = ensemble.scenarios[int(rng.integers(0, len(ensemble.scenarios)))]
        hidden_affected = set(hidden.affected).intersection(candidates)
        engine = AdaptiveSDAIF(config["decision"]["epsilon_regret"], config["decision"]["test_cost"])
        selected, steps, initial, final = _adaptive_sequence(engine, candidates, vertices, ensemble.consequence_weights, budget, hidden_affected)
        dominant = "risk interval" if (risk.upper - risk.lower) >= np.std(list(reach_probability.values())) else "network scenario"
        card = DecisionCard(
            event_id=event_id,
            selected_tests=selected,
            alternative_policies=baselines,
            worst_case_regret=initial.get("worst_case_regret"),
            epsilon=config["decision"]["epsilon_regret"],
            certified=bool(initial.get("certified", False)) and final["status"] == "OK",
            abstained=final["status"] != "OK",
            abstention_reason=final.get("reason") if final["status"] != "OK" else None,
            adversarial_scenario=initial.get("adversarial_scenario"),
            next_evidence_value=initial.get("next_evidence_value", [])[:5],
            dominant_uncertainty=dominant,
            evidence_labels=["LAB_CONFIRMED:surface-water source", "OBSERVED:NOAA weather", "MODEL_ESTIMATE:calibrated risk", "SIMULATED:Net3 affected region", "SIMULATED:hidden outcome"],
            model_versions={"nowcast": nowcast.model_version, "forecast": forecast.model_version, "hydraulics": ensemble.source_hash[:12], "decision": "adaptive-sdaif-v1"},
            claim_boundary="Software benchmark only. Confirmatory microbiology remains required; network reach is simulated, not Delhi field evidence.",
            response_guidance=final.get("response_guidance", ["Confirm with laboratory sampling; a utility operator must assess any warning, isolation or flushing action."]),
        )
        metrics = {"adaptive_sdaif": testing_metrics(selected, hidden_affected, ensemble.consequence_weights)}
        for name, plan in baselines.items():
            metrics[name] = testing_metrics(plan, hidden_affected, ensemble.consequence_weights)
        payload = {
            "schema_version": "0.1.0",
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "seed": seed,
            "budget": budget,
            "event_origin": "SIMULATED",
            "input_reference": event_id,
            "nowcast": asdict(nowcast),
            "forecast": asdict(forecast),
            "risk_after_transfer_gate": asdict(risk),
            "intrusion_hazard": intrusion_hazard.to_dict(),
            "fused_evidence": fused_evidence.to_dict(),
            "affected_region": [asdict(item) for item in reach],
            "protective_actions": rank_protective_actions([asdict(item) for item in reach], risk.upper),
            "adaptive_steps": steps,
            "decision_card": card.to_dict(),
            "metrics": metrics,
            "hidden_truth_disclosed_after_decisions": {"scenario_id": hidden.scenario_id, "affected_candidates": sorted(hidden_affected)},
        }
    run_dir = RESULTS_ROOT / "runs"
    run_dir.mkdir(parents=True, exist_ok=True)
    target = run_dir / f"demo_seed-{seed}_budget-{budget}.json"
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload

