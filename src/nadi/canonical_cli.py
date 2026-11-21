"""Guarded package entry point for evidence-separated NADI workflows."""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import joblib
import numpy as np

from nadi.authentic.site_rounds import build_site_day_table
from nadi.authentic.models import (
    CATEGORICAL_FEATURES, NUMERIC_FEATURES, TARGET, ProbabilityCalibrator,
    classification_metrics, model_family, select_threshold,
)
from nadi.core.layout import ROOT, load_layout, sha256


REQUIRED_COLUMNS = {
    "round_date", "samplingPoint.notation", "feature_cutoff", "high_500",
    "data_origin", "round_id", "site_prior_samples", "global_prior_samples",
}


def _split_frame(frame: pd.DataFrame, start: str, end: str | None = None) -> pd.DataFrame:
    dates = pd.to_datetime(frame["round_date"])
    mask = dates >= start
    if end is not None:
        mask &= dates <= end
    return frame.loc[mask].copy()


def _common_identity(layout, workflow: str, output: Path, started: str, outputs: list[Path], sources: dict[str, Path]) -> dict:
    return {
        "command": workflow.replace("_", "-"), "run_id": output.name, "status": "PASS",
        "started_utc": started, "finished_utc": _utc(), "seed": layout.seed,
        "evidence_class": layout.evidence_class, "domain": layout.domain,
        "input_path": str(layout.input_path), "input_sha256": layout.input_sha256,
        "config_path": str(layout.config_path), "config_sha256": layout.config_sha256,
        "source_sha256": {name: sha256(path) for name, path in sources.items()},
        "output_dir": str(output), "outputs_sha256": {path.name: sha256(path) for path in outputs},
    }


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def verify_data(config: Path, run_id: str) -> Path:
    layout = load_layout(config)
    if layout.domain != "UK_EA_MIXED_ENVIRONMENTAL_WATER_ECOLI" or layout.evidence_class != "LAB_CONFIRMED":
        raise ValueError("The data verifier currently supports only the audited EA domain")
    if layout.raw.get("input_sha256") != layout.input_sha256:
        raise ValueError("Input bytes differ from the canonical configuration")
    output_root = ROOT / "results" / "canonical" / "audit"
    if not run_id or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for c in run_id):
        raise ValueError("Invalid run ID")
    output = output_root / run_id
    if output.exists():
        raise FileExistsError(f"Run ID already exists: {output}")
    findings: list[str] = []
    with layout.input_path.open(newline="", encoding="utf-8") as source:
        columns = set(next(csv.reader(source)))
    missing = REQUIRED_COLUMNS - columns
    if missing:
        findings.append(f"Missing columns: {sorted(missing)}")
    frame = pd.read_csv(layout.input_path, parse_dates=["round_date", "feature_cutoff"]) if not missing else None
    stats = {}
    if frame is not None:
        stats = {
            "rows": len(frame),
            "sites": int(frame["samplingPoint.notation"].nunique()),
            "dates": int(frame["round_date"].nunique()),
            "duplicate_site_dates": int(frame[["round_date", "samplingPoint.notation"]].duplicated().sum()),
            "feature_cutoff_on_or_after_round": int((frame["feature_cutoff"] >= frame["round_date"]).sum()),
            "unexpected_origins": sorted(set(frame["data_origin"].dropna()) - {"AUTHENTIC_OBSERVED"}),
            "invalid_binary_labels": int((~frame["high_500"].isin([0, 1])).sum()),
        }
        if stats["duplicate_site_dates"]:
            findings.append("Duplicate site/date records")
        if stats["feature_cutoff_on_or_after_round"]:
            findings.append("Non-causal feature cutoff")
        if stats["unexpected_origins"]:
            findings.append("Unexpected data origin")
        if stats["invalid_binary_labels"]:
            findings.append("Invalid binary labels")
    report = {
        "status": "PASS" if not findings else "FAIL",
        "evidence_class": layout.evidence_class,
        "domain": layout.domain,
        "checks": stats,
        "findings": findings,
        "limitations": [
            "The CSV cannot establish actual laboratory-result release times.",
            "This check does not validate UK EA sampling selection or transfer to drinking-water networks.",
        ],
    }
    output.mkdir(parents=True, exist_ok=False)
    report_path = output / "data_verification.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "command": "verify-data", "run_id": run_id, "created_utc": _utc(),
        "status": report["status"], "seed": layout.seed,
        "config_path": str(layout.config_path), "config_sha256": layout.config_sha256,
        "input_path": str(layout.input_path), "input_sha256": layout.input_sha256,
        "source_sha256": {"src/nadi/canonical_cli.py": sha256(Path(__file__))},
        "output_dir": str(output),
        "outputs_sha256": {report_path.name: sha256(report_path)},
    }
    (output / "run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    if findings:
        raise ValueError(f"Verification failed; inspect {report_path}")
    return output


def prepare_authentic(config: Path, run_id: str) -> Path:
    layout = load_layout(config)
    if layout.raw.get("workflow") != "prepare_authentic":
        raise ValueError("Expected the prepare_authentic workflow")
    if layout.raw.get("input_sha256") != layout.input_sha256:
        raise ValueError("Raw EA input bytes differ from the pinned source")
    if layout.domain != "UK_EA_MIXED_ENVIRONMENTAL_WATER_ECOLI" or layout.evidence_class != "LAB_CONFIRMED":
        raise ValueError("The preparation domain/evidence class is incorrect")
    if layout.output_root != (ROOT / "results/canonical/preparation").resolve():
        raise ValueError("Preparation output root is incorrect")
    output = layout.create_output(run_id)
    started = _utc()
    raw = pd.read_csv(layout.input_path, low_memory=False)
    frame = build_site_day_table(raw)
    table_path = output / "ea_authentic_site_rounds_2024.csv"
    frame.to_csv(table_path, index=False)
    report = {
        "raw_observations": len(raw),
        "site_day_rows": len(frame),
        "sites": int(frame["samplingPoint.notation"].nunique()),
        "dates": int(frame["round_date"].nunique()),
        "data_origin": "AUTHENTIC_OBSERVED",
        "claim_boundary": "Mixed UK EA environmental-water observations, not drinking-water pipe biological evidence.",
        "result_release_timing": "NOT_AVAILABLE_IN_RAW_SOURCE",
    }
    report_path = output / "preparation_report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "command": "prepare-authentic", "run_id": run_id, "status": "PASS",
        "started_utc": started, "finished_utc": _utc(), "seed": layout.seed,
        "evidence_class": layout.evidence_class, "domain": layout.domain,
        "input_path": str(layout.input_path), "input_sha256": layout.input_sha256,
        "config_path": str(layout.config_path), "config_sha256": layout.config_sha256,
        "source_sha256": {
            "src/nadi/canonical_cli.py": sha256(Path(__file__)),
            "src/nadi/authentic/site_rounds.py": sha256(Path(__file__).resolve().parent / "authentic/site_rounds.py"),
        },
        "output_dir": str(output),
        "outputs_sha256": {path.name: sha256(path) for path in (table_path, report_path)},
    }
    (output / "run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return output


def train_risk(config: Path, run_id: str) -> Path:
    """Fit uncalibrated risk estimators on the chronological training period."""
    layout = load_layout(config)
    if layout.raw.get("workflow") != "train_risk" or layout.domain != "UK_EA_MIXED_ENVIRONMENTAL_WATER_ECOLI":
        raise ValueError("Expected the authentic microbial risk training configuration")
    if layout.raw.get("input_sha256") != layout.input_sha256 or layout.evidence_class != "LAB_CONFIRMED":
        raise ValueError("Training input identity/evidence class is incorrect")
    if layout.output_root != (ROOT / "results/canonical/risk_training").resolve():
        raise ValueError("Risk training output root is incorrect")
    output = layout.create_output(run_id)
    started = _utc()
    frame = pd.read_csv(layout.input_path, parse_dates=["round_date"])
    train = frame[frame["round_date"] <= layout.raw["train_through"]].copy()
    if train.empty or train[TARGET].nunique() != 2:
        raise ValueError("Chronological training set is empty or has one class")
    models = model_family(layout.seed)
    for model in models.values():
        model.estimator.fit(train[NUMERIC_FEATURES + CATEGORICAL_FEATURES], train[TARGET].astype(int))
        model.calibrator = None
    bundle_path = output / "uncalibrated_models.joblib"
    joblib.dump(models, bundle_path)
    report = {
        "status": "PASS", "train_rows": len(train), "train_sites": int(train["samplingPoint.notation"].nunique()),
        "train_dates": [str(train["round_date"].min().date()), str(train["round_date"].max().date())],
        "models": sorted(models), "calibration": "NOT_FITTED", "endpoint": "E_COLI_GE_500_PER_100ML_PROJECT_HIGH_COUNT",
        "evidence_class": "LAB_CONFIRMED", "claim_boundary": "Chronological mixed environmental-water model training; not pipe contamination detection.",
    }
    report_path = output / "training_report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    manifest = _common_identity(layout, "train_risk", output, started, [bundle_path, report_path], {
        "src/nadi/canonical_cli.py": Path(__file__), "src/nadi/authentic/models.py": Path(__file__).resolve().parent / "authentic/models.py",
    })
    (output / "run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return output


def calibrate_risk(config: Path, run_id: str) -> Path:
    """Fit probability calibration and validation-only thresholds for trained models."""
    layout = load_layout(config)
    if layout.raw.get("workflow") != "calibrate_risk" or layout.domain != "UK_EA_MIXED_ENVIRONMENTAL_WATER_ECOLI":
        raise ValueError("Expected the authentic microbial risk calibration configuration")
    if layout.raw.get("input_sha256") != layout.input_sha256 or layout.evidence_class != "LAB_CONFIRMED":
        raise ValueError("Calibration input identity/evidence class is incorrect")
    if layout.output_root != (ROOT / "results/canonical/risk_calibration").resolve():
        raise ValueError("Risk calibration output root is incorrect")
    upstream_path = ROOT / layout.raw["training_manifest"]
    upstream = json.loads(upstream_path.read_text(encoding="utf-8"))
    if upstream.get("command") != "train-risk" or upstream.get("status") != "PASS" or upstream.get("input_sha256") != layout.input_sha256:
        raise ValueError("Pinned training run is not compatible with calibration input")
    bundle_path = Path(upstream["output_dir"]) / "uncalibrated_models.joblib"
    if sha256(bundle_path) != upstream.get("outputs_sha256", {}).get(bundle_path.name):
        raise ValueError("Pinned uncalibrated model bundle failed hash verification")
    output = layout.create_output(run_id)
    started = _utc()
    frame = pd.read_csv(layout.input_path, parse_dates=["round_date"])
    start, end = layout.raw["calibration"]
    calibration = _split_frame(frame, start, end)
    if calibration.empty or calibration[TARGET].nunique() != 2:
        raise ValueError("Chronological calibration set is empty or has one class")
    models = joblib.load(bundle_path)
    report_models = {}
    for name, model in models.items():
        raw = model.estimator.predict_proba(calibration[NUMERIC_FEATURES + CATEGORICAL_FEATURES])[:, 1]
        model.calibrator = ProbabilityCalibrator().fit(raw, calibration[TARGET].to_numpy())
        probabilities = model.predict_proba(calibration)
        threshold = select_threshold(calibration[TARGET].to_numpy(), probabilities)
        report_models[name] = {
            "threshold_selected_on_calibration": threshold,
            "calibration_metrics": classification_metrics(calibration[TARGET].to_numpy(), probabilities, threshold),
        }
    calibrated_path = output / "calibrated_models.joblib"
    joblib.dump(models, calibrated_path)
    report = {
        "status": "PASS", "calibration_rows": len(calibration),
        "calibration_dates": [str(calibration["round_date"].min().date()), str(calibration["round_date"].max().date())],
        "models": report_models, "endpoint": "E_COLI_GE_500_PER_100ML_PROJECT_HIGH_COUNT",
        "claim_boundary": "Calibration uses a separate chronological environmental-water period; no locked test labels used.",
    }
    report_path = output / "calibration_report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    manifest = _common_identity(layout, "calibrate_risk", output, started, [calibrated_path, report_path], {
        "src/nadi/canonical_cli.py": Path(__file__), "src/nadi/authentic/models.py": Path(__file__).resolve().parent / "authentic/models.py",
    })
    manifest["training_manifest_path"] = str(upstream_path)
    manifest["training_manifest_sha256"] = sha256(upstream_path)
    (output / "run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return output


def evaluate_hydraulics(config: Path, run_id: str) -> Path:
    layout = load_layout(config)
    if layout.raw.get("workflow") != "evaluate_hydraulics" or layout.domain != "BWFLNET_MEASURED_PRESSURE":
        raise ValueError("Expected the BWFLnet pressure evaluation configuration")
    if layout.evidence_class != "OBSERVED" or layout.raw.get("input_sha256") != layout.input_sha256:
        raise ValueError("Observed pressure input identity is incorrect")
    if layout.output_root != (ROOT / "results/canonical/hydraulics").resolve():
        raise ValueError("Hydraulic output root is incorrect")
    baseline = (ROOT / layout.raw["baseline"]).resolve(strict=True)
    baseline_hash = sha256(baseline)
    if baseline_hash != layout.raw.get("baseline_sha256"):
        raise ValueError("Hydraulic baseline file differs from the pinned input")
    output = layout.create_output(run_id)
    started = _utc()
    frame = pd.read_csv(layout.input_path)
    required = {"timestamp", "logger", "observed_pressure_m", "physics_pressure_m", "hybrid_pressure_m", "interval_lower_m", "interval_upper_m"}
    if not required.issubset(frame.columns):
        raise ValueError(f"Missing prediction columns: {sorted(required - set(frame.columns))}")
    error = (frame["hybrid_pressure_m"] - frame["observed_pressure_m"]).abs()
    logger_mae = error.groupby(frame["logger"]).mean()
    baseline_frame = pd.read_csv(baseline)
    baseline_internal = baseline_frame.set_index("logger").loc[logger_mae.index, "training_mean_mae"]
    median_logger_mae = float(logger_mae.median())
    baseline_median = float(baseline_internal.median())
    report = {
        "status": "PASS", "domain": layout.domain,
        "observed_pressure_evidence": True, "predicted_pressure_evidence_class": "MODEL_ESTIMATE",
        "prediction_rows": len(frame), "timestamps": int(frame["timestamp"].nunique()),
        "internal_loggers": int(frame["logger"].nunique()),
        "median_internal_logger_mae_m": median_logger_mae,
        "aggregate_prediction_mae_m": float(error.mean()),
        "training_mean_baseline_median_logger_mae_m": baseline_median,
        "relative_median_mae_improvement": 1 - median_logger_mae / baseline_median,
        "stored_interval_coverage": float(((frame["observed_pressure_m"] >= frame["interval_lower_m"]) &
                                            (frame["observed_pressure_m"] <= frame["interval_upper_m"])).mean()),
        "limitations": [
            "Recalculation from stored predictions; this command does not retrain the hydraulic estimator.",
            "The validation week was previously inspected in model development.",
            "Measured pressure does not validate E. coli presence, source or pipe contamination.",
        ],
    }
    report_path = output / "hydraulic_evaluation.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "command": "evaluate-hydraulics", "run_id": run_id, "status": "PASS",
        "started_utc": started, "finished_utc": _utc(), "seed": layout.seed,
        "evidence_class": layout.evidence_class, "domain": layout.domain,
        "input_path": str(layout.input_path), "input_sha256": layout.input_sha256,
        "baseline_path": str(baseline), "baseline_sha256": baseline_hash,
        "config_path": str(layout.config_path), "config_sha256": layout.config_sha256,
        "source_sha256": {"src/nadi/canonical_cli.py": sha256(Path(__file__))},
        "output_dir": str(output), "outputs_sha256": {report_path.name: sha256(report_path)},
    }
    (output / "run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return output


def evaluate_sdaif(config: Path, run_id: str) -> Path:
    """Reconcile the authentic fixed-budget SDAIF replay from pinned event data."""
    layout = load_layout(config)
    if layout.raw.get("workflow") != "evaluate_sdaif" or layout.evidence_class != "LAB_CONFIRMED":
        raise ValueError("Expected an authentic SDAIF decision-evaluation configuration")
    if layout.raw.get("input_sha256") != layout.input_sha256:
        raise ValueError("Pinned SDAIF event table has changed")
    summary_path = (ROOT / layout.raw["summary"]).resolve(strict=True)
    if sha256(summary_path) != layout.raw.get("summary_sha256"):
        raise ValueError("Pinned SDAIF summary table has changed")
    prediction_path = (ROOT / layout.raw["site_predictions"]).resolve(strict=True)
    if sha256(prediction_path) != layout.raw.get("site_predictions_sha256"):
        raise ValueError("Pinned SDAIF site-prediction table has changed")
    output = layout.create_output(run_id)
    started = _utc()
    events = pd.read_csv(layout.input_path)
    summary = pd.read_csv(summary_path)
    budget = int(layout.raw["budget"])
    errors: list[str] = []
    by_round = events.groupby("round_id")
    if not (events["budget"] == budget).all():
        errors.append("Inconsistent policy budget")
    if by_round["policy"].nunique().nunique() != 1:
        errors.append("Policy set differs across monitoring rounds")
    if (events["selected_sites"].str.split("|").str.len() > budget).any():
        errors.append("A policy exceeds its test budget")
    policies = set(summary["policy"])
    if not {"adaptive_sdaif", "best_single_model", "adaptive_bayesian", "random", "routine_sampling_frequency"}.issubset(policies):
        errors.append("Required comparison policies are missing")
    totals = events.groupby("policy")["positives_found"].sum().to_dict()
    random_repetitions = int(layout.raw.get("random_permutations", 1000))
    if random_repetitions < 2:
        raise ValueError("At least two random permutations are required")
    predictions = pd.read_csv(prediction_path)
    event_rounds = sorted(events["round_id"].unique())
    random_totals = _random_permutation_totals(predictions, event_rounds, budget, random_repetitions, layout.seed)
    random_distribution = {
        "permutations": random_repetitions,
        "seed": layout.seed,
        "mean_total_positives_found": float(random_totals.mean()),
        "standard_deviation": float(random_totals.std(ddof=1)),
        "lower_95": float(np.quantile(random_totals, 0.025)),
        "upper_95": float(np.quantile(random_totals, 0.975)),
        "minimum": int(random_totals.min()),
        "maximum": int(random_totals.max()),
        "probability_random_matches_or_exceeds_sdaif": float((random_totals >= totals.get("adaptive_sdaif", 0)).mean()),
        "data_origin": "AUTHENTIC_OBSERVED",
        "interpretation": "Permutation uncertainty for the random baseline; it does not alter the frozen deterministic random comparator.",
    }
    result = {
        "status": "PASS" if not errors else "FAIL", "rounds": int(events["round_id"].nunique()),
        "budget": budget, "policies": sorted(policies), "total_positives_found": totals,
        "sdaif_ties_best_single": totals.get("adaptive_sdaif") == totals.get("best_single_model"),
        "sdaif_ties_adaptive_bayesian": totals.get("adaptive_sdaif") == totals.get("adaptive_bayesian"),
        "sdaif_vs_random_difference": int(totals.get("adaptive_sdaif", 0) - totals.get("random", 0)),
        "sdaif_vs_routine_difference": int(totals.get("adaptive_sdaif", 0) - totals.get("routine_sampling_frequency", 0)),
        "random_permutation_distribution": random_distribution,
        "errors": errors,
        "limitations": [
            "This is retrospective replay using a same-round outcome-reveal assumption.",
            "It does not establish superiority: SDAIF ties the best single model and adaptive Bayesian policy on total positives.",
            "The frozen deterministic random order is retained for reproducibility; the attached multi-permutation distribution quantifies its random-baseline uncertainty.",
        ],
    }
    result_path = output / "sdaif_evaluation.json"
    result_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    manifest = _common_identity(layout, "evaluate_sdaif", output, started, [result_path], {
        "src/nadi/canonical_cli.py": Path(__file__), "src/nadi/authentic/benchmark.py": Path(__file__).resolve().parent / "authentic/benchmark.py",
        "src/nadi/authentic/policy.py": Path(__file__).resolve().parent / "authentic/policy.py",
    })
    manifest["summary_path"] = str(summary_path)
    manifest["summary_sha256"] = sha256(summary_path)
    manifest["site_predictions_path"] = str(prediction_path)
    manifest["site_predictions_sha256"] = sha256(prediction_path)
    (output / "run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    if errors:
        raise ValueError(f"SDAIF evaluation failed; inspect {result_path}")
    return output


def _random_permutation_totals(
    predictions: pd.DataFrame,
    round_ids: list[str],
    budget: int,
    repetitions: int,
    seed: int,
) -> np.ndarray:
    """Evaluate a common-budget random baseline across independent permutations.

    Only observed locked-round outcomes are used.  The function never feeds
    current outcomes into the risk models; it simply quantifies the variation
    of a genuinely random selection policy over the same candidates that every
    replay policy received.
    """
    required = {"round_id", "samplingPoint.notation", "high_500"}
    missing = required - set(predictions.columns)
    if missing:
        raise ValueError(f"Missing random-baseline columns: {sorted(missing)}")
    groups: list[np.ndarray] = []
    for round_id in round_ids:
        group = predictions.loc[predictions["round_id"] == round_id]
        if group.empty:
            raise ValueError(f"Pinned predictions omit replay round {round_id}")
        if group["samplingPoint.notation"].duplicated().any():
            raise ValueError(f"Duplicate site in replay round {round_id}")
        outcomes = group["high_500"].astype(int).to_numpy()
        if len(outcomes) < budget:
            raise ValueError(f"Replay round {round_id} has fewer candidates than the test budget")
        groups.append(outcomes)
    rng = np.random.default_rng(seed)
    totals = np.zeros(repetitions, dtype=int)
    for index in range(repetitions):
        totals[index] = sum(int(rng.permutation(outcomes)[:budget].sum()) for outcomes in groups)
    return totals


def run_simulation(config: Path, run_id: str) -> Path:
    """Run the declared Net3 simulation to a new canonical output directory."""
    from nadi.evaluation.benchmark import run_locked

    layout = load_layout(config)
    if layout.raw.get("workflow") != "run_simulation" or layout.evidence_class != "SIMULATED":
        raise ValueError("Expected a simulated Net3 benchmark configuration")
    if layout.raw.get("input_sha256") != layout.input_sha256:
        raise ValueError("Pinned simulation benchmark configuration has changed")
    runtime_path = (ROOT / layout.raw["runtime_config"]).resolve(strict=True)
    if sha256(runtime_path) != layout.raw.get("runtime_config_sha256"):
        raise ValueError("Pinned simulation runtime configuration has changed")
    output = layout.create_output(run_id)
    started = _utc()
    benchmark_config = json.loads(layout.input_path.read_text(encoding="utf-8"))
    runtime_config = json.loads(runtime_path.read_text(encoding="utf-8"))
    summary = run_locked(runtime_config, benchmark_config, "net3_simulation", output)
    summary_path = output / "net3_simulation_summary.json"
    events_path = output / "net3_simulation_events.csv"
    aggregate_path = output / "net3_simulation_aggregate.csv"
    summary["evidence_class"] = "SIMULATED"
    summary["domain"] = layout.domain
    summary["claim_boundary"] = "EPANET/WNTR Net3 simulation only; no biological or field validation."
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    manifest = _common_identity(layout, "run_simulation", output, started, [summary_path, events_path, aggregate_path], {
        "src/nadi/canonical_cli.py": Path(__file__), "src/nadi/evaluation/benchmark.py": Path(__file__).resolve().parent / "evaluation/benchmark.py",
    })
    manifest["runtime_config_path"] = str(runtime_path)
    manifest["runtime_config_sha256"] = sha256(runtime_path)
    (output / "run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return output


def build_manifest(config: Path, run_id: str) -> Path:
    """Build a hash manifest over explicitly named canonical artifacts."""
    layout = load_layout(config)
    if layout.raw.get("workflow") != "build_manifest" or layout.raw.get("input_sha256") != layout.input_sha256:
        raise ValueError("Manifest configuration/input identity is incorrect")
    output = layout.create_output(run_id)
    started = _utc()
    artifacts = []
    for relative in layout.raw.get("include", []):
        path = (ROOT / relative).resolve(strict=True)
        artifacts.append({"path": str(path), "sha256": sha256(path), "evidence_hint": "CANONICAL_OR_CONFIGURATION"})
    artifacts.append({"path": str(layout.input_path), "sha256": layout.input_sha256, "evidence_hint": "PRIMARY_INPUT_MANIFEST"})
    payload = {"status": "PASS", "generated_utc": _utc(), "artifacts": artifacts,
               "limitations": ["This is a file-integrity manifest, not an independent scientific validation."]}
    manifest_path = output / "canonical_artifact_manifest.json"
    manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    run_manifest = _common_identity(layout, "build_manifest", output, started, [manifest_path], {
        "src/nadi/canonical_cli.py": Path(__file__),
    })
    (output / "run_manifest.json").write_text(json.dumps(run_manifest, indent=2) + "\n", encoding="utf-8")
    return output


def audit(config: Path, run_id: str) -> Path:
    """Audit canonical manifests and enforce evidence-track boundaries."""
    layout = load_layout(config)
    if layout.raw.get("workflow") != "audit" or layout.raw.get("input_sha256") != layout.input_sha256:
        raise ValueError("Audit configuration/input identity is incorrect")
    output = layout.create_output(run_id)
    started = _utc()
    checks: dict[str, dict] = {}
    failures: list[str] = []
    expected = {
        "authentic_manifest": ("evaluate-authentic", "LAB_CONFIRMED", "UK_EA_MIXED_ENVIRONMENTAL_WATER_ECOLI"),
        "hydraulic_manifest": ("evaluate-hydraulics", "OBSERVED", "BWFLNET_MEASURED_PRESSURE"),
        "simulation_manifest": ("run-simulation", "SIMULATED", "NET3_SIMULATED_TRACER_EVENT"),
    }
    for key, (command, evidence, domain) in expected.items():
        path = (ROOT / layout.raw[key]).resolve(strict=True)
        manifest = json.loads(path.read_text(encoding="utf-8"))
        actual_command = manifest.get("canonical_command", manifest.get("command"))
        ok = manifest.get("status") == "PASS" and actual_command == command and manifest.get("evidence_class") == evidence and manifest.get("domain") == domain
        checks[key] = {"path": str(path), "sha256": sha256(path), "passed": ok, "command": actual_command, "evidence_class": manifest.get("evidence_class"), "domain": manifest.get("domain")}
        if not ok:
            failures.append(f"{key} has wrong status, command, evidence class or domain")
    report = {
        "status": "PASS" if not failures else "FAIL", "checks": checks, "failures": failures,
        "approved_system_boundary": "Retrospective UK EA mixed environmental-water testing prioritization; separate measured BWFLnet pressure reconstruction; separate Net3 simulation.",
        "prohibited_inferences": [
            "Direct E. coli detection from ordinary sensors", "Drinking-water contamination localization", "Delhi/Ghaziabad validation", "Illness reduction", "Integrated biological-hydraulic field validation",
        ],
    }
    report_path = output / "canonical_audit.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    manifest = _common_identity(layout, "audit", output, started, [report_path], {"src/nadi/canonical_cli.py": Path(__file__)})
    (output / "run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    if failures:
        raise ValueError(f"Canonical audit failed; inspect {report_path}")
    return output


def build_report(config: Path, run_id: str) -> Path:
    """Create a concise evidence-separated report from pinned canonical artifacts."""
    layout = load_layout(config)
    if layout.raw.get("workflow") != "build_report" or layout.raw.get("input_sha256") != layout.input_sha256:
        raise ValueError("Report configuration/input identity is incorrect")
    output = layout.create_output(run_id)
    started = _utc()
    authentic_manifest = json.loads(layout.input_path.read_text(encoding="utf-8"))
    if authentic_manifest.get("canonical_command", authentic_manifest.get("command")) != "evaluate-authentic" or authentic_manifest.get("status") != "PASS":
        raise ValueError("Pinned authentic evaluation is not a passing canonical artifact")
    hydraulic_manifest_path = (ROOT / layout.raw["hydraulic_manifest"]).resolve(strict=True)
    hydraulic_manifest = json.loads(hydraulic_manifest_path.read_text(encoding="utf-8"))
    auth_dir = Path(authentic_manifest["output_dir"])
    hydro_dir = Path(hydraulic_manifest["output_dir"])
    auth_report = json.loads((auth_dir / "authentic_experiment_report.json").read_text(encoding="utf-8"))
    decision = pd.read_csv(auth_dir / "authentic_test_summary.csv").set_index("policy")
    hydraulic = json.loads((hydro_dir / "hydraulic_evaluation.json").read_text(encoding="utf-8"))
    best = auth_report["best_model_selected_on_validation"]
    metrics = auth_report["model_reports"][best]["locked_test"]
    text = f"""# NADI canonical evidence report

## Approved scope

NADI is a retrospective testing-prioritization and decision-intelligence system. The primary evidence is UK Environment Agency mixed environmental-water E. coli observations. It does not establish direct sensor detection, drinking-water pipe contamination localization, Delhi-NCR performance, health impact, or an integrated biological-hydraulic field model.

## Authentic microbial-risk and decision track

- Locked period: {metrics['n']} observations; positive prevalence {metrics['prevalence']:.3f}.
- Selected validation model: `{best}`; locked F1 {metrics['f1']:.3f}, ROC-AUC {metrics['roc_auc']:.3f}, PR-AUC {metrics['pr_auc']:.3f}, sensitivity {metrics['sensitivity']:.3f}, specificity {metrics['specificity']:.3f}.
- Across {int(decision.loc['adaptive_sdaif', 'rounds'])} eligible rounds at a three-test budget, SDAIF found {int(decision.loc['adaptive_sdaif', 'total_positives_found'])} high results; routine frequency found {int(decision.loc['routine_sampling_frequency', 'total_positives_found'])}; the deterministic random comparator found {int(decision.loc['random', 'total_positives_found'])}.
- SDAIF ties the best-single-model and adaptive-Bayesian policies on total positives. No superiority claim is supported.
- The sequential reveal is a retrospective same-round replay; actual laboratory-result release times are unavailable.

## Separate measured hydraulic track

- BWFLnet: {hydraulic['prediction_rows']} stored predictions over {hydraulic['timestamps']} timestamps and {hydraulic['internal_loggers']} internal loggers.
- Median logger MAE {hydraulic['median_internal_logger_mae_m']:.3f} m; aggregate MAE {hydraulic['aggregate_prediction_mae_m']:.3f} m; declared baseline improvement {hydraulic['relative_median_mae_improvement']:.1%}.
- This is pressure reconstruction, not microorganism evidence. Its validation period was previously inspected.

## Reproducibility

Authentic run manifest: `{authentic_manifest['output_dir']}/run_manifest.json`<br>
Hydraulic run manifest: `{hydraulic_manifest['output_dir']}/run_manifest.json`
"""
    report_path = output / "canonical_evidence_report.md"
    report_path.write_text(text, encoding="utf-8")
    manifest = _common_identity(layout, "build_report", output, started, [report_path], {"src/nadi/canonical_cli.py": Path(__file__)})
    manifest["hydraulic_manifest_sha256"] = sha256(hydraulic_manifest_path)
    (output / "run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return output


def run_tests(config: Path, run_id: str) -> Path:
    """Run the full test suite and retain stdout, stderr and a manifest."""
    layout = load_layout(config)
    if layout.raw.get("workflow") != "run_tests" or layout.raw.get("input_sha256") != layout.input_sha256:
        raise ValueError("Test configuration/input identity is incorrect")
    output = layout.create_output(run_id)
    started = _utc()
    completed = subprocess.run([sys.executable, "-m", "pytest"], cwd=ROOT, text=True, capture_output=True, check=False)
    stdout = output / "pytest.stdout.log"; stderr = output / "pytest.stderr.log"
    stdout.write_text(completed.stdout, encoding="utf-8"); stderr.write_text(completed.stderr, encoding="utf-8")
    manifest = _common_identity(layout, "run_tests", output, started, [stdout, stderr], {"src/nadi/canonical_cli.py": Path(__file__)})
    manifest["returncode"] = completed.returncode
    manifest["status"] = "PASS" if completed.returncode == 0 else "FAILED"
    (output / "run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    if completed.returncode:
        raise RuntimeError(f"Test suite failed; inspect {output}")
    return output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="nadi", description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("audit", "verify-data", "prepare-authentic", "train-risk", "calibrate-risk", "evaluate-authentic", "evaluate-sdaif", "evaluate-hydraulics", "run-simulation", "build-report", "build-manifest", "run-tests"):
        command = commands.add_parser(name)
        command.add_argument("--config", type=Path, required=True)
        command.add_argument("--run-id", required=True)
    args = parser.parse_args(argv)
    if args.command == "audit":
        output = audit(args.config, args.run_id)
    elif args.command == "verify-data":
        output = verify_data(args.config, args.run_id)
    elif args.command == "prepare-authentic":
        output = prepare_authentic(args.config, args.run_id)
    elif args.command == "train-risk":
        output = train_risk(args.config, args.run_id)
    elif args.command == "calibrate-risk":
        output = calibrate_risk(args.config, args.run_id)
    elif args.command == "evaluate-sdaif":
        output = evaluate_sdaif(args.config, args.run_id)
    elif args.command == "evaluate-hydraulics":
        output = evaluate_hydraulics(args.config, args.run_id)
    elif args.command == "run-simulation":
        output = run_simulation(args.config, args.run_id)
    elif args.command == "build-manifest":
        output = build_manifest(args.config, args.run_id)
    elif args.command == "build-report":
        output = build_report(args.config, args.run_id)
    elif args.command == "run-tests":
        output = run_tests(args.config, args.run_id)
    else:
        command = [sys.executable, str(ROOT / "scripts" / "canonical" / "run_authentic.py"),
                   "--config", str(args.config), "--run-id", args.run_id]
        subprocess.run(command, cwd=ROOT, check=True)
        output = ROOT / "results" / "canonical" / "authentic" / args.run_id
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
