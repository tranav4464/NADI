import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_ea_physchem_panel_is_sample_joined_and_limited():
    p = ROOT / "results" / "ea_ecoli_physchem_panel_v1.json"
    assert p.exists()
    obj = json.loads(p.read_text(encoding="utf-8"))
    assert obj["data_origin"] == "AUTHENTIC_OBSERVED"
    assert obj["records"] == 648
    assert obj["matched_feature_availability"]["temperature_0076"] > 0.4
    assert obj["models"]["laboratory_detection"]["physicochemical_only"]["hist_gradient_boosting"]["f1"] <= 1
    assert obj["models"]["high_risk_500_cfu_per_100ml"]["physicochemical_only"]["hist_gradient_boosting"]["roc_auc"] > 0.5
    assert any("Delhi" in x for x in obj["limitations"])
