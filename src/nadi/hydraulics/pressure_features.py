"""Auditable pressure-wave features for controlled physical-pipe observations.

These functions quantify hydraulic signal structure only.  They do not infer a
microbial outcome and should be kept separate from NADI's laboratory E. coli
model until paired field evidence exists.
"""
from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from scipy.signal import welch


DEFAULT_BANDS: tuple[tuple[float, float], ...] = (
    (0.0, 100.0), (100.0, 500.0), (500.0, 1000.0),
    (1000.0, 3000.0), (3000.0, 6000.0), (6000.0, 10000.0),
)


def pressure_wave_features(
    samples: Sequence[float] | np.ndarray,
    sample_interval_s: float,
    bands: Sequence[tuple[float, float]] = DEFAULT_BANDS,
) -> dict[str, float]:
    """Return scale and spectrum features from one observed pressure waveform.

    A fixed Welch window prevents a file's duration from changing the spectral
    resolution. Empty or non-finite input is rejected rather than imputed.
    """
    values = np.asarray(samples, dtype=float)
    if len(values) < 32 or not np.isfinite(values).all():
        raise ValueError("Pressure waveform needs at least 32 finite observations")
    if not np.isfinite(sample_interval_s) or sample_interval_s <= 0:
        raise ValueError("sample_interval_s must be finite and positive")
    changes = np.diff(values)
    quantiles = np.quantile(values, [0.01, 0.05, 0.25, 0.50, 0.75, 0.95, 0.99])
    frequencies, density = welch(
        values - values.mean(), fs=1.0 / float(sample_interval_s),
        nperseg=min(8192, len(values)),
    )
    total_power = float(np.trapezoid(density, frequencies))
    feature = {
        "pressure_mean": float(values.mean()),
        "pressure_std": float(values.std()),
        "pressure_span": float(values.max() - values.min()),
        "pressure_q01": float(quantiles[0]), "pressure_q05": float(quantiles[1]),
        "pressure_q25": float(quantiles[2]), "pressure_q50": float(quantiles[3]),
        "pressure_q75": float(quantiles[4]), "pressure_q95": float(quantiles[5]),
        "pressure_q99": float(quantiles[6]),
        "pressure_change_std": float(changes.std()),
        "pressure_abs_change_mean": float(np.abs(changes).mean()),
        "spectral_centroid_hz": float(np.sum(frequencies * density) / max(np.sum(density), 1e-30)),
        "spectral_flatness": float(np.exp(np.mean(np.log(density + 1e-30))) / max(float(density.mean()), 1e-30)),
        "spectral_total_power": total_power,
    }
    for low, high in bands:
        mask = (frequencies >= low) & (frequencies < high)
        power = float(np.trapezoid(density[mask], frequencies[mask])) if mask.any() else 0.0
        feature[f"spectral_power_{int(low)}_{int(high)}hz"] = float(np.log10(power + 1e-12))
    return feature
