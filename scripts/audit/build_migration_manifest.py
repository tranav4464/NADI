"""Create a hash-backed migration plan without moving or deleting files."""
from __future__ import annotations

import csv
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INVENTORY = ROOT / "reports" / "phase_0_file_classification.csv"
OUTPUT = ROOT / "reports" / "migration_manifest.csv"


def proposed(path: str) -> str:
    # Files already created in a canonical or historical destination must not
    # be planned for a second migration on a later inventory refresh.
    if path.startswith(("configs/canonical/", "configs/historical/", "results/canonical/",
                        "results/historical/", "scripts/canonical/", "scripts/historical/",
                        "docs/canonical/", "docs/historical/", "archive/")):
        return path
    if path.startswith("results/authentic_locked/"):
        return path.replace("results/authentic_locked/", "results/canonical/authentic/", 1)
    if path.startswith("results/locked/"):
        return path.replace("results/locked/", "results/historical/simulation/", 1)
    if path.startswith("results/bwflnet_full_hybrid/"):
        return path.replace("results/bwflnet_full_hybrid/", "results/canonical/hydraulics/", 1)
    if path.startswith("configs/"):
        return path.replace("configs/", "configs/historical/", 1)
    if path.startswith("scripts/download_") or path.startswith("scripts/acquire_"):
        return path.replace("scripts/", "scripts/acquisition/", 1)
    if path.startswith("data_processed/"):
        return path.replace("data_processed/", "data/processed/", 1)
    if path.startswith("data_raw/"):
        return path.replace("data_raw/", "data/raw/", 1)
    if path.startswith("data_interim/"):
        return path.replace("data_interim/", "data/processed/interim/", 1)
    if path.startswith("dist/nadi_dossier_render"):
        return path.replace("dist/", "archive/rendered/", 1)
    return path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    with INVENTORY.open(newline="", encoding="utf-8") as source:
        inventory = {item["path"]: item for item in csv.DictReader(source)}
    excluded = {".git", ".venv", ".venv_clean", ".pytest_cache", "__pycache__"}
    current_paths = {
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*")
        if path.is_file() and not any(part in excluded for part in path.relative_to(ROOT).parts)
    }
    # Hashing this manifest while replacing it would make its own row unstable.
    current_paths.discard(OUTPUT.relative_to(ROOT).as_posix())
    rows = []
    for original in sorted(current_paths | set(inventory)):
        item = inventory.get(original, {})
        path = ROOT / original
        if not path.is_file():
            rows.append({"original_path": original, "proposed_path": proposed(original),
                         "sha256_at_plan": "MISSING", "git_status_at_inventory": item.get("git_status", "new_after_phase0"),
                         "evidence_track": item.get("evidence_track", "unclassified_new"), "action": "HOLD_MISSING",
                         "migration_status": "not_moved", "reason": "Missing since Phase 0 scan; investigate before migration"})
            continue
        destination = proposed(original)
        rows.append({"original_path": original, "proposed_path": destination,
                     "sha256_at_plan": sha256(path), "git_status_at_inventory": item.get("git_status", "new_after_phase0"),
                     "evidence_track": item.get("evidence_track", "unclassified_new"), "action": "RETAIN_IN_PLACE" if destination == original else "PROPOSE_ONLY",
                     "migration_status": "not_moved", "reason": "No relocation until consumer/provenance and frozen-result checks pass"})
    OUTPUT.parent.mkdir(exist_ok=True)
    with OUTPUT.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"{OUTPUT}: {len(rows)} entries, {sum(r['action']=='PROPOSE_ONLY' for r in rows)} proposed moves, 0 executed")


if __name__ == "__main__":
    main()
