"""Build a non-destructive index of historical NADI artifacts.

This index is an archive *map*, not a relocation action.  Historical results
remain in place until every consumer and provenance reference can be migrated
with post-move hash checks.
"""
from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "reports" / "phase_0_file_classification.csv"
DESTINATION = ROOT / "archive" / "historical_index.csv"


def main() -> None:
    with SOURCE.open(newline="", encoding="utf-8") as handle:
        records = list(csv.DictReader(handle))

    retained = [
        record
        for record in records
        if record["generation_status"] in {"historical", "superseded", "temporary"}
        or record["likely_role"] in {"Historical result", "Superseded experiment", "Temporary artifact"}
    ]
    rows = [
        {
            "original_path": record["path"],
            "role": record["likely_role"],
            "evidence_track": record["evidence_track"],
            "generation_status": record["generation_status"],
            "safe_to_move": record["safe_to_move"],
            "archive_status": "RETAINED_AT_ORIGINAL_PATH",
            "reason": "Preserved pending hash-checked consumer migration; see reports/migration_manifest.csv",
        }
        for record in retained
    ]
    DESTINATION.parent.mkdir(exist_ok=True)
    with DESTINATION.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"{DESTINATION}: {len(rows)} indexed artifacts")


if __name__ == "__main__":
    main()
