# Phase 4 restructuring report — in progress

## Current result

`migration_manifest.csv` records the 866 files from the Phase 0 snapshot, their current SHA-256 hashes, Git status at inventory, evidence track and a proposed destination. It proposes 402 moves and explicitly records **zero executed moves**. A parser check found zero missing source files and zero proposed-destination collisions at generation time. The manifest is a migration plan, not evidence that the target tree is populated.

## Files inspected and commands

Used the Phase 0 inventory, Phase 3 ownership matrix, current Git status and the existing source/data/result directories. Ran `python scripts/audit/build_migration_manifest.py` from `.venv_clean` and checked its CSV with Python's `csv` and `Counter`. The script streams file hashes in 1 MiB blocks and does not write to source paths.

## Changes and tests

Added `scripts/audit/build_migration_manifest.py`, `reports/migration_manifest.csv` and this report. No existing code, raw data, frozen-looking result, ZIP bundle or temporary file was moved, copied over or deleted. No application tests were needed for a read-only manifest; the CSV shape and destination uniqueness were checked.

## Why execution remains gated

The proposed path mapping is intentionally broad and has not been approved as an executable migration. Existing scripts, dashboard routes and provenance JSON still refer to original locations. Moving 402 files before a canonical reader and compatibility strategy exists would break reproduction and could detach untracked artifacts from their generating commands. The manifest also represents the Phase 0 snapshot; files added after that snapshot require a later manifest revision before any move.

## Evidence status and next inputs

This phase is **not complete**. The next safe implementation step is to add the canonical configuration and guarded reader/writer interfaces under the proposed structure, test them against retained originals, update the migration manifest, and then migrate one bounded group at a time with post-move hash and consumer checks. README and entry-point documentation should be revised only when the canonical command actually runs. Historical V1–V5 and negative logs remain in place until their archive index and compatibility access are verified.

## Additive canonical layout progress

Added `src/nadi/core/layout.py`, `configs/canonical/authentic_xylem.json`, `docs/canonical/README.md`, and `archive/README.md`. The layout resolves an explicit input, computes input/config hashes, restricts output roots to `results/canonical`, and creates each run directory exclusively (`exist_ok=False`). It rejects path-like run identifiers. The configured EA input hash matches the audited processed table. Three semantic tests in `tests/test_canonical_layout.py` passed: configuration identity, refusal to reuse a run directory, and rejection of an output rooted at `results/authentic_locked`.

This is an additive structure, not migration completion. Existing scripts and the dashboard still use their prior paths. The migration manifest predates these additions and must be refreshed when the canonical command and target paths are settled. No old data or result was moved.

## Guarded run and refreshed manifest

Added `scripts/canonical/run_authentic.py` as a transitional entry path. It requires an explicit canonical config, checks that the config matches the presently audited endpoint/seed/budget/domain, creates a new run directory exclusively, calls the existing experiment script without changing its mathematics, and records command, source/data/config hashes, logs, return code and output hashes. The run `results/canonical/authentic/audit_20261120_02` succeeded and its five scientific outputs matched `results/authentic_locked` byte-for-byte. A repeated run ID failed before experiment execution. The migration-manifest generator was updated to discover files added after Phase 0; its refreshed output lists 896 current/snapshot entries, 403 proposed moves and zero executed moves.

Updated the README and canonical entry-point report to name the guarded workflow. Historical files remain where they were. Phase 4 is still incomplete as a full physical restructuring: provenance readers, dashboard and legacy scripts still use original paths, and the proposed moves have not been executed. The next bounded migration must verify consumer compatibility and post-move hashes; no wholesale move is justified by the manifest alone.

## Historical index and stricter experiment identity

Added `docs/historical/README.md` to identify V1–V5 simulation generations, the V3 budget/empty-event defects, the V4 correction, and the V5 later simulation. Added `configs/historical/README.md` without relocating versioned configs. The migration planner now retains files already under canonical/historical destinations; its refreshed manifest has 898 entries, 402 proposed moves, zero executed moves. No collision or missing source was reported in the refresh.

The canonical EA configuration now pins the processed-input SHA-256 and all date windows actually hard-coded in the historical experiment. The wrapper rejects a changed input or a configuration that would misdescribe those hard-coded splits. `pytest tests/test_canonical_layout.py` passed (3 tests). A fresh guarded run `results/canonical/authentic/audit_20261120_03` produced five scientific files byte-identical to the pre-existing authentic locked artifacts, now with the wrapper and layout included in its source manifest. This verifies wrapper reproducibility for the current audited input, not label-release timing or external transfer.

## Phase 4 gate

The additive canonical authentic path is usable, but the requested repository-wide restructuring is **not yet complete**. Historical artifacts have been indexed rather than moved because consumers and provenance still reference old paths. The legacy package CLI and dashboard remain outside the canonical ownership boundary. Those paths must be redirected or explicitly frozen before a move is executed. The next phase of work is to establish that boundary and a single command surface, then update the migration manifest with executed moves and post-move hashes where a bounded move is safe.

## Dashboard ownership correction

Added `configs/canonical/dashboard.json` and `src/nadi/dashboard/authentic_view.py`. The authentic route now resolves one explicit canonical run ID, checks its PASS manifest, domain/evidence class and four output hashes, and returns 503 on unavailable or altered evidence. It no longer reads `results/authentic_locked` directly or silently substitutes another authentic run. Unknown round IDs return 404 rather than silently showing the last round. The API says `AUTHENTIC_RETROSPECTIVE_REPLAY` and discloses the same-round reveal assumption and mixed environmental-water material. The visible page also states that laboratory turnaround was not modelled. The separate V5 simulation route no longer silently falls back to V4 while calling it V5. `pytest tests/test_dashboard.py tests/test_canonical_layout.py tests/test_authentic_provenance.py` passed (8 tests).

The current migration manifest refresh has 909 entries, 402 proposed moves, zero executed moves. Phase 4 remains open because the legacy package CLI, many auxiliary scripts, and direct old-path readers have not been fully isolated. This report records a verified bounded migration of the *dashboard reader*, without relocating any user-owned evidence.

A focused tamper test then replaced the dashboard hash function with a mismatching digest and confirmed the authentic API returns 503 instead of showing an unchecked result (`pytest tests/test_dashboard.py`: 5 passed). This test verifies the refusal path, not resistance to a malicious actor who can edit both artifacts and manifest.

## Package command boundary

Added `src/nadi/canonical_cli.py` and changed the installed `nadi` entry point to it; the former package CLI is retained as `nadi-legacy` and `python -m nadi.cli`. The guarded CLI currently implements `verify-data` and `evaluate-authentic` with explicit config/run IDs. `verify-data` checks the pinned input bytes, site/date uniqueness, pre-round feature cutoff, origin and label shape, and writes a new audit result and hash manifest. `evaluate-authentic` writes only to a fresh canonical run. The dashboard is pinned to `audit_20261120_04`, produced through that package command. Its five experiment outputs are byte-identical to the corresponding original authentic experiment outputs. `metric_85_feasibility_audit.json` in the old directory is a separate auxiliary file and was not produced by this command.

The README no longer recommends the old default command that would overwrite `results/authentic_locked`. The CLI does not yet provide all Phase 5 requested stages; this is an explicit partial boundary, not a complete Phase 5 claim. The full existing test suite passed after these changes (77 tests). Focused canonical CLI tests verify the data check, manifest creation, exclusive run ID and refusal of a mismatched input hash (10 focused tests passed together with dashboard/layout tests).

Final manifest refresh for this step: 921 entries, 402 proposed moves, zero executed, zero missing source files and zero proposed-path collisions. Counts in earlier sections are historical snapshots of the migration plan as the additive structure was built.

## Authentic preparation lineage

Added `configs/canonical/prepare_authentic.json` and the guarded `nadi prepare-authentic` command. It pins the 6.07 MB raw UK EA file by SHA-256, calls the existing site-day builder under a fresh output directory, and records output/source/config hashes and a material-domain boundary. The first prepared CSV was byte-identical to the existing `data_processed/ea_authentic_site_rounds_2024.csv`. The authentic evaluation config now names that specific preparation manifest; the evaluation wrapper verifies its prepared CSV hash before training. The fresh `audit_20261120_05` evaluation succeeded and the dashboard now points to it. The full suite passes (79 tests). This establishes reproducible raw-to-prepared-to-evaluation lineage for the current dataset. It does not establish prospective laboratory release timing or drinking-water transfer.

Added a separate `nadi evaluate-hydraulics` command with a pinned BWFLnet prediction file and baseline metrics file. It independently recomputed 18,171 pressure predictions over 673 timestamps and 27 internal loggers: median per-logger MAE 0.278216 m, aggregate MAE 0.414748 m, and 66.34% median-MAE improvement relative to the declared training-mean baseline. Its result says explicitly that the command does not retrain, that the validation week was previously inspected, and that pressure is not biological truth. The hydraulic output is stored under `results/canonical/hydraulics/`, separate from authentic microbiology.

## Explicit risk-model stages

Added `nadi train-risk` and `nadi calibrate-risk` with separate immutable runs. Training fits the three authentic-model estimators only through 31 May 2024. Calibration then reads the pinned training manifest, verifies the model bundle hash, applies Platt calibration and selects thresholds only on 1 June–15 July. The evaluation configuration pins the calibration manifest and its bundle; the wrapper verifies both before the locked October–December replay. New canonical evaluation `audit_20261120_06` used that staged bundle. Its three scientific CSV outputs (events, policy summary and site predictions) remain byte-identical to the historical authentic results. The JSON report intentionally differs because it now records the model-bundle lineage. Focused stage/dashboard/model tests passed (12 tests).

## Final structural disposition

The requested *canonical* structure is now operational: canonical modules,
configs, scripts, results, reports, dashboard reader, command surface and
research documents have an explicit current ownership boundary. The installed
`nadi` command routes to the guarded CLI; the earlier CLI is intentionally
renamed `nadi-legacy`.

The 404 proposed historical relocations have **not** been executed. This is a
deliberate preservation decision, not an unrecorded omission: raw/legacy files
are still consumed by historical reproducibility scripts and moving them would
invalidate their recorded paths without a complete consumer migration.
`archive/README.md`, `docs/historical/README.md`,
`configs/historical/README.md`, and the hash-backed
`reports/migration_manifest.csv` make their status explicit. The final manifest
contains 1,049 entries, 404 proposed moves and zero executed moves.

Accordingly, NADI has a clean supported **current** route while retaining a
non-destructive archive boundary. A future physical migration must be a
separate compatibility project; it is not necessary to reproduce or inspect
the canonical system and must not be represented as already completed.
