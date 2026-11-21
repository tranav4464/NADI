from __future__ import annotations

import pandas as pd

from nadi.authentic.site_rounds import build_site_day_table, parse_ecoli_result


def test_censored_result_endpoint_is_unambiguous() -> None:
    assert parse_ecoli_result("<10") == (10.0, False)
    assert parse_ecoli_result(">10000") == (10000.0, True)
    assert parse_ecoli_result("499") == (499.0, False)
    assert parse_ecoli_result("500") == (500.0, True)


def test_same_round_results_do_not_enter_history_features() -> None:
    raw = pd.DataFrame([
        {"id": "1", "samplingPoint.notation": "A", "samplingPoint.prefLabel": "A", "samplingPoint.easting": 1, "samplingPoint.northing": 2, "samplingPoint.region": "R", "samplingPoint.area": "AR", "samplingPoint.subArea": "S", "phenomenonTime": "2024-01-01T08:00:00Z", "samplingPurpose": "P", "sampleMaterialType": "W", "result": "1000"},
        {"id": "2", "samplingPoint.notation": "B", "samplingPoint.prefLabel": "B", "samplingPoint.easting": 3, "samplingPoint.northing": 4, "samplingPoint.region": "R", "samplingPoint.area": "AR", "samplingPoint.subArea": "S", "phenomenonTime": "2024-01-01T09:00:00Z", "samplingPurpose": "P", "sampleMaterialType": "W", "result": "<10"},
        {"id": "3", "samplingPoint.notation": "A", "samplingPoint.prefLabel": "A", "samplingPoint.easting": 1, "samplingPoint.northing": 2, "samplingPoint.region": "R", "samplingPoint.area": "AR", "samplingPoint.subArea": "S", "phenomenonTime": "2024-01-02T08:00:00Z", "samplingPurpose": "P", "sampleMaterialType": "W", "result": "600"},
    ])
    frame = build_site_day_table(raw)
    day_one = frame[frame["round_id"] == "EA-2024-01-01"]
    assert set(day_one["region_prior_samples"]) == {0}
    day_two_a = frame[(frame["round_id"] == "EA-2024-01-02") & (frame["samplingPoint.notation"] == "A")].iloc[0]
    assert day_two_a["site_prior_samples"] == 1
    assert day_two_a["site_last_positive"] == 1
