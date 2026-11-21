import json
from pathlib import Path


def test_authentic_prior_art_replication_status_is_explicit():
    root = Path(__file__).resolve().parents[1]
    report = json.loads((root / "results" / "authentic_prior_art_replication_v1.json").read_text(encoding="utf-8"))
    assert report["tracks"]["battledim_wntr"]["status"] == "REPRODUCED_SMOKE"
    assert report["tracks"]["open_ecoli_models"]["status"] == "CONTROLLED_SUBSET_ADAPTATION"
    assert report["tracks"]["open_ecoli_models"]["adaptation_result"].endswith("open_ecoli_prior_art_adaptation_v1.json")
