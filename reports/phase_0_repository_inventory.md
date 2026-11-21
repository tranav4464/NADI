# Phase 0 repository inventory

Generated 2026-11-20T15:44:05. Read-only scan of 866 meaningful files, 673,507,281 bytes; 820 modified, untracked or ignored paths. The CSV records each path, type, size, Git status, modification time, provisional evidence role and candidate textual consumers. The classifications are hypotheses; no file is yet cleared for movement or deletion.

## Git and provenance state

One initial commit is present. Numerous tracked files are modified and most acquired datasets/results are untracked. A move at this point risks breaking recorded source paths and rewriting the apparent history. The repository contains two virtual environments, several generations of benchmark configurations, frozen-looking results, and temporary EPANET files. Neither `LOCKED` naming nor a report establishes immutability.

## Evidence tracks

EA microbiology, BWFLnet real hydraulics, simulated network studies, telemetry, transfer data, dashboard, and historical benchmarks are present. Textual basename matches in the CSV are candidate consumers only; dynamic imports, absolute paths and data lookups may be missed. Runtime ownership requires Phase 3 verification.

## Changes and verification

Only this inventory script and reports were added. No source artifact was moved, deleted or regenerated. The next phase must trace the dossier numbers to exact result files, definitions and generating commands.

## Scope and classification limits

The CSV includes files outside `.git`, both virtual environments, `.pytest_cache` and bytecode caches. The virtual environments were inspected as environment roots; `.venv_clean/pyvenv.cfg` declares Python 3.10.11 with system site packages. They are not portable dependency locks. The package manifest is `pyproject.toml`, with a separate `requirements-lock.txt`.

Many rows remain `Unknown` deliberately. External datasets, configurations and source modules cannot be declared canonical from path names. `dist` holds multiple versioned evidence ZIPs and dossier renders. `results/locked` holds V1–V5 and regression benchmark generations, but naming does not prove immutability. `temp.bin`, `temp.inp` and `temp.rpt` are possible EPANET working artifacts; they remain untouched.

The `dependencies_consumers` entries are exact filename mentions in text files, not verified runtime edges. All rows have `safe_to_move=unverified` and `safe_to_delete=no`. The inventory is a point-in-time snapshot, and its count increases when new reports are added.

## Commands, failures, uncertainty and next inputs

Inspection used `git status --short`, `git log -5 --oneline`, `rg --files`, directory listings, manifest reads, and the read-only inventory script. One commit (`e7d2327`) was found. The scan succeeded; no existing artifact was moved, deleted or regenerated. Candidate consumer detection can miss dynamic imports, absolute paths and indirect data loads. Phase 1 must trace dossier claims to exact artifacts and hash inputs. Phase 3 must map runtime dependencies before any migration.
