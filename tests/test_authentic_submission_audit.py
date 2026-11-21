from __future__ import annotations

import importlib.util
from pathlib import Path


def test_primary_xylem_bundle_is_authentic_only() -> None:
    path = Path(__file__).resolve().parents[1] / "scripts" / "audit_authentic_submission.py"
    spec = importlib.util.spec_from_file_location("audit_authentic_submission", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    assert module.audit()["status"] == "PASS"
