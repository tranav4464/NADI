import json
from pathlib import Path


def test_wdseventdb_holdout_is_observed_and_nonbiological():
    path = Path(__file__).resolve().parents[1] / "results" / "wdseventdb_event_holdout_v1.json"
    obj = json.loads(path.read_text(encoding="utf-8"))
    assert obj["data_origin"] == "AUTHENTIC_OBSERVED_TESTBED"
    assert obj["event_files"] == 8
    assert "not E. coli" in obj["claim_boundary"]
