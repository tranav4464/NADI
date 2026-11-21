import json
from pathlib import Path


def test_open_ecoli_adaptation_is_authentic_and_explicitly_limited():
    path = Path(__file__).resolve().parents[1] / "results" / "open_ecoli_prior_art_adaptation_v1.json"
    obj = json.loads(path.read_text(encoding="utf-8"))
    assert obj["data_origin"] == "AUTHENTIC_OBSERVED"
    assert obj["status"] == "CONTROLLED_AUTHENTIC_SUBSET_ADAPTATION"
    assert obj["metrics"]["f1"] >= 0
    assert "not bit-for-bit reproduction" in obj["claim_boundary"]
