from __future__ import annotations

import numpy as np
import pytest

from nadi.hydraulics.pressure_features import pressure_wave_features


def test_pressure_features_are_finite_and_include_bands() -> None:
    t = np.arange(4096) / 25_600
    values = 2 * np.sin(2 * np.pi * 300 * t) + 0.2 * np.sin(2 * np.pi * 1800 * t)
    result = pressure_wave_features(values, 1 / 25_600)
    assert result["pressure_std"] > 0
    assert result["spectral_power_100_500hz"] > result["spectral_power_6000_10000hz"]
    assert all(np.isfinite(value) for value in result.values())


def test_pressure_features_reject_invalid_waveform() -> None:
    with pytest.raises(ValueError):
        pressure_wave_features([1.0, 2.0], 0.1)
