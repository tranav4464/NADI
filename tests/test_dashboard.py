from __future__ import annotations

import importlib.util
from pathlib import Path


def _app():
    path = Path(__file__).resolve().parents[1] / "app" / "server.py"
    spec = importlib.util.spec_from_file_location("nadi_dashboard", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.app


def test_dashboard_and_api_are_driven_by_result_files():
    client = _app().test_client()
    page = client.get("/")
    assert page.status_code == 200
    assert b"AUTHENTIC OBSERVED EVIDENCE" in page.data
    assert b"generated pipe event" in page.data
    authentic_xylem = client.get("/api/authentic-xylem")
    assert authentic_xylem.status_code == 200
    payload = authentic_xylem.get_json()
    assert payload["status"] == "AUTHENTIC_RETROSPECTIVE_REPLAY"
    assert payload["run_id"] == "audit_20261120_07"
    assert payload["domain"] == "UK_EA_MIXED_ENVIRONMENTAL_WATER_ECOLI"
    assert payload["data_policy"]["simulated_records_used"] is False
    assert payload["sites"]
    assert payload["adaptive_replay"]
    assert [step["selected_site"] for step in payload["adaptive_replay"]] == payload["selected_order"]
    legacy = client.get("/legacy")
    assert legacy.status_code == 200
    assert b"OPERATIONAL OUTCOME" in legacy.data
    latest = client.get("/api/latest")
    assert latest.status_code == 200
    assert latest.get_json()["event_origin"] == "SIMULATED"
    benchmark = client.get("/api/benchmark")
    assert benchmark.status_code == 200
    assert "gate" in benchmark.get_json()
    evidence = client.get("/api/evidence")
    assert evidence.status_code == 200
    assert evidence.get_json()["performance_matrix"] is not None
    assert evidence.get_json()["reproducibility_manifest"]["test_exit_code"] == 0
    authentic = client.get("/api/authentic")
    assert authentic.status_code == 200
    assert authentic.get_json()["surface_water_ecoli"]["data_origin"] == "AUTHENTIC_OBSERVED"
    assert authentic.get_json()["lira_piped_water_endpoint"]["endpoint"]["positive_rows"] == 24
    assert authentic.get_json()["texas_physical_pressure"]["data_origin"] == "AUTHENTIC_OBSERVED_CONTROLLED_PHYSICAL_TESTBED"
    assert "not direct E. coli detection" in authentic.get_json()["claim_boundary"]


def test_unsupported_city_request_abstains():
    client = _app().test_client()
    response = client.post("/api/demo", json={"seed": 20261117, "budget": 3, "domain": "DELHI_DRINKING_NETWORK"})
    assert response.status_code == 200
    assert response.get_json()["decision_card"]["abstained"] is True


def test_authentic_dashboard_rejects_artifact_hash_mismatch(monkeypatch):
    import nadi.dashboard.authentic_view as view

    monkeypatch.setattr(view, "sha256", lambda path: "corrupted")
    response = _app().test_client().get("/api/authentic-xylem")
    assert response.status_code == 503
    assert response.get_json()["status"] == "CANONICAL_ARTIFACT_UNAVAILABLE"


def test_pilot_preflight_rejects_noncausal_result_timing():
    client = _app().test_client()
    samples = [{
        "pilot_round_id": "r1", "location_id": "A", "collected_at_utc": "2026-01-01T09:00:00Z",
        "result_available_at_utc": "2026-01-01T10:00:00Z", "ecoli_result": 0,
        "ecoli_unit": "CFU/100mL", "ecoli_method": "partner", "valid_result": True,
        "sampling_reason": "pilot",
    }]
    rankings = [
        {"pilot_round_id": "r1", "location_id": "A", "policy": policy, "rank": 1,
         "information_cutoff_utc": "2026-01-02T09:00:00Z", "ranking_frozen_at_utc": "2026-01-02T08:00:00Z",
         "risk_probability": 0.3, "abstained": False}
        for policy in ("nadi_sdaif", "routine")
    ]
    response = client.post("/api/pilot-preflight", json={
        "samples": samples, "rankings": rankings,
        "endpoint_rule": {"analyte": "E. coli", "threshold": 1, "unit": "CFU/100mL"},
    })
    assert response.status_code == 422
    assert "LAB_OUTCOME_AVAILABLE_AT_OR_BEFORE_RANKING_CUTOFF" in response.get_json()["errors"]


def test_exhibition_seed_has_a_nontrivial_hidden_event():
    client = _app().test_client()
    payload = client.post("/api/demo", json={"seed": 20261118, "budget": 3}).get_json()
    assert len(payload["hidden_truth_disclosed_after_decisions"]["affected_candidates"]) > 0
    assert len(payload["decision_card"]["selected_tests"]) == 3
    assert payload["protective_actions"]
    assert all(item["requires_operator_review"] for item in payload["protective_actions"])

