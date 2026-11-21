from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

import numpy as np
import pyreadstat


INVALID_TEST_CODES = frozenset({991, 992})
CENSORED_ABOVE_100 = 101


def binary_ecoli(raw: float | None) -> int | None:
    """MICS WQ26/WQ27 result: 0 is absent; 1..100 and >100 are present."""
    if raw is None or not np.isfinite(raw):
        return None
    value = int(raw)
    if value in INVALID_TEST_CODES or value < 0 or value > CENSORED_ABOVE_100:
        return None
    return int(value > 0)


def audit_sav(path: Path) -> dict:
    data, metadata = pyreadstat.read_sav(str(path), output_format="dict")
    source = [binary_ecoli(value) for value in data["WQ27"]]
    household = [binary_ecoli(value) for value in data["WQ26"]]
    derived = [int(value) for value in data["e_coli"]]
    both = [(s, h) for s, h in zip(source, household) if s is not None and h is not None]
    counts = Counter(both)
    source_valid = [value for value in source if value is not None]
    household_valid = [value for value in household if value is not None]
    return {
        "source_file_sha256": hashlib.sha256(path.read_bytes()).hexdigest().upper(),
        "rows": metadata.number_rows,
        "raw_label_columns": {
            "source": "WQ27: Source water test (100ml)",
            "household": "WQ26: Household water test (100ml)",
            "derived": "e_coli: stored binary variable; do not trust as household endpoint",
        },
        "source": {"valid": len(source_valid), "positive": sum(source_valid), "negative": len(source_valid) - sum(source_valid), "invalid": len(source) - len(source_valid)},
        "household": {"valid": len(household_valid), "positive": sum(household_valid), "negative": len(household_valid) - sum(household_valid), "invalid": len(household) - len(household_valid)},
        "stored_label_matches_source_all_rows": all(value == int(raw > 0) for value, raw in zip(derived, data["WQ27"])),
        "stored_label_source_mismatches_on_valid_rows": sum(s is not None and s != y for s, y in zip(source, derived)),
        "stored_label_household_mismatches_on_valid_rows": sum(h is not None and h != y for h, y in zip(household, derived)),
        "paired_valid": len(both),
        "paired_table": {f"source_{s}_household_{h}": counts[(s, h)] for s in (0, 1) for h in (0, 1)},
        "domain": "2019 Bangladesh household survey; not time-series or pipe-network telemetry",
    }


def write_audit(path: Path, output: Path) -> dict:
    audit = audit_sav(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    return audit
