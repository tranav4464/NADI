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
    assert client.get("/").status_code == 200
    latest = client.get("/api/latest")
    assert latest.status_code == 200
    assert latest.get_json()["event_origin"] == "SIMULATED"
    benchmark = client.get("/api/benchmark")
    assert benchmark.status_code == 200
    assert "gate" in benchmark.get_json()


def test_unsupported_city_request_abstains():
    client = _app().test_client()
    response = client.post("/api/demo", json={"seed": 20261117, "budget": 3, "domain": "DELHI_DRINKING_NETWORK"})
    assert response.status_code == 200
    assert response.get_json()["decision_card"]["abstained"] is True


def test_exhibition_seed_has_a_nontrivial_hidden_event():
    client = _app().test_client()
    payload = client.post("/api/demo", json={"seed": 20261118, "budget": 3}).get_json()
    assert len(payload["hidden_truth_disclosed_after_decisions"]["affected_candidates"]) > 0
    assert len(payload["decision_card"]["selected_tests"]) == 3

