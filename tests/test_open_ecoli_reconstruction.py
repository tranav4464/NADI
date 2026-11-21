import json
from pathlib import Path


def test_open_ecoli_reconstruction_is_real_and_boundary_labelled():
    root = Path(__file__).resolve().parents[1]
    report = json.loads((root / "results" / "open_ecoli_real_data_reconstruction_v1.json").read_text(encoding="utf-8"))
    assert report["source"] == "WQP Marion County E. coli plus NOAA GHCN-D"
    assert report["original_workflow_status"] == "NOT_BIT_FOR_BIT_REPRODUCED"
    assert report["tracks"]["nowcast"]["xgboost_calibration"] is not None
