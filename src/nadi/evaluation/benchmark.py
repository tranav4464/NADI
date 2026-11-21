from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from ..evaluation.metrics import testing_metrics
from ..hydraulics.ensemble import load_reference_ensemble, scenario_vertices
from ..microbial_risk.weather_model import load_bundle
from ..paths import INTERIM_ROOT, RESULTS_ROOT
from ..pipeline.demo import _adaptive_sequence
from ..policies.baselines import adaptive_bayesian_sequence, select_all
from ..sdaif.engine import AdaptiveSDAIF
from ..transfer.gate import enforce_domain


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _canonical_hash(payload: dict) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest().upper()


def _records() -> pd.DataFrame:
    frame = pd.read_csv(INTERIM_ROOT / "wqp_marion_weather.csv", parse_dates=["date"])
    columns = [name for name in frame.columns if name.startswith("prcp_") or name.startswith("tavg_")] + ["month_sin", "month_cos"]
    return frame[(frame["date"] >= "2021-01-01") & (frame["date"] <= "2022-12-31")].dropna(subset=columns).reset_index(drop=True)


def _record(row: pd.Series) -> dict[str, float]:
    return {key: float(row[key]) for key in row.index if key.startswith("prcp_") or key.startswith("tavg_") or key in ("month_sin", "month_cos")}


def _decision_regret(selected: list[str], affected: set[str], weights: dict[str, float], budget: int) -> float:
    total = sum(weights[node] for node in affected)
    if total <= 0:
        return 0.0
    captured = sum(weights[node] for node in selected if node in affected)
    oracle = sum(sorted((weights[node] for node in affected), reverse=True)[:budget])
    return float(max(0.0, (oracle - captured) / total))


def _bootstrap_difference(adaptive: np.ndarray, comparator: np.ndarray, repeats: int, seed: int) -> dict:
    delta = adaptive - comparator
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, len(delta), size=(repeats, len(delta)))
    means = delta[indices].mean(axis=1)
    return {
        "mean_difference": float(delta.mean()),
        "paired_bootstrap_95pct": [float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))],
    }


def run_locked(
    config: dict, benchmark_config: dict, output_name: str = "locked_benchmark_v1", output_dir: Path | None = None,
) -> dict:
    data = _records()
    bundle = load_bundle()
    ensemble = load_reference_ensemble(benchmark_config["candidate_count"])
    candidates = list(ensemble.candidates)
    reach = {item.node_id: item.probability for item in ensemble.reach_estimates()}
    propensities = {node: 0.2 + 0.6 * (index + 1) / len(candidates) for index, node in enumerate(candidates)}
    rows = []
    abstentions = 0
    for seed in benchmark_config["seeds"]:
        rng = np.random.default_rng(seed)
        offsets = rng.choice(len(data), size=benchmark_config["event_count_per_seed"], replace=False)
        for event_index, offset in enumerate(offsets):
            source_row = data.iloc[int(offset)]
            risk = bundle["forecast"].predict(_record(source_row))
            risk = enforce_domain(risk, "SIMULATED_NETWORK_EVENT", allow_simulated_bridge=True)
            if risk.abstain:
                abstentions += 1
                continue
            vertices = scenario_vertices(ensemble, risk)
            hidden = ensemble.scenarios[int(rng.integers(0, len(ensemble.scenarios)))]
            affected = set(hidden.affected).intersection(candidates)
            event_id = f"{seed}-{event_index:03d}"
            for budget in benchmark_config["budgets"]:
                baselines = select_all(candidates, reach, ensemble.consequence_weights, vertices, budget, seed + event_index, config["decision"]["test_cost"], propensities)
                engine = AdaptiveSDAIF(config["decision"]["epsilon_regret"], config["decision"]["test_cost"])
                selected, _, initial, _ = _adaptive_sequence(engine, candidates, vertices, ensemble.consequence_weights, budget, affected)
                plans = {name: plan for name, plan in baselines.items()
                         if name in benchmark_config["policies"]}
                if "adaptive_sdaif" in benchmark_config["policies"]:
                    plans["adaptive_sdaif"] = selected
                if "adaptive_bayesian" in benchmark_config["policies"]:
                    plans["adaptive_bayesian"] = adaptive_bayesian_sequence(
                        candidates, vertices, ensemble.consequence_weights, budget, affected
                    )
                for policy, plan in plans.items():
                    metrics = testing_metrics(plan, affected, ensemble.consequence_weights)
                    rows.append({
                        "event_id": event_id,
                        "seed": seed,
                        "budget": budget,
                        "policy": policy,
                        "scenario_id": hidden.scenario_id,
                        "risk_probability": risk.probability,
                        "risk_lower": risk.lower,
                        "risk_upper": risk.upper,
                        "selected": "|".join(plan),
                        **metrics,
                        "true_regret": _decision_regret(plan, affected, ensemble.consequence_weights, budget),
                        "scenario_conditional_initial_certificate": bool(initial.get("certified", False)) if policy == "adaptive_sdaif" else False,
                    })
    table = pd.DataFrame(rows)
    if table.empty:
        raise RuntimeError("Locked benchmark produced no supported events")
    output_dir = output_dir or (RESULTS_ROOT / "locked")
    output_dir.mkdir(parents=True, exist_ok=True)
    table_path = output_dir / f"{output_name}_events.csv"
    table.to_csv(table_path, index=False, lineterminator="\n")
    aggregate = table.groupby(["budget", "policy"], as_index=False).agg(
        events=("event_id", "nunique"),
        nonempty_events=("empty_event", lambda x: int((~x).sum())),
        empty_events=("empty_event", "sum"),
        mean_coverage=("coverage_at_k", "mean"),
        mean_population_coverage=("population_weighted_coverage", "mean"),
        missed_event_rate=("missed_positive_event", "mean"),
        mean_true_regret=("true_regret", "mean"),
        initial_certificate_rate=("scenario_conditional_initial_certificate", "mean"),
    )
    aggregate_path = output_dir / f"{output_name}_aggregate.csv"
    aggregate.to_csv(aggregate_path, index=False, lineterminator="\n")
    primary = table[table["budget"] == benchmark_config["primary_budget"]]
    nonempty = primary[~primary["empty_event"]]
    pivot = nonempty.pivot(index="event_id", columns="policy", values=benchmark_config["primary_metric"])
    if pivot.empty or pivot.isna().any().any():
        raise RuntimeError("Primary metric requires complete nonempty paired events")
    baseline_names = [name for name in benchmark_config["policies"] if name != "adaptive_sdaif"]
    baseline_means = {name: float(pivot[name].mean()) for name in baseline_names}
    strongest = max(baseline_means, key=lambda name: (baseline_means[name], name))
    comparison = _bootstrap_difference(
        pivot["adaptive_sdaif"].to_numpy(), pivot[strongest].to_numpy(),
        benchmark_config["bootstrap_repetitions"], 20261118,
    )
    margin = benchmark_config["equivalence_margin"]
    equivalent = comparison["mean_difference"] >= -margin
    superior = comparison["paired_bootstrap_95pct"][0] > 0
    summary = {
        "benchmark_id": benchmark_config["benchmark_id"],
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "events_attempted": len(benchmark_config["seeds"]) * benchmark_config["event_count_per_seed"],
        "events_evaluated": int(primary["event_id"].nunique()),
        "nonempty_events_evaluated": int(nonempty["event_id"].nunique()),
        "empty_events_evaluated": int(primary["event_id"].nunique() - nonempty["event_id"].nunique()),
        "abstentions": abstentions,
        "primary_budget": benchmark_config["primary_budget"],
        "primary_metric": benchmark_config["primary_metric"],
        "strongest_fair_baseline": strongest,
        "strongest_baseline_mean": baseline_means[strongest],
        "adaptive_mean": float(pivot["adaptive_sdaif"].mean()),
        "comparison": comparison,
        "equivalent_within_margin": bool(equivalent),
        "superiority_supported": bool(superior),
        "gate": "PASS" if equivalent else "PIVOT",
        "config_sha256": _canonical_hash(benchmark_config),
        "event_table_sha256": _hash(table_path),
        "aggregate_sha256": _hash(aggregate_path),
        "information_contract": benchmark_config["information_contract"],
        "claim_boundary": benchmark_config["claim_boundary"],
        "negative_result_rule": "No superiority claim unless the paired 95% interval is above zero; equivalence is reported separately.",
        "certificate_boundary": "Initial next-test regret bound only, conditional on enumerated scenarios and risk interval; not a biological or real-world safety certificate.",
    }
    (output_dir / f"{output_name}_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary

