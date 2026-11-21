from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from math import log1p

import numpy as np
import pandas as pd


def parse_ecoli_result(value: object) -> tuple[float, bool]:
    """Parse the authentic EA result without inventing a measured value.

    Returned numeric values for censored results are conservative bounds used
    only for past-history features. The >=500 endpoint is unambiguous for the
    observed qualifiers in the audited file: `<1` and `<10` are negative;
    `>10000` and larger are positive.
    """

    text = str(value).strip().replace(",", "")
    if not text or text.lower() == "nan":
        return np.nan, False
    if text.startswith("<"):
        try:
            bound = float(text[1:])
        except ValueError:
            return np.nan, False
        return bound, bound >= 500
    if text.startswith(">"):
        try:
            bound = float(text[1:])
        except ValueError:
            return np.nan, False
        return bound, bound >= 500
    try:
        numeric = float(text)
    except ValueError:
        return np.nan, False
    return numeric, numeric >= 500


@dataclass
class _History:
    count: int = 0
    positives: int = 0
    log_sum: float = 0.0
    last_date: pd.Timestamp | None = None
    last_positive: int = 0

    @property
    def smoothed_rate(self) -> float:
        return (self.positives + 1.0) / (self.count + 2.0)

    @property
    def mean_log_count(self) -> float:
        return self.log_sum / self.count if self.count else 0.0

    def update(self, date: pd.Timestamp, positive: int, count_value: float) -> None:
        self.count += 1
        self.positives += int(positive)
        if np.isfinite(count_value):
            self.log_sum += log1p(max(0.0, float(count_value)))
        self.last_date = date
        self.last_positive = int(positive)


def _site_day_rows(raw: pd.DataFrame) -> pd.DataFrame:
    frame = raw.copy()
    frame["collection_time"] = pd.to_datetime(frame["phenomenonTime"], utc=True)
    frame["round_date"] = frame["collection_time"].dt.floor("D").dt.tz_localize(None)
    parsed = frame["result"].map(parse_ecoli_result)
    frame["ecoli_bound"] = [value for value, _ in parsed]
    frame["high_500"] = [int(flag) for _, flag in parsed]
    keys = ["round_date", "samplingPoint.notation"]
    aggregated = frame.sort_values("collection_time").groupby(keys, as_index=False).agg(
        collection_time=("collection_time", "min"),
        site_label=("samplingPoint.prefLabel", "first"),
        easting=("samplingPoint.easting", "first"),
        northing=("samplingPoint.northing", "first"),
        region=("samplingPoint.region", "first"),
        area=("samplingPoint.area", "first"),
        sub_area=("samplingPoint.subArea", "first"),
        sampling_purpose=("samplingPurpose", "first"),
        material=("sampleMaterialType", "first"),
        high_500=("high_500", "max"),
        ecoli_bound=("ecoli_bound", "max"),
        replicate_count=("id", "size"),
    )
    return aggregated.sort_values(["round_date", "samplingPoint.notation"]).reset_index(drop=True)


def build_site_day_table(raw: pd.DataFrame) -> pd.DataFrame:
    """Create past-only authentic site-day features.

    Every feature for a date is calculated before any outcome from that date is
    added to history, preventing same-round laboratory leakage.
    """

    daily = _site_day_rows(raw)
    site_history: defaultdict[str, _History] = defaultdict(_History)
    region_history: defaultdict[str, _History] = defaultdict(_History)
    global_history = _History()
    rows: list[dict] = []
    for date, group in daily.groupby("round_date", sort=True):
        pending: list[tuple[str, str, int, float]] = []
        day_of_year = int(pd.Timestamp(date).dayofyear)
        for record in group.to_dict("records"):
            site = str(record["samplingPoint.notation"])
            region = str(record.get("region") or "UNKNOWN")
            site_state = site_history[site]
            region_state = region_history[region]
            days_since = 365.0 if site_state.last_date is None else float((pd.Timestamp(date) - site_state.last_date).days)
            row = dict(record)
            row.update({
                "day_sin": float(np.sin(2 * np.pi * day_of_year / 366.0)),
                "day_cos": float(np.cos(2 * np.pi * day_of_year / 366.0)),
                "month": int(pd.Timestamp(date).month),
                "site_prior_samples": site_state.count,
                "site_prior_positive_rate": site_state.smoothed_rate,
                "site_prior_mean_log_count": site_state.mean_log_count,
                "site_last_positive": site_state.last_positive if site_state.count else 0,
                "days_since_site_sample": min(days_since, 365.0),
                "region_prior_samples": region_state.count,
                "region_prior_positive_rate": region_state.smoothed_rate,
                "global_prior_samples": global_history.count,
                "global_prior_positive_rate": global_history.smoothed_rate,
                "feature_cutoff": pd.Timestamp(date) - pd.Timedelta(nanoseconds=1),
                "data_origin": "AUTHENTIC_OBSERVED",
            })
            rows.append(row)
            pending.append((site, region, int(record["high_500"]), float(record["ecoli_bound"])))
        # Update only after all rows in the authentic sampling round received
        # their features.
        for site, region, positive, count_value in pending:
            site_history[site].update(pd.Timestamp(date), positive, count_value)
            region_history[region].update(pd.Timestamp(date), positive, count_value)
            global_history.update(pd.Timestamp(date), positive, count_value)
    result = pd.DataFrame(rows)
    result["round_id"] = result["round_date"].dt.strftime("EA-%Y-%m-%d")
    result["easting_km"] = pd.to_numeric(result["easting"], errors="coerce") / 1000.0
    result["northing_km"] = pd.to_numeric(result["northing"], errors="coerce") / 1000.0
    return result
