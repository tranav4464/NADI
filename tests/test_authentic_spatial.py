from __future__ import annotations

import numpy as np
import pandas as pd

from nadi.authentic.spatial import assign_monitoring_zones


def test_spatial_zone_uses_real_coordinates_and_keeps_claim_boundary() -> None:
    frame = pd.DataFrame({
        "round_id": ["R1", "R1", "R1"],
        "easting_km": [0.0, 3.0, 100.0], "northing_km": [0.0, 4.0, 100.0],
    })
    result = assign_monitoring_zones(frame, np.array([.9, .8, .1]), .5, maximum_link_km=6)
    assert result.loc[0, "monitoring_zone_id"] == result.loc[1, "monitoring_zone_id"]
    assert result.loc[2, "monitoring_zone_id"] == "NOT_HIGH_RISK"
    assert set(result["zone_claim"]) == {"MODEL_ESTIMATED_MONITORING_ZONE_NOT_PIPELINE_ROUTE"}
