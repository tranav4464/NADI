"""Build the transparent NADI performance matrix from frozen result files."""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def wilson(successes: int, total: int, z: float = 1.96) -> list[float]:
    if total <= 0:
        return [None, None]
    p = successes / total
    denominator = 1.0 + z * z / total
    centre = (p + z * z / (2.0 * total)) / denominator
    radius = z * math.sqrt((p * (1.0 - p) + z * z / (4.0 * total)) / total) / denominator
    return [max(0.0, centre - radius), min(1.0, centre + radius)]


def main() -> dict:
    # The production training command writes the frozen model card to the
    # project processed-data directory. Never consume a stale exploratory
    # selection artefact from results/.
    risk = load("data_processed/risk_model_card.json")
    gecco = load("results/gecco_event_v1.json")
    v5 = load("results/locked/benchmark_v5_no_placeholders_summary.json")
    ltown = load("results/ltown_decision_stress_v1.json")
    ea = load("results/ea_ecoli_authentic_baseline_v1.json")
    panel = load("results/ea_ecoli_physchem_panel_v1.json")
    geo = load("results/ea_ecoli_physchem_geographic_holdout_v1.json")
    weather = load("results/ea_weather_enriched_holdout_v1.json")
    locked_authentic = load("results/authentic_locked/authentic_experiment_report.json")
    texas = load("results/texas_physical_pressure_v1.json")
    locked_test = locked_authentic["model_reports"][locked_authentic["best_model_selected_on_validation"]]["locked_test"]
    locked_confusion = locked_test["confusion_matrix"]
    matrix = {
        "protocol_id": "NADI-PERFORMANCE-MATRIX-V1",
        "target_note": "85% is an aspirational target, not a result; each endpoint keeps its own metric and claim boundary.",
        "rows": [
            {
                "track": "canonical_locked_authentic_ea_risk",
                "endpoint": locked_authentic["claim_boundary"],
                "metric": "positive_f1",
                "value": locked_test["f1"],
                "accuracy": (locked_confusion["tn"] + locked_confusion["tp"]) / locked_test["n"],
                "precision": locked_test["precision"],
                "recall": locked_test["sensitivity"],
                "balanced_accuracy": locked_test["balanced_accuracy"],
                "auc": locked_test["roc_auc"],
                "pr_auc": locked_test["pr_auc"],
                "prevalence": locked_test["prevalence"],
                "status": "CANONICAL_AUTHENTIC_LOCKED_SURFACE_WATER",
            },
            {
                "track": "surface_water_nowcast",
                "endpoint": risk["nowcast"]["claim_boundary"],
                "metric": "positive_f1",
                "value": risk["nowcast"]["untouched_test_thresholded"]["positive_f1"],
                "accuracy": risk["nowcast"]["untouched_test_thresholded"]["accuracy"],
                "precision": risk["nowcast"]["untouched_test_thresholded"]["precision"],
                "recall": risk["nowcast"]["untouched_test_thresholded"]["recall"],
                "auc": risk["nowcast"]["untouched_test"]["roc_auc"],
                "prevalence": risk["nowcast"]["untouched_test_thresholded"]["prevalence"],
                "false_negatives": risk["nowcast"]["untouched_test_thresholded"]["fn"],
                "true_positives": risk["nowcast"]["untouched_test_thresholded"]["tp"],
                "calibration_ece": risk["nowcast"]["untouched_test"]["ece_10"],
                "recall_wilson_95": wilson(risk["nowcast"]["untouched_test_thresholded"]["tp"], risk["nowcast"]["untouched_test_thresholded"]["tp"] + risk["nowcast"]["untouched_test_thresholded"]["fn"]),
                "status": "MEASURED_NOT_85",
            },
            {
                "track": "surface_water_24h_forecast",
                "endpoint": risk["forecast_24h"]["claim_boundary"],
                "metric": "positive_f1",
                "value": risk["forecast_24h"]["untouched_test_thresholded"]["positive_f1"],
                "accuracy": risk["forecast_24h"]["untouched_test_thresholded"]["accuracy"],
                "precision": risk["forecast_24h"]["untouched_test_thresholded"]["precision"],
                "recall": risk["forecast_24h"]["untouched_test_thresholded"]["recall"],
                "auc": risk["forecast_24h"]["untouched_test"]["roc_auc"],
                "prevalence": risk["forecast_24h"]["untouched_test_thresholded"]["prevalence"],
                "false_negatives": risk["forecast_24h"]["untouched_test_thresholded"]["fn"],
                "true_positives": risk["forecast_24h"]["untouched_test_thresholded"]["tp"],
                "calibration_ece": risk["forecast_24h"]["untouched_test"]["ece_10"],
                "recall_wilson_95": wilson(risk["forecast_24h"]["untouched_test_thresholded"]["tp"], risk["forecast_24h"]["untouched_test_thresholded"]["tp"] + risk["forecast_24h"]["untouched_test_thresholded"]["fn"]),
                "status": "MEASURED_NOT_85",
            },
            {
                "track": "gecco_sensor_event",
                "endpoint": gecco["claim_boundary"],
                "metric": "positive_f1",
                "value": gecco["untouched_test"]["positive_f1"],
                "accuracy": gecco["untouched_test"]["accuracy"],
                "precision": gecco["untouched_test"]["precision"],
                "recall": gecco["untouched_test"]["recall"],
                "auc": gecco["untouched_test"]["roc_auc"],
                "prevalence": gecco["untouched_test"]["prevalence"],
                "false_negatives": gecco["untouched_test"]["fn"],
                "true_positives": gecco["untouched_test"]["tp"],
                "recall_wilson_95": wilson(gecco["untouched_test"]["tp"], gecco["untouched_test"]["tp"] + gecco["untouched_test"]["fn"]),
                "status": "MEASURED_PROXY_ONLY",
            },
            {
                "track": "sdaif_simulated_decision",
                "endpoint": v5["claim_boundary"],
                "metric": "coverage_at_3",
                "value": v5["adaptive_mean"],
                "baseline": v5["strongest_baseline_mean"],
                "status": "EQUIVALENT_NOT_SUPERIOR",
            },
            {
                "track": "ltown_decision_transfer",
                "endpoint": ltown["claim_boundary"],
                "metric": "coverage_at_3",
                "value": ltown["mean_coverage_nonempty"]["adaptive_sdaif"],
                "status": "TRANSFER_STRESS_NEGATIVE",
            },
            {
                "track": "ea_authentic_surface_water_ecoli",
                "endpoint": "Authentic England surface-water laboratory E. coli; not drinking-network validation",
                "metric": "positive_f1",
                "value": ea["models"]["hist_gradient_boosting"]["f1"],
                "accuracy": ea["models"]["hist_gradient_boosting"]["accuracy"],
                "precision": ea["models"]["hist_gradient_boosting"]["precision"],
                "recall": ea["models"]["hist_gradient_boosting"]["recall"],
                "auc": ea["models"]["hist_gradient_boosting"]["roc_auc"],
                "prevalence": ea["positive_prevalence"],
                "status": "AUTHENTIC_OBSERVED_SURFACE_WATER",
            },
            {
                "track": "ea_authentic_physchem_xgb",
                "endpoint": "Sample-matched pH/temperature/conductivity and laboratory E. coli detection; surface water only",
                "metric": "positive_f1",
                "value": panel["models"]["laboratory_detection"]["physicochemical_only"]["xgb_prior_art_reproduction"]["f1"],
                "accuracy": panel["models"]["laboratory_detection"]["physicochemical_only"]["xgb_prior_art_reproduction"]["accuracy"],
                "precision": panel["models"]["laboratory_detection"]["physicochemical_only"]["xgb_prior_art_reproduction"]["precision"],
                "recall": panel["models"]["laboratory_detection"]["physicochemical_only"]["xgb_prior_art_reproduction"]["recall"],
                "auc": panel["models"]["laboratory_detection"]["physicochemical_only"]["xgb_prior_art_reproduction"]["roc_auc"],
                "prevalence": panel["positive_prevalence"]["laboratory_detection"],
                "status": "AUTHENTIC_OBSERVED_PRIOR_ART_ADAPTATION",
            },
            {
                "track": "ea_authentic_unseen_site_xgb",
                "endpoint": geo["claim_boundary"],
                "metric": "positive_f1",
                "value": geo["models"]["xgb_prior_art_reproduction"]["f1"],
                "accuracy": geo["models"]["xgb_prior_art_reproduction"]["accuracy"],
                "precision": geo["models"]["xgb_prior_art_reproduction"]["precision"],
                "recall": geo["models"]["xgb_prior_art_reproduction"]["recall"],
                "auc": geo["models"]["xgb_prior_art_reproduction"]["roc_auc"],
                "status": "AUTHENTIC_OBSERVED_UNSEEN_LOCATION",
            },
            {
                "track": "ea_authentic_unseen_site_weather_xgb",
                "endpoint": weather["claim_boundary"],
                "metric": "positive_f1",
                "value": weather["metrics"]["f1"],
                "accuracy": weather["metrics"]["accuracy"],
                "precision": weather["metrics"]["precision"],
                "recall": weather["metrics"]["recall"],
                "auc": weather["metrics"]["roc_auc"],
                "status": "AUTHENTIC_OBSERVED_WEATHER_ENRICHED",
            },
            {
                "track": "texas_physical_pipe_pressure",
                "endpoint": texas["endpoint"],
                "metric": "roc_auc",
                "value": texas["out_of_fold_metrics"]["roc_auc"],
                "accuracy": texas["out_of_fold_metrics"]["accuracy"],
                "precision": texas["out_of_fold_metrics"]["precision"],
                "recall": texas["out_of_fold_metrics"]["recall"],
                "f1": texas["out_of_fold_metrics"]["f1"],
                "balanced_accuracy": texas["out_of_fold_metrics"]["balanced_accuracy"],
                "baseline_f1": texas["always_leak_baseline"]["f1"],
                "baseline_balanced_accuracy": texas["always_leak_baseline"]["balanced_accuracy"],
                "status": "AUTHENTIC_OBSERVED_PHYSICAL_HYDRAULIC_ONLY",
            },
        ],
        "global_claim_boundary": "No row establishes direct E. coli detection, Delhi-NCR field performance, reduced illness or municipal validation.",
    }
    out = ROOT / "results" / "performance_matrix_v1.json"
    out.write_text(json.dumps(matrix, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(matrix, indent=2))
    return matrix


if __name__ == "__main__":
    main()
