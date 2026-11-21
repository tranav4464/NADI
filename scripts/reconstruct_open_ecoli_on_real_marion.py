"""Reconstruct the open E. coli model family on acquired real Marion/NOAA data."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "open_ecoli_real_data_reconstruction_v1.json"


def main() -> dict:
    card = json.loads((ROOT / "data_processed" / "risk_model_card.json").read_text(encoding="utf-8"))
    tracks = {}
    for name, key in (("nowcast", "nowcast"), ("forecast_24h", "forecast_24h")):
        model = card[key]
        xgb = model["model_comparison"].get("xgboost")
        tracks[name] = {
            "selected_model": model["selected_model"],
            "xgboost_calibration": xgb,
            "untouched_test": model["untouched_test"],
            "claim_boundary": "Real Marion County surface-water E. coli and NOAA weather reconstruction; not drinking-water or network validation.",
        }
    report = {
        "reconstruction_id": "OPEN-ECOLI-REAL-MARION-RECONSTRUCTION-V1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source": "WQP Marion County E. coli plus NOAA GHCN-D",
        "method_relation": "Controlled model-family reconstruction: XGBoost is compared with logistic, random forest, ExtraTrees, tree and gradient boosting under a frozen temporal split.",
        "tracks": tracks,
        "original_workflow_status": "NOT_BIT_FOR_BIT_REPRODUCED",
        "reason": "The Open E. coli repository requires Environment Agency/NRW/SEPA, Open-Meteo, CORINE and MODIS source tables not included in the acquired repository.",
        "claim_boundary": "Real-data reconstruction only; no direct E. coli sensor detection, Delhi performance or hydraulic-network claim.",
    }
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    main()
