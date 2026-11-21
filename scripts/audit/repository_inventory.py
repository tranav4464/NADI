"""Read-only repository inventory; outputs metadata without moving source files."""
from __future__ import annotations

import csv
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reports"
EXCLUDED = {".git", ".venv", ".venv_clean", ".pytest_cache", "__pycache__"}


def git_lines(*args: str) -> list[str]:
    result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True)
    return result.stdout.splitlines()


def classify(relative: str) -> tuple[str, str, str]:
    p = relative.replace("\\", "/")
    if p.startswith("tests/"):
        return "Test", "cross-track", "current"
    if p.startswith("app/"):
        return "Dashboard", "dashboard/demo", "current"
    if p.startswith(("docs/", "reports/")) or p.endswith((".md", ".docx", ".pdf")):
        return "Documentation", "cross-track", "current" if not any(x in p.lower() for x in ("historical", "v3", "v4")) else "historical"
    if p.startswith("data/") or p.startswith(("data_raw/", "data_processed/", "data_interim/")):
        track = "authentic microbiology" if "ea" in p.lower() or "ecoli" in p.lower() else "hydraulic/telemetry/external"
        return "Canonical data" if "ea" in p.lower() else "Unknown", track, "current/verify"
    if p.startswith("results/"):
        status = "historical" if any(x in p.lower() for x in ("v3", "v4", "regression")) else "current/verify"
        track = "authentic microbiology" if "authentic" in p or "ea_" in p else "hydraulic/simulation/other"
        return "Historical result" if status == "historical" else "Unknown", track, status
    if p.startswith("dist/"):
        return "Generated artifact", "presentation", "current"
    if p.startswith("src/nadi/"):
        return "Canonical current code" if any(x in p for x in ("authentic/", "decision/")) else "Unknown", "code", "current/verify"
    if p.startswith("scripts/"):
        return "Unknown", "workflow", "current/verify"
    if p.startswith("configs/"):
        return "Unknown", "configuration", "current/verify"
    if p.startswith("logs/") or p.startswith("temp"):
        return "Temporary artifact", "operational", "unknown"
    return "Unknown", "cross-track", "unknown"


def main() -> None:
    OUT.mkdir(exist_ok=True)
    tracked = set(git_lines("ls-files"))
    status_lines = git_lines("status", "--porcelain=v1", "-uall")
    status = {line[3:].replace("\\", "/"): line[:2] for line in status_lines if len(line) >= 4}
    files = sorted(p for p in ROOT.rglob("*") if p.is_file() and not any(part in EXCLUDED for part in p.relative_to(ROOT).parts))
    # Candidate consumers are textual references, not verified runtime edges.
    text_files = [p for p in files if p.suffix.lower() in {".py", ".ps1", ".json", ".md", ".toml", ".js", ".html", ".bat"} and p.stat().st_size < 1_000_000]
    references = {}
    for source in text_files:
        try:
            references[source.relative_to(ROOT).as_posix()] = source.read_text(encoding="utf-8", errors="replace")
        except OSError:
            pass
    rows = []
    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        st = path.stat()
        category, track, generation = classify(rel)
        basename = path.name
        consumers = [name for name, content in references.items() if name != rel and basename in content]
        rows.append({"path": rel, "type": path.suffix.lower() or "no extension", "size_bytes": st.st_size,
                     "git_status": status.get(rel, "tracked-clean" if rel in tracked else "untracked/ignored"),
                     "modified_local": datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds"),
                     "likely_role": category, "evidence_track": track, "generation_status": generation,
                     "safe_to_move": "unverified", "safe_to_delete": "no", "dependencies_consumers": "; ".join(consumers[:20]) if consumers else "no textual reference found"})
    target = OUT / "phase_0_file_classification.csv"
    with target.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    sizes = sum(r["size_bytes"] for r in rows)
    modified = sum(r["git_status"] != "tracked-clean" for r in rows)
    (OUT / "phase_0_repository_inventory.md").write_text(
        f"# Phase 0 repository inventory\n\nGenerated {datetime.now().isoformat(timespec='seconds')}. "
        f"Read-only scan of {len(rows)} meaningful files, {sizes:,} bytes; {modified} modified, untracked or ignored paths. "
        "The CSV records each path, type, size, Git status, modification time, provisional evidence role and candidate textual consumers. "
        "The classifications are hypotheses; no file is yet cleared for movement or deletion.\n\n"
        "## Git and provenance state\n\nOne initial commit is present. Numerous tracked files are modified and most acquired datasets/results are untracked. "
        "A move at this point risks breaking recorded source paths and rewriting the apparent history. "
        "The repository contains two virtual environments, several generations of benchmark configurations, frozen-looking results, and temporary EPANET files. "
        "Neither `LOCKED` naming nor a report establishes immutability.\n\n"
        "## Evidence tracks\n\nEA microbiology, BWFLnet real hydraulics, simulated network studies, telemetry, transfer data, dashboard, and historical benchmarks are present. "
        "Textual basename matches in the CSV are candidate consumers only; dynamic imports, absolute paths and data lookups may be missed. Runtime ownership requires Phase 3 verification.\n\n"
        "## Changes and verification\n\nOnly this inventory script and reports were added. No source artifact was moved, deleted or regenerated. "
        "The next phase must trace the dossier numbers to exact result files, definitions and generating commands.\n",
        encoding="utf-8")
    print(target, len(rows), sizes)


if __name__ == "__main__":
    main()
