# NADI Repository Guide

This repository is organised around evidence boundaries rather than a single
monolithic contamination detector. New contributors and reviewers should begin
with the canonical authentic workflow and treat the other tracks as supporting
experiments.

## Canonical workflow

The guarded `nadi` command is the supported entry point:

```text
prepare-authentic -> verify-data -> train-risk -> calibrate-risk
-> evaluate-authentic -> evaluate-sdaif -> build-report
```

Every canonical command accepts an explicit configuration and run ID, writes a
run manifest, records hashes and refuses to overwrite an existing run.

## Evidence boundaries

- Authentic Environment Agency observations support retrospective
  environmental-water risk and testing-priority claims.
- BWFLnet supports hydraulic state-reconstruction claims only.
- Net3 and L-TOWN support conditional simulated network experiments.
- Telemetry datasets support anomaly and operational-state experiments.
- No track alone supports direct E. coli detection from ordinary sensors or a
  biologically validated drinking-water pipe localisation claim.

## Recommended reviewer path

1. Read `docs/CLAIM_MATRIX.md`.
2. Read `docs/canonical/NADI_Evidence_Corrected_Manuscript.md`.
3. Inspect `reports/canonical_performance_matrix.csv`.
4. Run the canonical CLI with fresh run IDs.
5. Run `python -m pytest -q`.
6. Inspect the generated run manifest and claim-boundary audit.

## Historical material

Historical configurations, reports and results are retained for traceability.
They are not canonical merely because their filenames contain words such as
`final`, `locked`, or a higher version number. Canonical ownership is defined by
the current configurations, entry points and claim-to-evidence reports.
