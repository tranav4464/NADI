from __future__ import annotations

import hashlib
from collections import defaultdict
from typing import Any, Mapping

import numpy as np
import pandas as pd

from .policy import authentic_sdaif_sequence, update_model_weights


def _stable_random_order(round_id: str, sites: list[str]) -> list[str]:
    return sorted(sites, key=lambda site: hashlib.sha256(f"{round_id}|{site}|NADI-2026".encode()).hexdigest())


def _bayesian_sequence(
    predictions: Mapping[str, Mapping[str, float]],
    weights: Mapping[str, float], truth: Mapping[str, bool], budget: int,
) -> list[str]:
    observed: dict[str, bool] = {}
    selected: list[str] = []
    for _ in range(min(budget, len(truth))):
        posterior, _ = update_model_weights(predictions, weights, observed)
        remaining = [site for site in truth if site not in observed]
        means = {
            site: sum(posterior[model] * predictions[model][site] for model in posterior)
            for site in remaining
        }
        site = max(remaining, key=lambda value: (means[value], value))
        selected.append(site)
        observed[site] = bool(truth[site])
    return selected


def evaluate_authentic_rounds(
    frame: pd.DataFrame,
    model_probabilities: Mapping[str, np.ndarray],
    initial_model_weights: Mapping[str, float],
    best_model: str,
    budget: int = 3,
    robustness_weight: float = 0.25,
    min_sites: int = 5,
    max_sites: int = 25,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    data = frame.copy().reset_index(drop=True)
    for name, values in model_probabilities.items():
        data[f"prob_{name}"] = np.asarray(values, dtype=float)
    rows: list[dict[str, Any]] = []
    for round_id, group in data.groupby("round_id", sort=True):
        if not min_sites <= len(group) <= max_sites:
            continue
        group = group.copy()
        sites = group["samplingPoint.notation"].astype(str).tolist()
        truth = dict(zip(sites, group["high_500"].astype(bool)))
        predictions = {
            model: dict(zip(sites, group[f"prob_{model}"].astype(float)))
            for model in model_probabilities
        }
        ensemble = {
            site: sum(initial_model_weights[m] * predictions[m][site] for m in predictions)
            for site in sites
        }
        selections: dict[str, list[str]] = {
            "random": _stable_random_order(str(round_id), sites)[:budget],
            "routine_sampling_frequency": group.sort_values(
                ["site_prior_samples", "samplingPoint.notation"], ascending=[False, True]
            )["samplingPoint.notation"].astype(str).head(budget).tolist(),
            "historical_positive_rate": group.sort_values(
                ["site_prior_positive_rate", "samplingPoint.notation"], ascending=[False, True]
            )["samplingPoint.notation"].astype(str).head(budget).tolist(),
            "best_single_model": sorted(sites, key=lambda site: (-predictions[best_model][site], site))[:budget],
            "fixed_ensemble": sorted(sites, key=lambda site: (-ensemble[site], site))[:budget],
            "adaptive_bayesian": _bayesian_sequence(predictions, initial_model_weights, truth, budget),
        }
        sdaif = authentic_sdaif_sequence(
            predictions, initial_model_weights, truth, budget, robustness_weight
        )
        selections["adaptive_sdaif"] = sdaif["selected"]
        positives = int(sum(truth.values()))
        oracle_found = min(budget, positives)
        for policy, selected in selections.items():
            outcomes = [int(truth[site]) for site in selected]
            found = int(sum(outcomes))
            first = next((index + 1 for index, outcome in enumerate(outcomes) if outcome), budget + 1)
            rows.append({
                "round_id": round_id, "policy": policy, "available_sites": len(sites),
                "available_positives": positives, "budget": budget,
                "selected_sites": "|".join(selected), "selected_outcomes": "|".join(map(str, outcomes)),
                "positives_found": found, "fraction_available_positives_found": found / positives if positives else np.nan,
                "tests_to_first_positive": first, "missed_positive_round": int(positives > 0 and found == 0),
                "oracle_positives_found": oracle_found, "positive_discovery_regret": oracle_found - found,
                "tests_per_positive": len(selected) / found if found else np.nan,
                "data_origin": "AUTHENTIC_OBSERVED",
            })
    events = pd.DataFrame(rows)
    summaries = []
    for policy, group in events.groupby("policy", sort=True):
        positive_rounds = group[group["available_positives"] > 0]
        summaries.append({
            "policy": policy, "rounds": len(group),
            "mean_positives_found_at_budget": float(group["positives_found"].mean()),
            "total_positives_found": int(group["positives_found"].sum()),
            "mean_positive_discovery_regret": float(group["positive_discovery_regret"].mean()),
            "mean_tests_to_first_positive_positive_rounds": float(positive_rounds["tests_to_first_positive"].mean()),
            "missed_positive_round_rate": float(positive_rounds["missed_positive_round"].mean()),
            "mean_fraction_available_positives_found": float(positive_rounds["fraction_available_positives_found"].mean()),
            "data_origin": "AUTHENTIC_OBSERVED",
        })
    return events, pd.DataFrame(summaries)


def round_bootstrap_interval(
    events: pd.DataFrame, policy: str, metric: str, replicates: int = 1000, seed: int = 2026,
) -> dict[str, float]:
    values = events.loc[events["policy"] == policy, metric].dropna().to_numpy(dtype=float)
    if len(values) == 0:
        return {"estimate": float("nan"), "lower_95": float("nan"), "upper_95": float("nan")}
    rng = np.random.default_rng(seed)
    means = np.asarray([rng.choice(values, size=len(values), replace=True).mean() for _ in range(replicates)])
    return {
        "estimate": float(values.mean()), "lower_95": float(np.quantile(means, 0.025)),
        "upper_95": float(np.quantile(means, 0.975)),
    }


def paired_bootstrap_difference(
    events: pd.DataFrame, policy_a: str, policy_b: str, metric: str,
    replicates: int = 2000, seed: int = 2026,
) -> dict[str, float]:
    wide = events.pivot(index="round_id", columns="policy", values=metric).dropna(subset=[policy_a, policy_b])
    differences = (wide[policy_a] - wide[policy_b]).to_numpy(dtype=float)
    rng = np.random.default_rng(seed)
    means = np.asarray([
        rng.choice(differences, size=len(differences), replace=True).mean()
        for _ in range(replicates)
    ])
    return {
        "policy_a": policy_a, "policy_b": policy_b, "metric": metric,
        "rounds": int(len(differences)), "estimate_a_minus_b": float(differences.mean()),
        "lower_95": float(np.quantile(means, 0.025)),
        "upper_95": float(np.quantile(means, 0.975)),
    }
