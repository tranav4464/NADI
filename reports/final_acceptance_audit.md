# Final acceptance audit — canonical NADI system

## Objective tested

Transform the accumulated NADI workspace into one reproducible,
evidence-separated water-safety decision-intelligence project without deleting
historical work, manufacturing stronger claims, or merging incompatible data.

## Acceptance evidence

| Required outcome | Current evidence | Status |
|---|---|---|
| Safe inventory and file classification | `reports/phase_0_repository_inventory.md`, `reports/phase_0_file_classification.csv` | PASS |
| Dossier-to-code reconciliation | `reports/phase_1_dossier_code_reconciliation.md` | PASS |
| One canonical system plus separated tracks | `reports/canonical_architecture.md`, `reports/evidence_track_boundaries.md` | PASS |
| Execution/dependency ownership audit | Phase 3 reports | PASS |
| Preservation and migration record | `reports/migration_manifest.csv`, `archive/historical_index.csv` (25 retained historical/superseded artifacts), historical indexes; no destructive move/delete made | PASS |
| One canonical command surface | `nadi` CLI and `reports/phase_5_canonical_cli_report.md` | PASS |
| Data-integrity and leakage audit | `reports/phase_6_integrity_and_leakage_audit.md` | PASS with stated limitations |
| Semantic test/reproducibility audit | `reports/phase_7_test_audit.md`; fresh isolated environment, canonical run: 88 passed | PASS |
| Reconciled performance matrix | `reports/canonical_performance_matrix.csv` | PASS |
| Narrow evidence-supported contribution and claim controls | Phase 9 reports | PASS |
| Executable research notebook | `notebooks/NADI_Canonical_Evidence_Notebook.ipynb` and Phase 10 report | PASS |
| Evidence-corrected manuscript | `docs/canonical/NADI_Evidence_Corrected_Manuscript.md` and Phase 11 report | PASS |
| Standard phase reporting | `reports/phase_0_to_11_reporting_addendum.md` | PASS |

## Canonical research conclusion

The supported primary result is an **authentic retrospective UK mixed
environmental-water E. coli fixed-budget testing-prioritization experiment**.
It uses causal features, calibrated risk models and SDAIF to produce a ranked
testing order. The observed hydraulic pressure study and simulation studies are
separate, correctly labelled supporting tracks.

## Non-negotiable claim boundary

The cleaned project still does **not** prove direct E. coli detection by
ordinary sensors, pipe contamination localization, Delhi/Ghaziabad performance,
prospective municipal effectiveness, health-outcome reduction or a field-joined
biological-hydraulic model. These exclusions are enforced in the claim matrix
and are requirements for any future presentation.

## Repository decision

Historical and generated files remain in their original locations to preserve
their hashes, provenance and existing consumers. The canonical CLI, configs,
results and dashboard view form the only supported current entry path. The
historical archive index identifies 25 historical/superseded artifacts by
original path and evidence track; broader generated artifacts are retained in
the migration manifest rather than silently deleted or presented as canonical.

The intended directory layout is documented in
`docs/canonical/PROJECT_STRUCTURE.md`; compatibility directories are present
for future bounded migrations. This preserves reproducibility while preventing
a cosmetic move from breaking hash-pinned historical workflows.
