from __future__ import annotations

import importlib.util
from pathlib import Path


def test_xylem_submission_pack_matches_locked_evidence() -> None:
    path = Path(__file__).resolve().parents[1] / "scripts" / "audit_xylem_submission_pack.py"
    spec = importlib.util.spec_from_file_location("audit_xylem_submission_pack", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    result = module.main()
    assert result["status"] == "PASS"
    assert result["locked_counts"] == {"adaptive": 114, "random": 80, "routine": 84}
