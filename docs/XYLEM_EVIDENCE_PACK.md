# NADI Xylem evidence pack

This page is the reviewer’s shortest route through the current software-first
prototype. The **canonical Xylem result** is the chronologically locked,
authentic EA experiment recorded in `results/authentic_locked/`. Earlier
baseline and proxy tracks remain in the repository for reproducibility, but
they are not alternative headline results and must not be compared as though
they used the same endpoint, split, features, or decision task.

## What is demonstrated

1. A production risk pipeline with temporal train/calibration/untouched-test
   partitions and calibration-aware reporting.
2. Location/regime-adaptive robust normalisation with a global fallback for
   sparse or unseen groups.
3. Typed evidence fusion that retains reliability, support, disagreement and
   dominant uncertainty.
4. Bounded intrusion-context evidence that abstains when observations are
   missing, rather than inventing a contamination pathway.
5. EPANET/WNTR scenario ensembles for uncertain source, demand, tank and pipe
   states, with affected-node reach and arrival intervals. These are retained
   as a clearly separated software demonstration, not scored Xylem evidence.
6. SDAIF sequential testing decisions with delayed-result semantics,
   minimax-regret certificates and explicit abstention.
7. Consequence-weighted, operator-reviewed protective-action ranking.
8. A Flask dashboard, evidence API, reproducibility manifest and automated
   claim-boundary audit.
9. Frozen downloads of the Open E. coli Models, EPA WNTR and EPA EPANET 2.2
   prior-art repositories, with commit IDs recorded in
   `results/prior_art_repository_audit_v1.json`. Acquisition is recorded
   separately from method reproduction.
10. A newly downloaded authentic Environment Agency E. coli laboratory track
    (14,069 confirmed membrane-filtration observations from 2024) with a
    leakage-safe temporal baseline; this is explicitly surface-water evidence,
    not a drinking-network claim.
11. A controlled authentic-subset adaptation of the Open E. coli repository’s
    XGBoost classifier using 648 official EA samples; the full multi-agency
    workflow remains separately marked as not bit-for-bit reproduced.

## Canonical locked authentic results

The final experiment begins with 14,069 confirmed membrane-filtration E. coli
observations from 2024, aggregates them to 13,405 site-day records across 920
sites, and reserves the final 545 records for chronological locked testing.
The endpoint is **E. coli >= 500 CFU/100 mL** in the EA surface-water context.

| Track | Result | Interpretation |
|---|---:|---|
| Locked risk model | F1 0.838; ROC-AUC 0.866; PR-AUC 0.916; sensitivity 0.966; balanced accuracy 0.678; Brier 0.141 | Selected on an earlier validation period, then evaluated once on the 545-row locked period. |
| Three-test SDAIF policy | 114 confirmed high results across 41 authentic multi-site rounds | Same information and budget as every comparator; no positive round missed. |
| Deterministic random policy | 80 confirmed high results | Fixed-seed comparator under the same three-test budget. |
| Routine-frequency policy | 84 confirmed high results | Historical routine-priority comparator under the same three-test budget. |
| Strongest fair policy comparators | Tie on total discoveries | The result supports transparent robustness and decision utility, not universal superiority. |
| Unseen-site transfer stress test | F1 0.722; ROC-AUC 0.705 | Performance falls at unseen sites; NADI requires local calibration or abstention rather than a Delhi-NCR transfer claim. |

## Supporting, non-headline tracks

The repository also preserves EA baselines, GECCO/Bristol proxy work and
EPANET/WNTR/L-TOWN stress tests. They answer narrower implementation questions:
model-family replication, sensor processing, and uncertainty handling. They
are not pooled with the canonical experiment and do not establish a
drinking-water pipeline claim.

The complete canonical metrics, per-round policy outputs, false negatives,
prevalence and calibration data are in
`results/authentic_locked/authentic_experiment_report.json`,
`results/authentic_locked/authentic_test_summary.csv`, and
`results/authentic_locked/authentic_test_events.csv`. Broader exploratory
metrics remain in `results/performance_matrix_v1.json` and
`docs/PERFORMANCE_MATRIX.md`.

## What is not claimed

NADI does not claim direct E. coli detection from ordinary sensors, Delhi or
Ghaziabad field performance, a calibrated municipal digital twin, automatic
utility actuation, prevented illness, or superiority over the strongest fair
baseline. The hydraulic outcomes are simulated tracer-reach outcomes, and the
biological model is a surface-water context model.

## Reproduce and inspect

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\reproduce.ps1
.\.venv\Scripts\python scripts\build_repro_manifest.py
.\.venv\Scripts\python scripts\audit_claim_boundaries.py
```

The dashboard evidence endpoints are `/api/evidence` for the simulation and
provenance artefacts and `/api/authentic` for the observed-data metrics. The
hash-anchored artifact
record is `results/reproducibility_manifest_v1.json`; all tests and claim audits
must be green before presenting the prototype.

The requirement-by-requirement completion audit is in
`docs/AUTHENTIC_BUILD_COMPLETION_AUDIT.md`.

## Xylem mentorship request

The decisive next validation is a bounded, anonymised pressure-zone pilot with
verified operating states and independent confirmatory microbiology. The
requested support is technical review, a safe topology/operations abstraction,
and help designing a prospective comparison against routine sampling—not
endorsement of unsupported field claims.
