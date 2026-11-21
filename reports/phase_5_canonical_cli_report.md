# Phase 5 — canonical CLI report

## Result

The installed `nadi` entry point now exposes one guarded command surface:

```text
nadi audit
nadi verify-data
nadi prepare-authentic
nadi train-risk
nadi calibrate-risk
nadi evaluate-authentic
nadi evaluate-sdaif
nadi evaluate-hydraulics
nadi run-simulation
nadi build-report
nadi build-manifest
nadi run-tests
```

Every command requires `--config` and `--run-id`. Each writes only to a new
directory below `results/canonical/`, records input/config/source/output SHA-256
hashes, seed, output path, command status, and the evidence class/domain. A
reused run ID raises before an existing result is overwritten. The old package
commands remain available only through `nadi-legacy` or `python -m nadi.cli`.

## Implemented workflows

| Command | Evidence and result | Status |
|---|---|---|
| `prepare-authentic` | Pinned raw EA file to a new leakage-safe site-day CSV | Rebuilt output byte-identical to audited processed CSV |
| `verify-data` | Input hash, schema, duplicate site-day, causal cutoff, labels, origin | PASS |
| `train-risk` | Fits pre-31-May estimators only | PASS |
| `calibrate-risk` | Pins training manifest; Platt calibration and threshold on Jun–Jul only | PASS |
| `evaluate-authentic` | Pins preparation and calibration artifacts; reruns locked Oct–Dec replay | PASS; scientific CSV outputs match historical results byte-for-byte |
| `evaluate-sdaif` | Reconciles authentic policy replay | PASS; reports ties rather than superiority |
| `evaluate-hydraulics` | Recomputes BWFLnet pressure metrics from pinned predictions | PASS; separate observed-pressure track |
| `run-simulation` | Re-executes declared Net3 benchmark into canonical output | PASS; event and aggregate CSVs match V5 byte-for-byte |
| `build-manifest` | Hash manifest for explicit artifacts | PASS |
| `audit` | Checks three evidence-track manifests and prohibited boundary | PASS |
| `build-report` | Generates evidence-separated summary | PASS |
| `run-tests` | Captures full pytest output under canonical results | PASS, 88 tests in the latest isolated installed-CLI run |

## Commands and tests

All commands were run through the clean environment with configurations in
`configs/canonical/`. The latest retained isolated installed-CLI test run is
`results/canonical/tests/audit_20261120_isolated_04` and reports
`88 passed in 21.69s`.

## Evidence boundary

The authentic EA result is retrospective mixed environmental-water
prioritization. The BWFLnet result is pressure reconstruction. Net3 is
simulation. The CLI carries those labels forward and does not join the tracks.
It does not validate direct E. coli detection, pipe contamination localization,
Delhi-NCR performance, illness reduction, or integrated biological-hydraulic
field operation.

## Remaining risks and next inputs

The package CLI is complete in command coverage, but Phase 6 must verify the
semantics of chronological splits, release timing, policy fairness, selection
bias, transfer leakage and non-pristine hydraulic validation. The existing
regression suite does not yet prove every requested integrity property.
