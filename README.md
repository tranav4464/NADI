# NADI: Network-Adaptive Decision Intelligence for Water Safety

[![Tests](https://github.com/tranav4464/NADI/actions/workflows/ci.yml/badge.svg)](https://github.com/tranav4464/NADI/actions/workflows/ci.yml)

**NADI is an evidence-separated, uncertainty-aware mathematical decision system
for prioritising limited confirmatory water-quality testing.** It combines
calibrated microbial-risk models, explicit model disagreement, fixed-budget
SDAIF optimisation, and separately validated hydraulic and simulation tracks.

> **Current validated scope:** retrospective testing prioritisation using
> authentic UK Environment Agency laboratory observations. NADI does not claim
> direct sensor-based E. coli detection, a biologically validated pipe-network
> localisation system, or completed municipal deployment.

## What NADI produces

```text
historical laboratory evidence
        -> causal feature construction
        -> calibrated risk-model family
        -> explicit uncertainty representation
        -> SDAIF fixed-budget optimisation
        -> ordered confirmatory-testing list
        -> sequential update after revealed results
        -> auditable decision card
```

The repository deliberately separates four evidence tracks:

| Track | Purpose | Evidence status |
|---|---|---|
| Authentic microbial risk | Retrospective risk estimation and testing prioritisation | Laboratory-linked observations |
| Real-network hydraulics | Pressure/state reconstruction on BWFLnet | Observed/reconstructed, not biological validation |
| Network simulation | Conditional source tracing and placement stress tests | Simulated |
| Transfer and telemetry | Robustness, anomaly, and domain-shift studies | Dataset-specific |

## Repository map

| Path | Contents |
|---|---|
| `src/nadi/` | Canonical Python package and mathematical decision components |
| `configs/canonical/` | Guarded canonical experiment configurations |
| `scripts/canonical/` | Reproducible command-line workflows |
| `tests/` | Semantic, integrity, provenance, and claim-boundary tests |
| `notebooks/` | Executable research companions |
| `results/canonical/` | Canonical structured result artifacts |
| `docs/canonical/` | Evidence-corrected manuscript and canonical documentation |
| `reports/` | Repository, provenance, and scientific audits |
| `figures/` | Generated research and presentation figures |

For orientation, read [`docs/REPOSITORY_GUIDE.md`](docs/REPOSITORY_GUIDE.md),
[`docs/CLAIM_MATRIX.md`](docs/CLAIM_MATRIX.md), and
[`docs/DATA_AND_EVIDENCE.md`](docs/DATA_AND_EVIDENCE.md).

## Guarded canonical authentic run

The audited primary experiment is a retrospective testing-priority study on UK
Environment Agency E. coli observations with **mixed environmental-water
materials**. It does not detect E. coli in drinking-water pipes. Run it with an
explicit configuration and a unique run ID. First create a new virtual
environment that does **not** inherit system packages:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt -e .
```

Then run the canonical CLI:

```powershell
.\.venv\Scripts\nadi.exe prepare-authentic --config configs\canonical\prepare_authentic.json --run-id prepare_001
.\.venv\Scripts\nadi.exe verify-data --config configs\canonical\authentic_xylem.json --run-id verify_001
.\.venv\Scripts\nadi.exe train-risk --config configs\canonical\train_risk.json --run-id train_001
.\.venv\Scripts\nadi.exe calibrate-risk --config configs\canonical\calibrate_risk.json --run-id calibrate_001
.\.venv\Scripts\nadi.exe evaluate-authentic --config configs\canonical\authentic_xylem.json --run-id authentic_001
.\.venv\Scripts\nadi.exe evaluate-hydraulics --config configs\canonical\evaluate_hydraulics.json --run-id hydraulic_001
```

The command refuses an existing run ID and writes a hashed run manifest under
`results/canonical/authentic/<run-id>/`. The existing `results/authentic_locked`
artifacts are retained as historical evidence. The installed `nadi` entry point
uses the guarded CLI; `nadi-legacy` and `python -m nadi.cli` expose the earlier
development workflow and must be treated as historical. See
`reports/canonical_entry_points.md` for the current ownership boundary.

## Current Xylem track: authentic observed evidence only

NADI's current Xylem experiment is an applied-mathematics prototype for deciding
**where limited confirmatory water tests should begin**. Its scored evidence uses
authentic Environment Agency laboratory records, dates, sites and coordinates
only. Generated contamination labels, generated laboratory outcomes and
generated pipe events are excluded from the Xylem result.

The canonical preparation command rebuilds the processed table from the pinned
raw EA file in a fresh run directory; its output was byte-identical to the
existing processed CSV. Evaluation consumes the pinned processed CSV and checks
it against the specific preparation manifest named in its configuration. To
reproduce that configured run in a clean environment, generate the pinned
preparation, training, and calibration run IDs first. Evaluation validates the
calibrated bundle hash but reruns the fixed evaluation logic against it. The
canonical commands refuse to overwrite historical locked files.

Start with [the Xylem submission index](docs/XYLEM_SUBMISSION_INDEX.md). The
BWFLnet hydraulic pressure evidence is evaluated separately and is not part of
the authentic E. coli performance claim. The hydraulic command recomputes
metrics from stored predictions; it does not retrain the estimator.

## Historical development track

The original NADI prototype examined decisions when E. coli-referenced risk
evidence and water-network movement are uncertain.

The [core coupling audit](docs/CORE_COUPLING_AUDIT.md) explains what the current
SDAIF benchmark proves: sequential decisions on simulated tracer reach. The
surface-water E. coli model has not been validated as a node-specific
drinking-water predictor.

The current [open issues register](docs/OPEN_ISSUES_REGISTER.md) tracks the
remaining implementation and evidence gaps against the Xylem plan.

The reviewer-facing [Xylem evidence pack](docs/XYLEM_EVIDENCE_PACK.md)
summarises demonstrated components, measured results and claim boundaries.
The [definition-of-done audit](docs/DEFINITION_OF_DONE_AUDIT.md) separates
software evidence from external field-validation requirements.
The clean-environment reproduction record is in
`docs/CLEAN_ENV_REPRODUCTION.md`.
The authentic-data registry is in `docs/AUTHENTIC_DATASET_REGISTRY.md`.

The executable chain is:

```text
frozen evidence -> calibrated risk interval -> uncertain network reach
-> candidate consequences -> adaptive SDAIF test plan -> decision card
```

The project keeps four evidence types separate:

- `LAB_CONFIRMED`: an accepted microbiological result in its original dataset;
- `OBSERVED`: weather, telemetry, or network input actually recorded in its source;
- `MODEL_ESTIMATE`: calibrated or simulated model output;
- `SIMULATED`: constructed network event or hidden benchmark truth.

The current dashboard also exposes an explicitly bounded intrusion-context
layer and an operator-reviewed protective-action ranking. With no public
sewage/pipe-defect observations in the benchmark, the intrusion layer abstains
instead of inventing a hazard signal; protective actions remain advisory and
are never automatic actuation.

When the Flask dashboard is running, `/api/evidence` exposes the frozen
performance matrix and reproducibility manifest for inspection by a reviewer;
`/api/authentic` exposes the separately audited observed-data metrics.

NADI does **not** claim that ordinary sensors directly detect E. coli, that the benchmark is Delhi's real pipe network, or that the software has already prevented illness.

## Reproduce

The supported reproduction route is the guarded canonical CLI. Use fresh run
IDs; a command will refuse to overwrite an existing canonical result.

```powershell
.\.venv\Scripts\nadi.exe prepare-authentic --config configs\canonical\prepare_authentic.json --run-id prepare_review_001
.\.venv\Scripts\nadi.exe train-risk --config configs\canonical\train_risk.json --run-id train_review_001
.\.venv\Scripts\nadi.exe calibrate-risk --config configs\canonical\calibrate_risk.json --run-id calibrate_review_001
.\.venv\Scripts\nadi.exe evaluate-authentic --config configs\canonical\authentic_xylem.json --run-id authentic_review_001
.\.venv\Scripts\nadi.exe evaluate-sdaif --config configs\canonical\evaluate_sdaif.json --run-id decision_review_001
.\.venv\Scripts\nadi.exe evaluate-hydraulics --config configs\canonical\evaluate_hydraulics.json --run-id hydraulic_review_001
.\.venv\Scripts\nadi.exe run-simulation --config configs\canonical\simulation_net3.json --run-id simulation_review_001
.\.venv\Scripts\nadi.exe audit --config configs\canonical\audit.json --run-id audit_review_001
.\.venv\Scripts\nadi.exe run-tests --config configs\canonical\run_tests.json --run-id tests_review_001
```

The former `nadi-legacy` / `python -m nadi.cli` route remains only for
historical reproduction and must not be used to create a new canonical claim.
The evidence-corrected manuscript is
`docs/canonical/NADI_Evidence_Corrected_Manuscript.md`, and the executable
review notebook is `notebooks/NADI_Canonical_Evidence_Notebook.ipynb`.

Location adaptation is implemented in `src/nadi/telemetry/normal.py`. It fits
causal robust local baselines with a global fallback for sparse or unseen
locations. See `docs/LOCATION_ADAPTATION_EVIDENCE.md`; this layer does not turn
physicochemical telemetry into direct E. coli detection.

The current locked simulated result is V5 (with V4 preserved as the corrected
historical benchmark). V3 is preserved as a superseded
historical result in `results/locked`. V5 is
not rerun by the ordinary reproduction script, preventing accidental
replacement of the frozen evaluation. Run `scripts/reproduce.ps1` to rebuild
the ordinary pipeline, tests, demonstration, and evidence report.

Raw resources remain in the sibling `nadi_resources` directory. `provenance/resource_manifest.json` freezes their paths and checksums.

Authentic-data replication additions: `scripts/download_ea_ecoli_authentic.py`
and `scripts/download_ea_ecoli_feature_panel.py` download official EA laboratory
observations; `scripts/train_ea_ecoli_authentic.py` and
`scripts/train_ea_physchem_panel.py` train leakage-safe real-data baselines.
Their outputs are recorded in `docs/AUTHENTIC_DATASET_REGISTRY.md` and the
reproducibility manifest. These tracks are surface-water evidence and do not
claim Delhi-NCR drinking-network validation. The Open E. coli model family is
also run as a controlled XGBoost adaptation on the authentic EA subset by
`scripts/replicate_open_ecoli_xgb_authentic_subset.py`; the full multi-agency
workflow remains explicitly marked as not bit-for-bit reproduced because its
external source tables are not bundled.
