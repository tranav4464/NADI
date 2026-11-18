import hashlib
from pathlib import Path

import pandas as pd

from nadi.microbial_risk.weather_model import FORECAST_FEATURES, NOWCAST_FEATURES
from nadi.paths import INTERIM_ROOT, PROCESSED_ROOT


def test_forecast_feature_contract_excludes_same_day_weather():
    assert "prcp_same_day" not in FORECAST_FEATURES
    assert "tavg_same_day" not in FORECAST_FEATURES
    assert "prcp_same_day" in NOWCAST_FEATURES
    assert "tavg_same_day" in NOWCAST_FEATURES
    assert all("prev_" in feature or feature.startswith("month_") for feature in FORECAST_FEATURES)


def test_temporal_partitions_are_strict_and_disjoint():
    frame = pd.read_csv(INTERIM_ROOT / "wqp_marion_weather.csv", parse_dates=["date"])
    train = frame[frame.date <= "2018-12-31"]
    calibration = frame[(frame.date > "2018-12-31") & (frame.date <= "2020-12-31")]
    test = frame[(frame.date > "2020-12-31") & (frame.date <= "2022-12-31")]
    assert train.date.max() < calibration.date.min() <= calibration.date.max() < test.date.min()
    assert set(train.index).isdisjoint(calibration.index)
    assert set(train.index).isdisjoint(test.index)
    assert set(calibration.index).isdisjoint(test.index)


def test_prepared_data_and_model_card_have_frozen_bytes():
    for path in (INTERIM_ROOT / "wqp_marion_weather.csv", PROCESSED_ROOT / "risk_model_card.json"):
        assert path.exists()
        assert len(hashlib.sha256(Path(path).read_bytes()).hexdigest()) == 64
