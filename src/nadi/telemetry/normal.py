from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class LocalNormalModel:
    """Causal local-normal statistics fitted only on a training window."""

    columns: tuple[str, ...]
    group_column: str | None
    global_stats: dict[str, tuple[float, float, int]]
    group_stats: dict[str, dict[str, tuple[float, float, int]]]
    min_group_count: int = 20

    def _stats(self, group: str | None, column: str) -> tuple[float, float, int]:
        if group is not None and group in self.group_stats:
            item = self.group_stats[group].get(column)
            if item is not None and item[2] >= self.min_group_count:
                return item
        return self.global_stats[column]

    def transform(self, frame: pd.DataFrame) -> pd.DataFrame:
        """Return robust z-scores; unknown groups use global training normals."""
        output = pd.DataFrame(index=frame.index)
        groups = frame[self.group_column].astype(str).to_numpy() if self.group_column and self.group_column in frame else [None] * len(frame)
        for column in self.columns:
            scores = []
            for row_number, value in enumerate(frame[column].to_numpy()):
                median, mad, count = self._stats(groups[row_number], column)
                if pd.isna(value):
                    scores.append(np.nan)
                else:
                    scale = max(1.4826 * mad, 1e-9)
                    scores.append(float((float(value) - median) / scale))
            output[f"{column}_local_z"] = scores
        return output


def _stats(frame: pd.DataFrame, columns: Iterable[str]) -> dict[str, tuple[float, float, int]]:
    result = {}
    for column in columns:
        values = pd.to_numeric(frame[column], errors="coerce").dropna()
        median = float(values.median()) if len(values) else 0.0
        mad = float((values - median).abs().median()) if len(values) else 1.0
        result[column] = (median, mad, int(len(values)))
    return result


def fit_local_normals(
    frame: pd.DataFrame,
    columns: Iterable[str],
    group_column: str | None = None,
    min_group_count: int = 20,
) -> LocalNormalModel:
    columns = tuple(columns)
    global_stats = _stats(frame, columns)
    group_stats: dict[str, dict[str, tuple[float, float, int]]] = {}
    if group_column and group_column in frame:
        for group, subset in frame.assign(_group=frame[group_column].astype(str)).groupby("_group", sort=True):
            group_stats[str(group)] = _stats(subset, columns)
    return LocalNormalModel(columns, group_column, global_stats, group_stats, min_group_count)
