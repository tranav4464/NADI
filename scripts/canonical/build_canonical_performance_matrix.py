"""Build the evidence-separated performance matrix required for Phase 8."""
from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "reports" / "canonical_performance_matrix.csv"


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def row(track: str, dataset: str, status: str, split: str, count: str, metric: str, value: object,
        baseline: str, ci: str, randomization: str, artifact: str, command: str, limitation: str) -> dict:
    return {
        "track": track, "dataset": dataset, "evidence_status": status, "split": split,
        "sample_count": count, "metric": metric, "result": value, "baseline": baseline,
        "confidence_interval": ci, "randomization_method": randomization,
        "artifact_path": artifact, "code_command": command, "limitation": limitation,
    }


def main() -> None:
    auth_path = "results/canonical/authentic/audit_20261120_07/authentic_experiment_report.json"
    auth = load(auth_path)
    best = auth["best_model_selected_on_validation"]
    locked = auth["model_reports"][best]["locked_test"]
    summary_path = "results/canonical/authentic/audit_20261120_07/authentic_test_summary.csv"
    summary = list(csv.DictReader((ROOT / summary_path).open(encoding="utf-8")))
    policy = {item["policy"]: item for item in summary}
    decision_path = "results/canonical/decision/audit_20261120_03/sdaif_evaluation.json"
    decision = load(decision_path)
    random_dist = decision["random_permutation_distribution"]
    transfer_path = "results/ea_ecoli_physchem_geographic_holdout_v1.json"
    transfer = load(transfer_path)["models"]["xgb_prior_art_reproduction"]
    hydro_path = "results/canonical/hydraulics/audit_20261120_01/hydraulic_evaluation.json"
    hydro = load(hydro_path)
    net3_path = "results/canonical/simulation/audit_20261120_01/net3_simulation_summary.json"
    net3 = load(net3_path)
    ltown_path = "results/ltown_decision_stress_v1.json"
    ltown = load(ltown_path)
    gecco_path = "results/gecco_event_v1.json"
    gecco = load(gecco_path)["untouched_test"]
    texas_path = "results/texas_physical_pressure_v1.json"
    texas = load(texas_path)["out_of_fold_metrics"]
    prior_path = "results/open_ecoli_prior_art_adaptation_v1.json"
    prior = load(prior_path)["metrics"]
    rows = [
        row("authentic microbial classification", "UK EA mixed environmental-water E. coli", "AUTHENTIC_OBSERVED", "chronological locked Oct-Dec 2024", str(locked["n"]), "F1", locked["f1"], "always-positive / training prevalence", "not computed", "seed 2026; fixed chronological split", auth_path, "nadi evaluate-authentic", "High prevalence 0.642 and low specificity 0.390; not drinking-water pipes."),
        row("authentic microbial classification", "UK EA mixed environmental-water E. coli", "AUTHENTIC_OBSERVED", "chronological locked Oct-Dec 2024", str(locked["n"]), "ROC-AUC", locked["roc_auc"], "not applicable", "not computed", "seed 2026; fixed chronological split", auth_path, "nadi evaluate-authentic", "Laboratory result release times unavailable."),
        row("authentic testing prioritization", "UK EA site rounds", "AUTHENTIC_OBSERVED", "41 eligible historical rounds, budget 3", "41 rounds", "high results found", policy["adaptive_sdaif"]["total_positives_found"], f"routine=84; deterministic random=80; random permutation mean={random_dist['mean_total_positives_found']:.2f}; best single=114; adaptive Bayesian=114", f"random permutation 95% range [{random_dist['lower_95']:.0f}, {random_dist['upper_95']:.0f}] across {random_dist['permutations']} permutations", f"{random_dist['permutations']} common-candidate permutations, seed {random_dist['seed']}", decision_path, "nadi evaluate-sdaif", "Same-round outcome-reveal replay; no superiority over strongest comparators."),
        row("unseen-site transfer", "UK EA physicochemical panel", "AUTHENTIC_OBSERVED", "site-hash holdout", "140 records / 38 sites", "F1", transfer["f1"], "within-site locked model F1=0.838", "not computed", "deterministic site hash", transfer_path, "historical external transfer script", "Surface-water transfer only; weak specificity and no Delhi-NCR inference."),
        row("BWFLnet pressure reconstruction", "BWFLnet", "OBSERVED + MODEL_ESTIMATE", "published held-out week, previously inspected", "18171 predictions / 673 timestamps / 27 loggers", "median logger MAE (m)", hydro["median_internal_logger_mae_m"], f"training-mean median MAE={hydro['training_mean_baseline_median_logger_mae_m']}", "not computed", "fixed published split", hydro_path, "nadi evaluate-hydraulics", "Pressure only; no microbial labels; validation week non-pristine."),
        row("simulated Net3 evaluation", "EPA Net3", "SIMULATED", "120 scenarios; 76 nonempty", "120 events", "Coverage@3", net3["adaptive_mean"], f"adaptive Bayesian={net3['strongest_baseline_mean']}", str(net3["comparison"]["paired_bootstrap_95pct"]), "seeds fixed in V5 configuration", net3_path, "nadi run-simulation", "SDAIF ties strongest baseline; no biological or field evidence."),
        row("simulated L-TOWN transfer", "L-TOWN", "SIMULATED", "4 hidden nonempty cases", "4 cases", "Coverage@3", ltown["mean_coverage_nonempty"]["adaptive_sdaif"], f"hydraulic/adaptive Bayesian={ltown['mean_coverage_nonempty']['adaptive_bayesian']}", "not computed", "frozen hidden scenario cases", ltown_path, "historical L-TOWN stress script", "Negative transfer; tiny case count; no microbial labels."),
        row("GECCO telemetry", "GECCO 2019", "AUTHENTIC_OBSERVED", "chronological untouched test", str(gecco["rows"]), "event F1", gecco["positive_f1"], f"always-negative accuracy={load(gecco_path)['always_negative_test_accuracy']}", "not computed", "fixed original chronological split", gecco_path, "historical GECCO evaluation", "Sensor-event anomaly endpoint, not E. coli."),
        row("Texas physical-network evidence", "Texas controlled pipe testbed", "AUTHENTIC_OBSERVED_CONTROLLED_PHYSICAL_TESTBED", "5-fold grouped whole-run holdout", str(texas["records"]), "F1", texas["f1"], f"always-leak F1={load(texas_path)['always_leak_baseline']['f1']}", "fold-level not aggregated", "StratifiedGroupKFold", texas_path, "historical Texas pressure evaluation", "Pressure-wave leak classification, not microbial detection."),
        row("external prior-art adaptation", "Open E. coli Models bounded EA subset", "AUTHENTIC_OBSERVED", "ordered temporal 80/20", "648 records", "F1", prior["f1"], "not a bit-for-bit prior-art reproduction", "not computed", "ordered temporal split", prior_path, "historical prior-art adaptation", "Limited pH/temperature/conductivity panel; not drinking-water validation."),
    ]
    with OUTPUT.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    print(f"{OUTPUT}: {len(rows)} rows")


if __name__ == "__main__":
    main()
