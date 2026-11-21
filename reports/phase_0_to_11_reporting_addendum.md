# Phase 0–11 reporting addendum

This addendum standardizes the reporting fields requested in the master
objective. It supplements, rather than replaces, the detailed phase reports.
Evidence classes retain their meanings: `LAB_CONFIRMED`, `OBSERVED`,
`SIMULATED`, `MODEL_ESTIMATE`, and `ASSUMED`.

## Phase 0 — inventory

- **Files inspected:** repository tree, Git state/history, package, data,
  results, logs, dashboard, distribution bundles and virtual environments.
- **Commands/tests:** inventory scanner and read-only Git inspection.
- **Changes/results:** created the complete inventory and classification CSV.
- **Failures/uncertainties:** historical/generated ownership was initially
  mixed; classification is an audit judgement, not a claim of scientific validity.
- **Evidence/risks/next input:** inventory supports all later phase decisions;
  no destructive action occurred; Phase 1 reconciles claims.

## Phase 1 — dossier reconciliation

- **Files inspected:** dossier, source scripts, authentic/pressure/simulation
  outputs and test artifacts.
- **Commands/tests:** result-to-artifact checks and byte/metric reconciliation.
- **Changes/results:** recorded which numerical claims are supported, tied or
  negative; corrected the EA domain to mixed environmental water.
- **Failures/uncertainties:** source data lack true laboratory-result release
  times; hydraulic and biological tracks are not field-joined.
- **Evidence/risks/next input:** `reports/phase_1_dossier_code_reconciliation.md`;
  Phase 2 narrows the canonical claim.

## Phase 2 — canonical system

- **Files inspected:** reconciliation evidence and execution entry points.
- **Commands/tests:** architecture/ownership review; later CLI tests cover the
  resulting boundary.
- **Changes/results:** defined laboratory-risk prioritization as the only
  primary validated claim; separated hydraulic, simulated, telemetry and transfer tracks.
- **Failures/uncertainties:** no shared biological/network event table exists.
- **Evidence/risks/next input:** canonical architecture and evidence-boundary
  documents; Phase 3 traces implementation ownership.

## Phase 3 — ownership/dependencies

- **Files inspected:** scripts, package modules, configs, dashboards, notebooks,
  results and tests.
- **Commands/tests:** dependency and duplicate-logic audit.
- **Changes/results:** identified duplicate policy/metric paths, stale “locked”
  terminology, dashboard bypass risk and distinct authentic versus simulated
  SDAIF implementations.
- **Failures/uncertainties:** legacy paths remain intentionally available.
- **Evidence/risks/next input:** Phase 3 reports; Phase 4 builds a guarded route.

## Phase 4 — structure/preservation

- **Files inspected:** migration candidates, provenance references and legacy
  consumers.
- **Commands/tests:** migration-manifest refresh and dashboard compatibility tests.
- **Changes/results:** added canonical/historical structure, project structure
  guide, archive index and non-destructive migration manifest.
- **Failures/uncertainties:** 402 physical moves remain deferred because legacy
  consumers require original paths; no raw data were moved.
- **Evidence/risks/next input:** 1,015 migration entries and 25 indexed
  historical/superseded artifacts; Phase 5 owns execution safety.

## Phase 5 — canonical CLI

- **Files inspected:** package entry points, configs, canonical artifacts.
- **Commands/tests:** installed `nadi` CLI; guarded preparation, training,
  calibration, evaluation, simulation, reporting, audit and test commands.
- **Changes/results:** every canonical command requires config/run ID, logs
  hashes and refuses existing output directories.
- **Failures/uncertainties:** legacy CLI remains for historical reproduction;
  it is not a canonical entry path.
- **Evidence/risks/next input:** Phase 5 report and `nadi --help`; Phase 6
  audits data and selection integrity.

## Phase 6 — integrity/leakage

- **Files inspected:** authentic processed data, split definitions, policy
  event files, calibration lineage, transfer/hydraulic records.
- **Commands/tests:** integrity invariant tests and causal-feature checks.
- **Changes/results:** verified date/site isolation, causal cutoffs, common
  candidate budget and canonical hashes; added a 2,000-permutation
  common-candidate random baseline audit.
- **Failures/uncertainties:** laboratory availability times, selection bias,
  broad external overlap and prospective field validation remain unavailable.
- **Evidence/risks/next input:** Phase 6 audit; Phase 7 tests semantic behavior.

## Phase 7 — tests/reproducibility

- **Files inspected:** full package, test suite, locks and dependency metadata.
- **Commands/tests:** fresh isolated venv install from `requirements-lock.txt`,
  `pytest`, then guarded `nadi run-tests`.
- **Changes/results:** isolated run exposed missing `openpyxl`; pinned it in
  both dependency declarations, added a regression check, and reran successfully: **88 passed**.
- **Failures/uncertainties:** this proves software reproducibility, not field
  biological validity.
- **Evidence/risks/next input:**
  `results/canonical/tests/audit_20261120_isolated_02`; Phase 8 reconciles results.

## Phase 8 — result reconciliation

- **Files inspected:** authentic, transfer, hydraulic, simulation, telemetry
  and adaptation artifacts.
- **Commands/tests:** canonical performance-matrix builder and schema test.
- **Changes/results:** created one evidence-labeled matrix retaining ties,
  poor transfer and negative L-TOWN findings.
- **Failures/uncertainties:** metrics cannot turn a simulated result into a
  biological one.
- **Evidence/risks/next input:** performance matrix; Phase 9 constrains claims.

## Phase 9 — scientific contribution

- **Files inspected:** prior-art documents, claim matrix, performance matrix
  and implementation boundary.
- **Commands/tests:** claim-boundary audit.
- **Changes/results:** approved the narrow contribution—auditable fixed-budget
  testing prioritization—and prohibited unsupported detection/deployment claims.
- **Failures/uncertainties:** no standalone globally novel theorem is established.
- **Evidence/risks/next input:** approved/prohibited claims; Phase 10 presents them.

## Phase 10 — research presentation

- **Files inspected:** canonical artifacts and matrix.
- **Commands/tests:** JSON/notebook execution test against clean environment.
- **Changes/results:** built 18-section notebook with evidence labels and
  limitations.
- **Failures/uncertainties:** no visualization is allowed to blur authentic and
  simulated evidence classes.
- **Evidence/risks/next input:** notebook and report; Phase 11 writes manuscript.

## Phase 11 — manuscript/final acceptance

- **Files inspected:** canonical architecture, performance matrix, claims,
  notebook and reproducibility manifests.
- **Commands/tests:** manuscript cross-check, installed CLI verification and
  final acceptance audit.
- **Changes/results:** produced evidence-corrected manuscript and final
  acceptance audit; the final abstract was written after reconciled results.
- **Failures/uncertainties:** future field collection remains required for a
  unified drinking-water contamination-to-response claim.
- **Evidence/risks/next input:** the next external work is qualified
  field/laboratory validation, not stronger wording of current results.
