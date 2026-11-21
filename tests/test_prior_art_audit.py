import json
from pathlib import Path


def test_prior_art_repositories_are_recorded_without_overclaiming():
    root = Path(__file__).resolve().parents[1]
    report = json.loads((root / "results" / "prior_art_repository_audit_v1.json").read_text(encoding="utf-8"))
    assert set(report["repositories"]) == {"open_ecoli_models", "wntr", "epanet2_2"}
    for row in report["repositories"].values():
        assert row["status"] == "DOWNLOADED"
        assert row["replication_status"] == "ACQUIRED_NOT_REPRODUCED"
