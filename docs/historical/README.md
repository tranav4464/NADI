# Historical work and protocol status

The dated V1–V5 network benchmarks are **simulated hydraulic/tracer experiments**.
They are retained in `results/locked/` at their original paths, with configurations
in `configs/` and the governing corrections in `logs/protocol_deviations.md`.
The name `locked` records the original experiment convention; it does not mean
the files are write-protected. Use the Phase 4 migration manifest before moving
any of them.

| Generation | Current file family | Status and reason |
|---|---|---|
| V1 | `locked_benchmark_v1_*` | Historical. SDAIF received sequential result access while the Bayesian comparator was static. |
| V2 | `locked_benchmark_v2_*` | Historical. Added an adaptive Bayesian comparator; the first summary had a wrong configuration hash and was rerun. Preserve the correction history. |
| V3 | `locked_benchmark_v3_*` | Superseded for performance claims. Its conditional decision compared inconsistent test budgets and its empty-event coverage convention was wrong. |
| V4 | `locked_benchmark_v4_*` | Corrected simulation generation with committed tests and nonempty-event accounting. |
| V5 | `benchmark_v5_no_placeholders_*` | Later no-placeholder simulation generation. It is distinct from the authentic EA experiment. |
| V4 delay regression | `regression_v4_delay_engine_*` | A regression check of delayed decision code, not an independent contamination trial. |
| Small test output | `test_benchmark_*` | Generated test artifact, not a headline result. |

The primary empirical Xylem evidence is the separate UK Environment Agency
mixed environmental-water experiment under `results/authentic_locked/`.
BWFLnet real pressure reconstruction is separate under `results/bwflnet_full_hybrid/`.
Neither track biologically validates a drinking-water pipe response.

See `reports/evidence_track_boundaries.md`, `reports/phase_1_dossier_code_reconciliation.md`,
and `reports/phase_3_duplicate_logic_report.md` before reusing any result.
