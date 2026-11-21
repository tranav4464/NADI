import json
from pathlib import Path


def test_performance_matrix_reports_decision_relevant_counts():
    root = Path(__file__).resolve().parents[1]
    matrix = json.loads((root / "results" / "performance_matrix_v1.json").read_text(encoding="utf-8"))
    rows = {row["track"]: row for row in matrix["rows"]}
    for track in ("surface_water_nowcast", "surface_water_24h_forecast"):
        row = rows[track]
        assert 0.0 <= row["prevalence"] <= 1.0
        assert 0.0 <= row["precision"] <= 1.0
        assert row["false_negatives"] >= 0
        assert 0.0 <= row["calibration_ece"] <= 1.0
        assert 0.0 <= row["recall_wilson_95"][0] <= row["recall_wilson_95"][1] <= 1.0
    assert rows["gecco_sensor_event"]["status"] == "MEASURED_PROXY_ONLY"
