"""Audit downloaded prior-art repositories without calling them reproduced."""
from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIOR = ROOT.parent / "nadi_resources" / "prior_art"
OUT = ROOT / "results" / "prior_art_repository_audit_v1.json"

REPOS = {
    "open_ecoli_models": ("Open-Ecoli-Models", "https://github.com/Cognizant-RDMAI/Open-Ecoli-Models"),
    "wntr": ("WNTR", "https://github.com/USEPA/WNTR"),
    "epanet2_2": ("EPANET2.2", "https://github.com/USEPA/EPANET2.2"),
}


def run(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def main() -> dict:
    rows = {}
    for key, (dirname, url) in REPOS.items():
        repo = PRIOR / dirname
        if not repo.exists():
            rows[key] = {"status": "MISSING", "url": url}
            continue
        files = [p for p in repo.rglob("*") if p.is_file() and ".git" not in p.parts]
        rows[key] = {
            "status": "DOWNLOADED",
            "url": url,
            "commit": run(repo, "rev-parse", "HEAD"),
            "branch": run(repo, "branch", "--show-current"),
            "file_count": len(files),
            "notebooks": sorted(p.relative_to(repo).as_posix() for p in files if p.suffix == ".ipynb"),
            "readmes": sorted(p.relative_to(repo).as_posix() for p in files if p.name.lower().startswith("readme")),
            "license_files": sorted(p.relative_to(repo).as_posix() for p in files if "license" in p.name.lower()),
            "repository_snapshot_sha256": sha256(repo / ".git" / "HEAD"),
            "replication_status": "ACQUIRED_NOT_REPRODUCED",
        }
    result = {
        "audit_id": "NADI-PRIOR-ART-REPOSITORIES-V1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "repositories": rows,
        "claim_boundary": "Downloaded source repositories are prior-art inputs; acquisition is not method reproduction and contains no claim of matching published performance.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    main()
