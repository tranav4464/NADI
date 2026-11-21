from __future__ import annotations

import importlib.util
from pathlib import Path


def test_epa_distribution_audit_refuses_underpowered_training() -> None:
    path = Path(__file__).resolve().parents[1] / "scripts" / "audit_epa_distribution_water.py"
    spec = importlib.util.spec_from_file_location("audit_epa_distribution_water", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    result = module.main()
    assert result["data_origin"] == "AUTHENTIC_OBSERVED"
    assert result["ecoli_positive_records"] == 0
    assert result["model_gate"] == "NOT_SUITABLE_FOR_E_COLI_CLASSIFIER_TRAINING"
