from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pandas as pd
from flask import Flask, jsonify, render_template, request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from nadi.cli import load_config  # noqa: E402
from nadi.authentic.policy import authentic_sdaif_sequence  # noqa: E402
from nadi.dashboard.authentic_view import authentic_run  # noqa: E402
from nadi.pilot import audit_pilot_bundle  # noqa: E402
from nadi.pipeline.demo import run_demo  # noqa: E402

app = Flask(
    __name__,
    template_folder=str(ROOT / "app" / "templates"),
    static_folder=str(ROOT / "app" / "static"),
)


def _latest_demo() -> dict:
    paths = sorted((ROOT / "results" / "runs").glob("demo_*.json"), key=lambda p: p.stat().st_mtime)
    if not paths:
        return run_demo(load_config(), 20261118, 3)
    return json.loads(paths[-1].read_text(encoding="utf-8"))


def _benchmark() -> dict:
    path = ROOT / "results" / "locked" / "benchmark_v5_no_placeholders_summary.json"
    if not path.exists():
        return {"gate": "V5_NOT_AVAILABLE", "evidence_class": "SIMULATED"}
    result = json.loads(path.read_text(encoding="utf-8"))
    result["status"] = "CURRENT_SIMULATED_BENCHMARK_V5"
    result["evidence_class"] = "SIMULATED"
    result["interpretation"] = "Coverage@3 is conditional on nonempty simulated affected sets. SDAIF ties adaptive Bayesian; no field or biological detection claim."
    return result


@app.get("/api/evidence")
def evidence():
    """Expose the frozen metric/provenance artefacts for an auditable demo."""
    matrix_path = ROOT / "results" / "performance_matrix_v1.json"
    manifest_path = ROOT / "results" / "reproducibility_manifest_v1.json"
    return jsonify({
        "performance_matrix": json.loads(matrix_path.read_text(encoding="utf-8")) if matrix_path.exists() else None,
        "reproducibility_manifest": json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else None,
        "claim_boundary": "Evidence artefacts describe software benchmarks and provenance; they do not establish field or biological validity.",
    })


@app.get("/api/authentic")
def authentic():
    """Expose authentic-data metrics separately from simulated network runs."""
    files = {
        "surface_water_ecoli": ROOT / "results" / "ea_ecoli_authentic_baseline_v1.json",
        "physchem_panel": ROOT / "results" / "ea_ecoli_physchem_panel_v1.json",
        "lira_piped_water_endpoint": ROOT / "results" / "lira_piped_water_audit.json",
        "texas_physical_pressure": ROOT / "results" / "texas_physical_pressure_v1.json",
        "build_status": ROOT / "results" / "authentic_build_status_v1.json",
    }
    payload = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in files.items() if path.exists()}
    payload["claim_boundary"] = (
        "Authentic observed surface-water and operational tracks only; "
        "not direct E. coli detection or Delhi-NCR drinking-network validation."
    )
    return jsonify(payload)


@app.get("/")
def index():
    return render_template("authentic.html")


@app.get("/legacy")
def legacy():
    return render_template("index.html")


@app.get("/api/authentic-xylem")
def authentic_xylem():
    """Retrospective replay from one pinned, hash-verified authentic run."""
    try:
        base, run_manifest = authentic_run()
    except (FileNotFoundError, KeyError, ValueError, json.JSONDecodeError) as error:
        return jsonify({"status": "CANONICAL_ARTIFACT_UNAVAILABLE", "error": str(error)}), 503
    report_path = base / "authentic_experiment_report.json"
    sites_path = base / "authentic_locked_site_predictions_and_zones.csv"
    events_path = base / "authentic_test_events.csv"
    summary_path = base / "authentic_test_summary.csv"
    if not all(path.exists() for path in (report_path, sites_path, events_path, summary_path)):
        return jsonify({"status": "NOT_BUILT"}), 503
    report = json.loads(report_path.read_text(encoding="utf-8"))
    sites = pd.read_csv(sites_path)
    events = pd.read_csv(events_path)
    summary = pd.read_csv(summary_path)
    decision_rounds = set(events.loc[events["policy"] == "adaptive_sdaif", "round_id"].astype(str))
    rounds = sorted(set(sites["round_id"].astype(str)).intersection(decision_rounds))
    if not rounds:
        return jsonify({"status": "NO_ELIGIBLE_ROUNDS"}), 503
    requested = str(request.args.get("round", rounds[-1]))
    if requested not in rounds:
        return jsonify({"status": "UNKNOWN_ROUND", "round": requested}), 404
    view = sites[sites["round_id"].astype(str) == requested].copy()
    view = view.sort_values(["predicted_probability", "samplingPoint.notation"], ascending=[False, True])
    event = events[(events["round_id"].astype(str) == requested) & (events["policy"] == "adaptive_sdaif")]
    selected = [] if event.empty else str(event.iloc[0]["selected_sites"]).split("|")
    model_names = sorted(
        column.removeprefix("probability_")
        for column in view.columns if column.startswith("probability_")
    )
    predictions = {
        name: dict(zip(view["samplingPoint.notation"].astype(str), view[f"probability_{name}"].astype(float)))
        for name in model_names
    }
    truth = dict(zip(view["samplingPoint.notation"].astype(str), view["high_500"].astype(bool)))
    replay = authentic_sdaif_sequence(
        predictions,
        report["model_uncertainty_weights_from_validation_log_loss"],
        truth,
        budget=int(event.iloc[0]["budget"]) if not event.empty else 3,
        robustness_weight=float(report["selected_sdaif_robustness_weight"]),
    )
    if selected and replay["selected"] != selected:
        raise RuntimeError("Frozen SDAIF selection cannot be reproduced from stored round predictions")
    records = []
    for row in view.to_dict("records"):
        records.append({
            "site_id": str(row["samplingPoint.notation"]),
            "site_label": str(row.get("site_label", "")),
            "probability": float(row["predicted_probability"]),
            "model_probability_mean": float(row["model_probability_mean"]),
            "model_probability_std": float(row["model_probability_std"]),
            "within_transfer_support": bool(row["within_validation_disagreement_support"]),
            "site_unseen_during_training": bool(row["site_unseen_during_model_training"]),
            "laboratory_high_500": bool(row["high_500"]),
            "selected_by_sdaif": str(row["samplingPoint.notation"]) in selected,
            "monitoring_zone": str(row["monitoring_zone_id"]),
            "easting_km": float(row["easting_km"]),
            "northing_km": float(row["northing_km"]),
        })
    return jsonify({
        "status": "AUTHENTIC_RETROSPECTIVE_REPLAY",
        "evidence_class": run_manifest["evidence_class"],
        "domain": run_manifest["domain"],
        "run_id": run_manifest["run_id"],
        "result_timing": run_manifest["result_timing"],
        "round": requested,
        "available_rounds": rounds,
        "sites": records,
        "selected_order": selected,
        "adaptive_replay": replay["steps"],
        "policy_summary": summary.to_dict("records"),
        "model_report": report["model_reports"][report["best_model_selected_on_validation"]]["locked_test"],
        "best_model": report["best_model_selected_on_validation"],
        "claim_boundary": (
            "Retrospective prioritisation among sampled UK Environment Agency mixed "
            "environmental-water sites. The immediate sequential outcome reveal is a "
            "replay assumption. No drinking-water pipe biological validation or live alert."
        ),
        "material_mix_note": "EA input includes sea, river, estuarine, drainage and other materials; the historical report calls them surface water.",
        "data_policy": report["data_policy"],
    })


@app.post("/api/pilot-preflight")
def pilot_preflight():
    """Validate an anonymised prospective bundle before any score is computed.

    This endpoint is intentionally non-persistent: a partner can check its
    schema and causal timestamp order without uploading a data file to a third
    party service. It returns a design/provenance audit, never a biological
    classification or public-health instruction.
    """
    body = request.get_json(silent=True)
    if not isinstance(body, dict) or not isinstance(body.get("samples"), list) or not isinstance(body.get("rankings"), list):
        return jsonify({
            "status": "REJECT",
            "errors": ["EXPECTED_JSON_OBJECT_WITH_SAMPLES_AND_RANKINGS_LISTS"],
            "claim_boundary": "No prospective claim can be assessed from an invalid request.",
        }), 400
    result = audit_pilot_bundle(
        pd.DataFrame(body["samples"]), pd.DataFrame(body["rankings"]),
        endpoint_rule=body.get("endpoint_rule"),
    ).as_dict()
    return jsonify(result), 200 if result["status"] == "PASS" else 422


@app.get("/api/latest")
def latest():
    return jsonify(_latest_demo())


@app.get("/api/benchmark")
def benchmark():
    return jsonify(_benchmark())


@app.post("/api/demo")
def demo():
    body = request.get_json(silent=True) or {}
    seed = int(body.get("seed", 20261118))
    budget = max(1, min(10, int(body.get("budget", 3))))
    domain = str(body.get("domain", "SIMULATED_NETWORK_EVENT"))
    return jsonify(run_demo(load_config(), seed, budget, domain))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("NADI_PORT", "5050")), debug=False)

