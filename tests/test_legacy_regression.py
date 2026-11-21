from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

WORKSPACE = Path(__file__).resolve().parents[2]
LEGACY_ROOT = WORKSPACE / "nadi_xylem"
if not (LEGACY_ROOT / "engine.py").exists():
    pytest.skip(
        "the historical nadi_xylem sibling workspace is not bundled with the public repository",
        allow_module_level=True,
    )
sys.path.insert(0, str(LEGACY_ROOT))

from engine import BASELINE, ContextModel, ProxyModel, evaluate  # noqa: E402


def test_historical_demo_fixture_remains_reproducible():
    model = ProxyModel.load(WORKSPACE / "nadi_xylem" / "proxy_model.json")
    context = ContextModel(json.loads((WORKSPACE / "nadi_xylem" / "context_model.json").read_text()))
    event = {"node_id": "SOUTH-B", "pressure": 0.42, "flow": 4.2, "chlorine": 0.09, "turbidity": 6.4, "conductivity": 590, "ph": 6.72, "temperature": 26.4, "rainfall_24h": 31, "restart": 1, "tlf": 1.8}
    context = ContextModel(json.loads((WORKSPACE / "nadi_xylem" / "context_model.json").read_text(encoding="utf-8")))
    result = evaluate(event, "data", model, BASELINE, context)
    assert result["nowcast"]["risk"] > 0.5
    assert result["sdaif"]["action"]
    assert "Only an accepted biological test" in result["claim_boundary"]

