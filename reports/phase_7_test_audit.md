# Phase 7 — Test and reproducibility audit

## Scope

This audit tested the canonical system as a set of semantic invariants, not
merely as an existence check for already-generated files. The audit was run in
the clean project environment with:

```text
<fresh-isolated-environment>\\Scripts\\python.exe -m pytest
```

The canonical invocation was also captured through the installed package entry
point (after a clean editable reinstall):

```text
nadi run-tests --config configs/canonical/run_tests.json --run-id audit_20261120_isolated_04
```

## Result

**PASS — 88 tests in 21.69 seconds in a genuinely isolated virtual
environment.** The canonical run manifest is
`results/canonical/tests/audit_20261120_isolated_04/run_manifest.json`; it
records return code 0, source/config/input hashes and hashes of the retained
test logs.

The first isolated run exposed that `openpyxl` was used by the EPA workbook
audit but absent from both declared dependency files. It was added as
`openpyxl==3.1.5` to `pyproject.toml` and `requirements-lock.txt`, and the
guarded test configuration hash was updated before this passing rerun. A
regression test now requires the reader to appear in both declarations. This
is a resolved reproducibility defect, not a suppressed failing test.

## Tested properties

| Area | Semantic checks covered |
|---|---|
| Authentic input and provenance | Required schema, pinned hashes, binary endpoint, single site-day representation, evidence class and material domain |
| Causality and leakage | Chronological partitions, same-date isolation, pre-round feature cutoffs, train/validation/test separation and unseen-site exclusion |
| Risk stages | Training-boundary enforcement, calibration lineage, calibration/threshold isolation and locked-evaluation lineage |
| Testing policies | Common candidate rounds, common budget, budget feasibility, deterministic replay and adaptive update using revealed outcomes only |
| SDAIF mathematics | Regret calculation, Bayesian/update behavior, abstention, delayed-evidence and fusion invariants |
| Hydraulic and simulation tracks | Pressure-feature dimensions, source/localization and placement constraints, explicit simulated labels and separate evidence classes |
| Canonical safety | Explicit configuration/run IDs, refusal to reuse an output directory, input-hash mismatch refusal and frozen-result protection |
| Dashboard and claims | Canonical-artifact hash verification, refusal on a tampered manifest/output, evidence-class propagation and claim-boundary checks |
| Presentation artifacts | Canonical performance matrix schema and 18-section research notebook execution |

## What the passing tests do not prove

The test suite does not establish biological validity in drinking-water pipes,
municipal deployment, real-time laboratory availability, Delhi-NCR transfer,
or health impact. It verifies the implementation, provenance and stated
evidence boundaries for the available datasets. Those limits remain recorded
in `reports/phase_6_integrity_and_leakage_audit.md` and
`reports/prohibited_claims.md`.
