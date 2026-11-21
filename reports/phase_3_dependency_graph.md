# Phase 3 dependency graph — working audit

This is a source-traced graph, not a claim that all workflows are canonical. No code or result was moved during this phase.

## Authentic EA path

`../nadi_resources/datasets/EA_ECOLI_AUTHENTIC/ea_ecoli_confirmed_mf_2024.csv` -> `scripts/build_authentic_site_rounds.py` -> `nadi.authentic.site_rounds.build_site_day_table` -> `data_processed/ea_authentic_site_rounds_2024.csv` and `results/ea_authentic_site_rounds_2024.json` -> `scripts/run_authentic_xylem_experiment.py` -> `nadi.authentic.models.model_family` (three classifiers; train seed 2026; Platt calibration) -> validation-only threshold/model/robustness selection -> `nadi.authentic.benchmark.evaluate_authentic_rounds` -> `nadi.authentic.policy.authentic_sdaif_sequence` -> report, site predictions, events and policy summary in `results/authentic_locked`. This path was reproduced into `results/audit/authentic_reproduction_20261120`, yielding byte-identical files.

The site-day builder updates history after each complete date, but it writes to fixed output paths. The model uses current-record `sampling_purpose` and `material`, whose predecision availability is not established. The experiment output path is configurable, but defaults to an overwriteable directory named `authentic_locked`. The one “random” comparator is a fixed SHA-256 sort, not a distribution over random permutations.

## BWFLnet observed-pressure path

`data/external/bwflnet/{data.zip,BWFLnet.inp,link_properties.csv}` -> `scripts/train_bwflnet_full_hybrid.py` -> WNTR/EPANET physics variants, boundary features and training-only model selection -> heldout prediction rows, per-logger metrics, model joblib and report in `results/bwflnet_full_hybrid`. Stored predictions have 18,171 internal pressure rows across 673 timestamps; independently recomputed median logger MAE .27821578 m. This path predicts hydraulic state, not contaminant transport. The fixed output directory and earlier validation-week inspection require preservation and disclosure.

## Simulated path

Public Net3 or L-TOWN network -> `nadi.hydraulics.generate`/ensemble and source tracing -> generated scenario reach and policy testing through `nadi.evaluation.benchmark`, `nadi.sdaif.engine` and versioned runner scripts -> `results/locked/benchmark_v1..v5` or L-TOWN stress JSON. V5 Net3 is a corrected 120-event simulation with a tie; L-TOWN stress has worse SDAIF coverage than hydraulic/Bayesian ranking. No biological observation is joined to these events.

## Dashboard consumers and bypass risk

`app/server.py:/api/authentic-xylem` reads four files directly from `results/authentic_locked`, derives candidate rounds, calls `authentic_sdaif_sequence`, checks its selected list against the stored event row, and returns a JSON replay. This is a useful equality check, but the route bypasses a packaged canonical artifact/API and does not verify source hashes or evidence availability time. It includes `laboratory_high_500` for every candidate in its response before any simulated sequential reveal. Thus the server/client protocol is an **unblinded retrospective replay**, even if the UI progressively reveals results. Do not describe the API as blind at request time. `/api/latest`, `/api/benchmark` and `/api/demo` remain separate legacy/simulated routes.

## Simulation runner ancestry and generated reporting

The L-TOWN ensemble is created by `scripts/generate_ltown_ensemble.py` from a named `.inp` file through `hydraulics.generate._simulate`. `scripts/out_of_ensemble_benchmark.py --config configs/ltown_decision_stress_v1.json --output <fresh>` loads that ensemble, simulates four hidden cases, calls `AdaptiveSDAIF`, delayed testing and policy baselines, then writes the stress JSON. Its defaults point instead to Net3 V1; an omitted explicit config would run a different study. `src/nadi/evaluation/benchmark.py` is the V1–V5 Net3 benchmark runner called by `nadi benchmark` and reads Marion weather, a risk bundle and simulated reference ensemble.

`src/nadi/reporting/evidence.py` chooses V5 if its summary exists and otherwise silently falls back to V4. Its figure title still says “Locked V4” even for a V5 figure, and its prose describes “network locations” in a composite chain whose risk and reach sources are not paired. This report generator should not be the canonical Xylem evidence source without an explicit evidence-class and version repair. No notebook files (`*.ipynb`) were found outside the virtual environments; notebook-only behavior is not present in this checkout.

## Inspection status

Public APIs, side effects, principal file dependencies, duplicate implementations and runner ancestry are recorded here and in the ownership matrix and duplicate-logic report. Dynamic imports and every possible file consumer cannot be proven absent by static inspection; migrations must therefore preserve old files and run import, dashboard and reproduction checks. Phase 3 is a completed ownership audit with these explicit limits, not proof that every source module is reachable or that current result reporting is correct.
