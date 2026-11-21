# Phase 6 — data integrity and leakage audit

## Scope and result

This audit evaluates the canonical UK Environment Agency mixed
environmental-water E. coli replay, the BWFLnet pressure reconstruction, and
the Net3 simulation as separate tracks. It does not infer that passing a
software check validates drinking-water contamination detection.

## Checks that pass

| Topic | Evidence | Result |
|---|---|---|
| Chronological split | Training ends 2024-05-31; calibration 2024-06-01 to 2024-07-15; validation 2024-07-16 to 2024-09-30; locked test starts 2024-10-01 | PASS: index sets and dates disjoint |
| Same-date history isolation | `build_site_day_table` computes all rows for a date before pending outcomes update site, region, or global history | PASS: unit test and 13,405-row invariant |
| Duplicate site-day rows | `round_date` + `samplingPoint.notation` | PASS: zero duplicates in canonical CSV |
| Replicate consolidation | Source aggregation uses the maximum high-count endpoint with `replicate_count` retained | PASS: code inspected; endpoint rule explicit |
| Feature cutoff | Every canonical row has `feature_cutoff < round_date` | PASS: 13,405-row invariant |
| Calibration/threshold separation | Train, calibration, validation, and locked partitions are separate; calibration stage is pinned to a pre-test training manifest | PASS in code and artifact lineage |
| Policy budget and candidate fairness | 41 replay rounds; every policy sees same recorded round size/positive count and budget 3 | PASS: event-table invariant |
| Adaptive update implementation | First choice depends only on predictions and priors; only selected outcomes enter posterior update | PASS for algorithmic replay |
| Site-held-out subgroup definition | 50 locked rows / 31 sites absent from training-site labels | PASS as a subgroup definition; performance remains weak |
| Canonical artifact integrity | Authenticated events/summary hash against the canonical run manifest | PASS |

## Findings that limit the claim

| Topic | Finding | Consequence |
|---|---|---|
| Laboratory result availability | EA source has collection time but no result-release timestamp. The replay exposes a selected same-round result immediately. | Sequential adaptation is an analytical replay, not a validated real-time culture workflow. |
| Sampling-selection bias | `sampling_purpose` is a current-row feature and historical EA sites were not selected by a NADI-random sampling design. | Retrospective ranking may not estimate performance under an operationally random/representative test stream. |
| Candidate-set availability | Candidate sites are reconstructed from observed same-date agency samples, rather than an independently archived pre-decision eligible outlet list. | The decision problem is retrospective and conditional on the observed candidate set. |
| Random comparator | The frozen baseline remains a deterministic SHA-derived order, and a separate 2,000-permutation common-candidate audit quantifies random-policy uncertainty (mean 82.62; 95% range 75–90). | The historical 80-result comparator remains reproducible; random uncertainty is now explicit. |
| Oracle comparison | Oracle is `min(budget, observed positive candidates)` within each observed round. | It is a conditional discovery reference, not a public-health or population-exposure oracle. |
| Unseen-site transfer | 50 rows: F1 0.722, ROC-AUC 0.705, specificity 0.182. | No universal or city-transfer claim. |
| External overlap | No formal source-level deduplication against every external dataset is encoded. | External comparisons remain separate and cannot be pooled as independent evidence. |
| BWFLnet validation reuse | The validation week was previously inspected during development. | Hydraulic performance is supportive reconstruction evidence, not pristine final validation. |
| Simulation | Net3 and L-TOWN are assumed/simulated scenarios with no paired microbial labels. | No biological or field contamination claim. |

## Required interpretation

The canonical microbial result supports: *given an observed UK EA monitoring
round, historical past-only features and a three-test budget retrospectively
prioritized laboratory-confirmed high E. coli results better than the declared
routine and the evaluated random-policy distribution.* It does **not** establish a
prospective testing advantage until a time-stamped, independently selected
sampling protocol records when results became available.

## Files inspected and commands run

- `src/nadi/authentic/site_rounds.py`
- `scripts/run_authentic_xylem_experiment.py`
- `src/nadi/authentic/benchmark.py` and `policy.py`
- canonical authentic events, summary, and manifest
- canonical BWFLnet and Net3 manifests
- `pytest tests/test_integrity_invariants.py tests/test_authentic_site_rounds.py tests/test_authentic_benchmark.py tests/test_authentic_policy.py` — 11 passed

## Next-phase inputs

Phase 7 should turn the checks above into persistent semantic tests where they
are not already covered, ensure frozen-result refusal and dashboard API behavior
remain tested, and retain the unsupported items as explicit limitations rather
than silently relaxing them.
