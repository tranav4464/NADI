from __future__ import annotations

from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
WORKSPACE_ROOT = PACKAGE_ROOT.parent
RESOURCE_ROOT = WORKSPACE_ROOT / "nadi_resources"
HISTORICAL_MATH_ROOT = WORKSPACE_ROOT / "nadi_math_checks"
CONFIG_ROOT = PACKAGE_ROOT / "configs"
PROVENANCE_ROOT = PACKAGE_ROOT / "provenance"
INTERIM_ROOT = PACKAGE_ROOT / "data_interim"
PROCESSED_ROOT = PACKAGE_ROOT / "data_processed"
RESULTS_ROOT = PACKAGE_ROOT / "results"

