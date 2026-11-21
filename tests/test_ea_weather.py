import json
from pathlib import Path

import pytest


def test_ea_weather_panel_is_observed_and_fully_matched():
    root = Path(__file__).resolve().parents[1]
    weather_metadata = root.parent / "nadi_resources/datasets/EA_ECOLI_AUTHENTIC/ea_openmeteo_weather_panel_q1_2024.json"
    if not weather_metadata.exists():
        pytest.skip("external EA/Open-Meteo resource is not bundled with the public repository")
    meta = json.loads(weather_metadata.read_text(encoding="utf-8"))
    result = json.loads((root / "results/ea_weather_enriched_holdout_v1.json").read_text(encoding="utf-8"))
    assert meta["data_origin"] == "AUTHENTIC_OBSERVED"
    assert meta["errors"] == []
    assert result["weather_match_rate"] == 1.0
    assert "not drinking-network validation" in result["claim_boundary"]
