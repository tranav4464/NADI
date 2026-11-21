import csv
from pathlib import Path


def test_canonical_performance_matrix_separates_all_required_tracks():
    root = Path(__file__).resolve().parents[1]
    rows = list(csv.DictReader((root / "reports/canonical_performance_matrix.csv").open(encoding="utf-8", newline="")))
    tracks = {row["track"] for row in rows}
    assert {
        "authentic microbial classification", "authentic testing prioritization", "unseen-site transfer",
        "BWFLnet pressure reconstruction", "simulated Net3 evaluation", "simulated L-TOWN transfer",
        "GECCO telemetry", "Texas physical-network evidence", "external prior-art adaptation",
    }.issubset(tracks)
    assert all(row["artifact_path"] and row["limitation"] and row["evidence_status"] for row in rows)
    net3 = next(row for row in rows if row["track"] == "simulated Net3 evaluation")
    ltown = next(row for row in rows if row["track"] == "simulated L-TOWN transfer")
    assert net3["evidence_status"] == "SIMULATED"
    assert float(ltown["result"]) < float(ltown["baseline"].split("=")[1])
