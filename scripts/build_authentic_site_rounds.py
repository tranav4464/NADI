"""Build the leakage-safe authentic EA site-day table and audit report."""
from __future__ import annotations

import json
import hashlib
from pathlib import Path

import pandas as pd

from nadi.authentic.site_rounds import build_site_day_table


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT.parent / "nadi_resources" / "datasets" / "EA_ECOLI_AUTHENTIC" / "ea_ecoli_confirmed_mf_2024.csv"
OUT = ROOT / "data_processed" / "ea_authentic_site_rounds_2024.csv"
REPORT = ROOT / "results" / "ea_authentic_site_rounds_2024.json"


def main() -> dict:
    raw = pd.read_csv(RAW, low_memory=False)
    frame = build_site_day_table(raw)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(OUT, index=False)
    round_sizes = frame.groupby("round_id")["samplingPoint.notation"].nunique()
    report = {
        "dataset": "EA_AUTHENTIC_SITE_ROUNDS_2024",
        "data_origin": "AUTHENTIC_OBSERVED",
        "raw_source_path": str(RAW.resolve()),
        "raw_source_sha256": hashlib.sha256(RAW.read_bytes()).hexdigest(),
        "raw_observations": int(len(raw)),
        "site_day_records": int(len(frame)),
        "unique_sites": int(frame["samplingPoint.notation"].nunique()),
        "rounds": int(frame["round_id"].nunique()),
        "rounds_at_least_5_sites": int((round_sizes >= 5).sum()),
        "rounds_at_least_10_sites": int((round_sizes >= 10).sum()),
        "rounds_at_least_20_sites": int((round_sizes >= 20).sum()),
        "positive_prevalence_500": float(frame["high_500"].mean()),
        "date_range": [str(frame["round_date"].min().date()), str(frame["round_date"].max().date())],
        "feature_contract": "Every history feature excludes all laboratory outcomes from the current round date.",
        "claim_boundary": "Authentic England surface-water monitoring; not drinking-water pipeline validation.",
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    main()
