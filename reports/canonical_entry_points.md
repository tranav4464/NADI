# Canonical entry points — Phase 2 current-state map

## What executes today

| Workflow | Current command | Source implementation | Output and side effect | Proposed disposition |
|---|---|---|---|---|
| EA site-day construction | `python scripts/build_authentic_site_rounds.py` | `nadi.authentic.site_rounds` | Overwrites `data_processed/ea_authentic_site_rounds_2024.csv` and its report | Wrap in canonical CLI with explicit input/config/fresh output |
| EA model and decision replay | `python scripts/run_authentic_xylem_experiment.py --output-dir <fresh>` | `nadi.authentic.models`, `policy`, `benchmark`, `spatial` | Writes report, events, summary and predictions; default output would overwrite named locked files | Canonical primary path after output guard and release-time contract |
| BWFLnet pressure evaluation | `python scripts/train_bwflnet_full_hybrid.py` | Script-local training plus `nadi.hydraulics.pressure_features` | Writes model and reports to fixed directory | Separate supporting command; protect existing artifacts |
| Net3 benchmark | `nadi benchmark ...` and versioned configs | `nadi.evaluation.benchmark`, hydraulic ensemble and SDAIF | Writes simulated benchmark files | Historical/simulation command only |
| L-TOWN stress | Versioned evaluation scripts/configs | `nadi.hydraulics`/SDAIF scripts | Simulated tracer metrics | Simulation command only |
| Dashboard | `app/server.py` / `START_NADI.bat` | Flask routes plus static UI | Reads result files and may reconstruct an authentic replay | Audit against canonical API before promotion |
| Legacy package CLI | `nadi-legacy` or `python -m nadi.cli` | `src/nadi/cli.py` | Exposes `freeze-resources`, `audit-resources`, `prepare`, `train-risk`, `generate-hydraulics`, `build-evidence`, `run-demo`, `benchmark` | Historical reproduction only; it does not expose the authentic canonical pipeline |

`scripts/canonical/run_authentic.py` is the guarded evaluator used by the package CLI. It requires `--config` and `--run-id`, creates an exclusive output directory, records source/data/config hashes, and reproduces the authentic experiment. Canonical output `audit_20261120_07` preserves byte-identical scientific CSV outputs relative to the historical authentic result while adding preparation and calibration lineage.

The installed `nadi` package entry point now routes to `nadi.canonical_cli`.
`nadi prepare-authentic` builds the EA site-day table from the pinned raw file
in a fresh run directory. Its first output matched the prior processed CSV
byte-for-byte. The evaluation config pins that preparation run manifest and
the evaluation wrapper checks the prepared file against the audited input hash.
`nadi verify-data` checks the pinned authentic input hash, schema, site/date
uniqueness, causal feature cutoff, labels and origin, and writes a fresh audit
manifest. `nadi train-risk` fits only the chronological pre-May model estimators.
`nadi calibrate-risk` attaches Platt calibration and validation-only thresholds
from the next chronological window. `nadi evaluate-authentic` verifies the
calibrated bundle and invokes the exact locked experiment against that bundle.
It writes a new run manifest. `nadi evaluate-hydraulics` recomputes pressure metrics
from pinned BWFLnet predictions and a pinned baseline, without training or
biological inference. All require explicit config and unique run ID. The
Old development commands remain under `nadi-legacy` / `python -m nadi.cli` for
historical reproduction and are not canonical. The guarded package CLI now
also supplies `audit`, `evaluate-sdaif`, `run-simulation`, `build-report`,
`build-manifest`, and `run-tests`. See `reports/phase_5_canonical_cli_report.md`
for the full command-to-artifact map and evidence boundary.

Phase 2 changes were documentation only. No tests were needed for these boundary reports; Phase 1's authentic fresh rerun and stored-prediction arithmetic are the supporting checks. Remaining risks are unguarded default writes, ambiguous “locked” naming, dashboard bypasses, and separate result generations. The next phase input is the source-to-artifact dependency map.
