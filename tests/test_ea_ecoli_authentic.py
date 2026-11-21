import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_ea_authentic_baseline_has_observed_boundary_and_metrics():
    p = ROOT / "results" / "ea_ecoli_authentic_baseline_v1.json"
    assert p.exists()
    obj = json.loads(p.read_text(encoding="utf-8"))
    assert obj["data_origin"] == "AUTHENTIC_OBSERVED"
    assert obj["records"] > 1000
    assert obj["domain"] == "surface_water_laboratory_observations"
    assert "hist_gradient_boosting" in obj["models"]
    assert 0 <= obj["models"]["hist_gradient_boosting"]["f1"] <= 1
    assert any("Delhi" in x for x in obj["limitations"])
