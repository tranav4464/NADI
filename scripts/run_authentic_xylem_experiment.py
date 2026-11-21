from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import joblib
from sklearn.metrics import log_loss

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from nadi.authentic.benchmark import (
    evaluate_authentic_rounds, paired_bootstrap_difference, round_bootstrap_interval,
)
from nadi.authentic.models import (
    TARGET, classification_metrics, model_family, select_threshold,
)
from nadi.authentic.spatial import assign_monitoring_zones


def _json_default(value):
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
    raise TypeError(type(value).__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run NADI's authentic-only locked Xylem experiment")
    parser.add_argument("--input", type=Path, default=ROOT / "data_processed" / "ea_authentic_site_rounds_2024.csv")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results" / "authentic_locked")
    parser.add_argument("--budget", type=int, default=3)
    parser.add_argument("--model-bundle", type=Path, help="Optional calibrated canonical model bundle")
    args = parser.parse_args()

    frame = pd.read_csv(args.input, parse_dates=["round_date", "feature_cutoff"])
    train = frame[frame["round_date"] <= "2024-05-31"].copy()
    calibration = frame[(frame["round_date"] >= "2024-06-01") & (frame["round_date"] <= "2024-07-15")].copy()
    validation = frame[(frame["round_date"] >= "2024-07-16") & (frame["round_date"] <= "2024-09-30")].copy()
    locked_test = frame[frame["round_date"] >= "2024-10-01"].copy()
    if min(map(len, (train, calibration, validation, locked_test))) == 0:
        raise RuntimeError("A chronological split is empty")

    if args.model_bundle:
        models = joblib.load(args.model_bundle)
        if set(models) != {"logistic", "xgboost", "hist_gradient"}:
            raise ValueError("Canonical bundle has an unexpected model family")
        if any(model.calibrator is None for model in models.values()):
            raise ValueError("Canonical model bundle is not calibrated")
    else:
        models = model_family(2026)
        for model in models.values():
            model.fit(train, calibration)

    validation_probabilities = {name: model.predict_proba(validation) for name, model in models.items()}
    test_probabilities = {name: model.predict_proba(locked_test) for name, model in models.items()}
    model_reports = {}
    weights_raw = {}
    for name in models:
        threshold = select_threshold(validation[TARGET].to_numpy(), validation_probabilities[name])
        model_reports[name] = {
            "threshold_selected_on_validation": threshold,
            "validation": classification_metrics(validation[TARGET].to_numpy(), validation_probabilities[name], threshold),
            "locked_test": classification_metrics(locked_test[TARGET].to_numpy(), test_probabilities[name], threshold),
        }
        weights_raw[name] = float(np.exp(-log_loss(validation[TARGET], validation_probabilities[name], labels=[0, 1])))
    total = sum(weights_raw.values())
    weights = {name: value / total for name, value in weights_raw.items()}
    best_model = max(models, key=lambda name: (model_reports[name]["validation"]["pr_auc"], model_reports[name]["validation"]["balanced_accuracy"]))
    validation_matrix = np.column_stack([validation_probabilities[name] for name in sorted(validation_probabilities)])
    test_matrix = np.column_stack([test_probabilities[name] for name in sorted(test_probabilities)])
    disagreement_cutoff = float(np.quantile(validation_matrix.std(axis=1), 0.95))
    supported_test = test_matrix.std(axis=1) <= disagreement_cutoff
    training_sites = set(train["samplingPoint.notation"].astype(str))
    unseen_site_mask = ~locked_test["samplingPoint.notation"].astype(str).isin(training_sites).to_numpy()
    threshold = model_reports[best_model]["threshold_selected_on_validation"]
    subgroup_reports = {
        "supported_by_validation_disagreement_gate": {
            "records": int(supported_test.sum()), "coverage": float(supported_test.mean()),
            "metrics": classification_metrics(
                locked_test[TARGET].to_numpy()[supported_test], test_probabilities[best_model][supported_test], threshold
            ),
        },
        "sites_unseen_during_model_training": {
            "records": int(unseen_site_mask.sum()),
            "unique_sites": int(locked_test.loc[unseen_site_mask, "samplingPoint.notation"].nunique()),
            "metrics": classification_metrics(
                locked_test[TARGET].to_numpy()[unseen_site_mask], test_probabilities[best_model][unseen_site_mask], threshold
            ),
        },
    }
    region_reports = {}
    for region, indices in locked_test.groupby("region").groups.items():
        position = locked_test.index.get_indexer(indices)
        labels = locked_test.loc[indices, TARGET].to_numpy()
        if len(indices) >= 20 and len(np.unique(labels)) == 2:
            region_reports[str(region)] = classification_metrics(labels, test_probabilities[best_model][position], threshold)

    baseline_reports = {
        "always_positive": classification_metrics(
            locked_test[TARGET].to_numpy(), np.ones(len(locked_test)), 0.5
        ),
        "training_prevalence_constant": classification_metrics(
            locked_test[TARGET].to_numpy(), np.full(len(locked_test), train[TARGET].mean()), 0.5
        ),
    }

    tuning = []
    for robustness in (0.0, 0.25, 0.5, 0.75, 1.0):
        events, summary = evaluate_authentic_rounds(
            validation, validation_probabilities, weights, best_model,
            budget=args.budget, robustness_weight=robustness,
        )
        row = summary[summary["policy"] == "adaptive_sdaif"].iloc[0].to_dict()
        row["robustness_weight"] = robustness
        tuning.append(row)
    tuning.sort(key=lambda row: (
        -row["mean_positives_found_at_budget"],
        row["mean_positive_discovery_regret"],
        row["missed_positive_round_rate"],
        row["robustness_weight"],
    ))
    chosen_robustness = float(tuning[0]["robustness_weight"])

    test_events, test_summary = evaluate_authentic_rounds(
        locked_test, test_probabilities, weights, best_model,
        budget=args.budget, robustness_weight=chosen_robustness,
    )
    intervals = {
        policy: {
            metric: round_bootstrap_interval(test_events, policy, metric, 2000)
            for metric in ("positives_found", "positive_discovery_regret", "missed_positive_round")
        }
        for policy in sorted(test_events["policy"].unique())
    }
    paired_policy_comparisons = [
        paired_bootstrap_difference(test_events, "adaptive_sdaif", comparator, "positives_found")
        for comparator in ("random", "routine_sampling_frequency", "best_single_model", "adaptive_bayesian")
    ]

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    locked_locations = assign_monitoring_zones(
        locked_test,
        test_probabilities[best_model],
        model_reports[best_model]["threshold_selected_on_validation"],
    )
    probability_matrix = test_matrix
    for name in sorted(test_probabilities):
        locked_locations[f"probability_{name}"] = test_probabilities[name]
    locked_locations["model_probability_mean"] = probability_matrix.mean(axis=1)
    locked_locations["model_probability_std"] = probability_matrix.std(axis=1)
    locked_locations["within_validation_disagreement_support"] = supported_test
    locked_locations["site_unseen_during_model_training"] = unseen_site_mask
    locked_locations["uncertainty_origin"] = "DISAGREEMENT_AMONG_CALIBRATED_AUTHENTIC_DATA_MODELS"
    locked_locations.to_csv(output_dir / "authentic_locked_site_predictions_and_zones.csv", index=False)
    test_events.to_csv(output_dir / "authentic_test_events.csv", index=False)
    test_summary.to_csv(output_dir / "authentic_test_summary.csv", index=False)
    report = {
        "experiment": "NADI_XYLEM_AUTHENTIC_ONLY_V1",
        "data_policy": {
            "observed_records_only": True,
            "synthetic_records_used": False,
            "simulated_records_used": False,
            "endpoint": "laboratory E. coli result >=500 in the authentic EA record",
            "domain": "UK Environment Agency surface-water monitoring; not drinking-water pipes",
        },
        "source": str(args.input.resolve()),
        "model_bundle": str(args.model_bundle.resolve()) if args.model_bundle else "TRAINED_AND_CALIBRATED_IN_PROCESS",
        "processed_input_sha256": hashlib.sha256(args.input.read_bytes()).hexdigest(),
        "chronological_splits": {
            "train_through": "2024-05-31", "calibration": "2024-06-01/2024-07-15",
            "validation": "2024-07-16/2024-09-30", "locked_test": "2024-10-01/2024-12-31",
            "counts": {"train": len(train), "calibration": len(calibration), "validation": len(validation), "locked_test": len(locked_test)},
        },
        "leakage_control": "Features for every date were frozen before any laboratory result from that date updated history.",
        "model_reports": model_reports,
        "classification_baselines": baseline_reports,
        "model_uncertainty_weights_from_validation_log_loss": weights,
        "best_model_selected_on_validation": best_model,
        "transfer_and_subgroup_audit": {
            "model_disagreement_cutoff_selected_as_validation_95th_percentile": disagreement_cutoff,
            "subgroups": subgroup_reports,
            "regions_with_at_least_20_records_and_both_classes": region_reports,
            "interpretation": "Unseen-site rows have local past-history features but their sites supplied no model-training labels.",
        },
        "sdaif_tuning_on_validation_only": tuning,
        "selected_sdaif_robustness_weight": chosen_robustness,
        "locked_policy_summary": test_summary.to_dict("records"),
        "locked_round_bootstrap_95_intervals": intervals,
        "locked_paired_policy_comparisons": paired_policy_comparisons,
        "claim_boundary": (
            "This experiment validates retrospective prioritisation among authentically sampled surface-water sites. "
            "It does not validate direct E. coli detection, a drinking-water pipeline, a contaminated branch, or Delhi-NCR deployment."
        ),
    }
    (output_dir / "authentic_experiment_report.json").write_text(
        json.dumps(report, indent=2, default=_json_default), encoding="utf-8"
    )
    (output_dir / "LOCKED_COMPLETE.txt").write_text(
        "Completed with authentic observed records only. See authentic_experiment_report.json.\n", encoding="utf-8"
    )
    print(json.dumps({
        "best_model": best_model,
        "selected_robustness_weight": chosen_robustness,
        "locked_rounds": int(test_events["round_id"].nunique()),
        "locked_summary": test_summary.to_dict("records"),
        "output_dir": str(output_dir),
    }, indent=2, default=_json_default))


if __name__ == "__main__":
    main()
