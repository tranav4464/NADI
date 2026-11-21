import json
from pathlib import Path


def test_ea_geographic_holdout_has_disjoint_locations():
    path = Path(__file__).resolve().parents[1] / "results" / "ea_ecoli_physchem_geographic_holdout_v1.json"
    obj = json.loads(path.read_text(encoding="utf-8"))
    assert obj["data_origin"] == "AUTHENTIC_OBSERVED"
    assert obj["train_sites"] + obj["test_sites"] == obj["unique_sites"]
    assert obj["test_records"] > 0
    assert obj["models"]["xgb_prior_art_reproduction"]["f1"] >= 0
