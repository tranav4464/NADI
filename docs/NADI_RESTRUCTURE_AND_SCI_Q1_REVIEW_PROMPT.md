# NADI Repository Review and Research-Grade Restructuring Prompt

You are a senior research-software architect, applied mathematician, water-quality machine-learning researcher, scientific visualisation specialist, and rigorous SCI-Q1 peer reviewer.

You are reviewing the NADI project:

**NADI: Network Adaptive Decision Intelligence for Water Safety**

Repository:

`C:\Users\TRANAV\OneDrive\Desktop\STEM PROJECT\nadi`

Primary project dossier:

`C:\Users\TRANAV\OneDrive\Desktop\STEM PROJECT\nadi\dist\NADI_XYLEM_Project_Dossier_2026.docx`

The dossier presents a strong research concept, but the repository appears to be a multi-generation research workspace containing authentic experiments, historical benchmarks, hydraulic studies, simulated networks, transfer studies, telemetry experiments, dashboards, generated outputs, temporary files, and multiple entry points. Treat it as potentially Frankenstein-built until the code and evidence prove otherwise.

Your task is to inspect, reconcile, untangle, restructure, test, document, and improve the project without destroying useful work or overstating scientific claims.

Do not blindly rewrite the entire repository.
Do not assume the dossier is fully implemented.
Do not assume a result is valid because a report or JSON file exists.
Do not fabricate data, metrics, novelty, deployment, clinical safety, or contamination detection.
Do not silently delete files.
Do not overwrite frozen results.
Do not merge incompatible datasets merely to create a stronger story.
Do not present simulated hydraulic evidence as biological contamination validation.
Do not present surface-water E. coli risk as drinking-water pipe contamination detection.
Do not claim Delhi/Ghaziabad validation, illness reduction, regulatory safety, or direct sensor-based E. coli detection without evidence.
Do not guarantee SCI-Q1 publication or acceptance.

Use existing code and artifacts wherever they are correct. Refactor only after tracing behavior. Preserve historical evidence and negative results.

## Canonical scientific boundary

The current defensible NADI claim should be tested rather than assumed:

> NADI uses historical laboratory E. coli evidence and transparent decision mathematics to prioritize a limited confirmatory-testing budget. A separate hydraulic track estimates real-network pressure/state from sparse observations. The two tracks are not yet a unified, biologically validated contamination-to-pipe-response system.

Keep these evidence classes separate throughout the project:

- `LAB_CONFIRMED`: accepted microbiological observations from the original source
- `OBSERVED`: recorded weather, telemetry, pressure, flow, or operational data
- `MODEL_ESTIMATE`: calibrated predictions or reconstructed values
- `SIMULATED`: constructed network states, tracer events, or hidden benchmark truths
- `ASSUMED`: declared parameters used when direct evidence is unavailable
- `HISTORICAL`: superseded experiments or prior benchmark generations

# Phase 0 — Safe repository inventory

Inspect the complete repository before editing:

- Git history and working-tree status
- Tracked and untracked files
- `src/nadi` package structure
- `scripts`
- `configs`
- `data`, `data_raw`, `data_processed`, and `data_interim`
- `results`
- `logs`
- `provenance`
- `docs`
- `tests`
- `app`
- virtual environments
- `dist`
- temporary files such as `.bin`, `.inp`, and `.rpt`
- caches and generated files
- frozen V3/V4/V5 benchmark artifacts

Create an inventory containing:

- Path
- File type
- Size
- Git status
- Modification time
- Likely role
- Evidence track
- Current, historical, generated, temporary, or unknown status
- Safe-to-move status
- Safe-to-delete status
- Consumers and dependencies

Do not delete during this phase.

Deliver:

- `reports/phase_0_repository_inventory.md`
- `reports/phase_0_file_classification.csv`
- dependency graph
- list of blockers and unresolved ambiguities

# Phase 1 — Dossier-to-code reconciliation

Read the entire dossier and map every major claim to implementation and evidence.

Verify the provenance of these dossier claims where applicable:

- 13,405 authentic Environment Agency observations
- 920 monitoring sites
- 285 sampling dates
- 545 locked observations
- F1 0.838
- ROC-AUC 0.866
- PR-AUC 0.916
- sensitivity 0.966
- 114 high-E.-coli results in the top three across 41 rounds
- 84 under routine-frequency ordering
- 80 under deterministic-random ordering
- BWFLnet with 2,548 nodes and 2,606 links
- 0.278 m median internal-node error
- 66.3% improvement versus the declared baseline
- Net3 and L-TOWN simulated results
- unseen-site transfer results
- all comparator ties and negative findings

For each result record:

- Source artifact
- Generation command
- Dataset version
- Split or time period
- Metric definition
- Seed
- Whether frozen
- Whether modified later
- Authentic/simulated/reconstructed/assumed status
- Permitted interpretation
- Prohibited interpretation

Deliver:

- `reports/phase_1_dossier_code_reconciliation.md`
- claim-to-artifact matrix
- evidence-status matrix

# Phase 2 — Canonical system definition

Define one canonical NADI system:

```text
historical laboratory evidence
→ causal feature construction
→ calibrated risk models
→ model-family uncertainty
→ SDAIF fixed-budget optimization
→ ordered confirmatory-testing list
→ sequential update after revealed outcomes
→ auditable decision card
```

Keep supporting tracks separate:

```text
authentic microbial risk
real-network hydraulic validation
simulated hydraulic/source tracing
external transfer stress tests
telemetry/anomaly studies
dashboard/demo
```

Do not call the full project an end-to-end contamination detector unless a shared event-level dataset provides verified biological labels, timestamps, locations, network mapping, and operational state.

Deliver:

- `reports/canonical_architecture.md`
- `reports/evidence_track_boundaries.md`
- `reports/canonical_entry_points.md`

# Phase 3 — Code untangling and dependency audit

Trace each real execution path.

## Authentic microbial path

```text
official EA records
→ site-day consolidation
→ chronological causal features
→ model training
→ probability calibration
→ validation selection
→ locked test
→ site rounds
→ comparator policies
→ SDAIF
→ metrics and report
```

## Hydraulic path

```text
BWFLnet
→ network parsing
→ boundary/internal split
→ physical model
→ residual correction
→ validation
→ pressure metrics
```

## Simulation path

```text
EPANET/WNTR network
→ scenario generation
→ tracer propagation
→ source/localization analysis
→ placement policy
→ SDAIF stress test
```

For every module identify:

- public API
- inputs and outputs
- configuration
- random seeds
- file dependencies
- side effects
- hidden global state
- tests
- duplicate logic
- historical status
- downstream consumers

Find and resolve:

- duplicate feature construction
- duplicate calibration logic
- duplicate metric implementations
- multiple SDAIF implementations
- multiple “final” or “locked” result paths
- inconsistent endpoint thresholds
- inconsistent monitoring-round rules
- scripts that overwrite frozen outputs
- notebook-only behavior
- dashboard logic that bypasses canonical APIs
- generated artifacts committed as if they were source

Deliver:

- `reports/phase_3_dependency_graph.md`
- `reports/phase_3_code_ownership_matrix.csv`
- `reports/phase_3_duplicate_logic_report.md`

# Phase 4 — Clean repository structure

Create a migration plan toward:

```text
nadi/
  src/nadi/
    core/
    authentic/
    microbial_risk/
    decision/
    hydraulics/
    simulation/
    transfer/
    telemetry/
    reporting/
    provenance/
    dashboard/
  configs/
    canonical/
    historical/
    simulation/
    transfer/
  scripts/
    canonical/
    audit/
    acquisition/
    historical/
  data/
    raw/
    processed/
    manifests/
    external/
    simulated/
  results/
    canonical/
    historical/
    simulation/
    transfer/
    audit/
  docs/
    canonical/
    evidence/
    historical/
    competition/
  notebooks/
  reports/
  archive/
  tests/
```

Move files only after recording:

- original path
- destination path
- SHA-256
- reason
- affected imports
- affected commands
- rollback path

Preserve frozen outputs, historical reports, negative-result logs, and provenance manifests.

Deliver:

- `reports/migration_manifest.csv`
- `reports/phase_4_restructure_report.md`
- updated README
- updated entry-point documentation

# Phase 5 — Canonical CLI and reproducibility

Create one canonical CLI with commands such as:

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

Every command must:

- use explicit configuration
- write structured logs
- write a run manifest
- record source hashes
- record data hashes
- record config hashes
- record seed and version
- record output paths
- refuse to overwrite frozen results
- label evidence class

Historical scripts may remain archived but must not appear to be canonical.

# Phase 6 — Data integrity and leakage audit

Audit:

- chronological splitting
- same-date leakage
- site leakage
- duplicate site-day records
- replicate consolidation
- current-result contamination of features
- calibration leakage
- threshold selection
- validation/test contamination
- unseen-site transfer
- external overlap
- hydraulic train/validation reuse
- previously inspected validation periods

For monitoring rounds verify:

- candidates are known before selection
- outcomes are revealed only after selection
- all policies receive the same candidates and budget
- sequential updates use only revealed outcomes
- random baselines use many permutations
- oracle comparisons are defined consistently

Deliver:

`reports/phase_6_integrity_and_leakage_audit.md`

# Phase 7 — Tests and semantics

Test semantics, not merely file existence:

- data schema
- file hashes
- causal feature construction
- same-date isolation
- calibration
- threshold selection
- site-round generation
- budget constraints
- SDAIF regret
- Bayesian updates
- abstention
- hydraulic tensor shapes
- simulation labels
- evidence-class propagation
- claim-boundary enforcement
- frozen-result protection
- dashboard API contracts
- clean-environment reproduction

Deliver:

- updated tests
- clean test log
- `reports/phase_7_test_audit.md`
- reproduction log

# Phase 8 — Canonical results reconciliation

Build one performance matrix with separate sections for:

1. Authentic microbial classification
2. Authentic testing prioritization
3. Unseen-site transfer
4. BWFLnet pressure reconstruction
5. Net3 simulation
6. L-TOWN transfer stress
7. GECCO telemetry
8. Texas physical-network evidence
9. External prior-art adaptation

Every row must contain:

- evidence track
- dataset
- authentic/simulated/reconstructed status
- split
- sample count
- metric
- result
- baseline
- confidence interval
- randomization method
- artifact path
- command
- limitation

Preserve all ties and negative findings, including SDAIF comparator ties, unseen-site weakness, L-TOWN transfer weakness, high locked-period prevalence, low specificity, and random-comparator uncertainty.

Deliver:

`reports/canonical_performance_matrix.csv`

# Phase 9 — Research-quality executable notebook

Create:

`notebooks/NADI_executable_research_companion.ipynb`

The notebook must execute from the clean environment and contain these sections.

## 9.1 Research identity and scope

Show:

- title
- primary research question
- validated claim
- prohibited claims
- evidence-class legend
- version and artifact manifest

## 9.2 System architecture

Create a publication-quality pipeline figure:

```text
historical laboratory evidence
→ causal features
→ risk models
→ calibration
→ model disagreement
→ SDAIF
→ ordered confirmatory-testing list
→ revealed result
→ posterior update
→ decision card
```

Also show authentic, hydraulic, simulated, historical, and assumed tracks in a separate evidence map.

## 9.3 Authentic dataset visualizations

Generate as many meaningful figures as the data supports, including:

- observation timeline
- site distribution map
- monitoring-site count distribution
- E. coli prevalence over time
- positive/negative distribution
- region distribution
- sampling purpose distribution
- material distribution
- missingness heatmap
- duplicate/site-day consolidation diagram
- train/calibration/validation/test chronology

Do not expose sensitive precise coordinates in public outputs. Use aggregation or pseudonymous site IDs when required.

## 9.4 Causal feature and leakage visualizations

Show:

- feature-availability timeline
- historical-window construction
- current-result exclusion
- leakage-prevention flowchart
- feature-group matrix
- historical sample-count distribution
- days-since-previous-sample distribution

## 9.5 Risk-model visualizations

Show:

- model-family architecture
- feature importance with uncertainty caveats
- ROC curves
- precision-recall curves
- calibration curves
- reliability diagram
- Brier/calibration comparison
- threshold tradeoff
- confusion matrix
- per-class or endpoint metrics

## 9.6 Detection-style outputs

Use careful terminology. NADI estimates risk and prioritizes confirmatory testing; it does not directly detect E. coli from ordinary sensors.

Show:

- estimated high-risk site
- laboratory-confirmed high result
- missed high result
- false alarm
- testing priority
- abstention

Generate:

- estimated-versus-confirmed map
- true-positive/false-positive/missed-positive map
- threshold sensitivity plot
- precision-recall ranking curve
- top-k capture curve
- cumulative positives found as tests increase
- lift curve
- site-level error map

## 9.7 Geographic risk maps

For each site display where permitted:

- calibrated risk probability
- laboratory result when available
- historical positive rate
- model disagreement
- worst-case regret
- testing rank
- transfer-support flag
- abstention flag

Generate:

- geographic risk-probability map
- confirmatory-testing priority map
- observed laboratory-result map
- uncertainty overlay map
- model-disagreement map
- worst-case-regret map
- transfer-support map
- abstention map
- high-risk sites selected by each policy

Use a consistent legend:

- blue: low estimated risk
- yellow: moderate estimated risk
- red: high estimated risk
- black ring: selected for confirmatory testing
- hatched: weak transfer support
- grey: abstained or insufficient evidence

Every map must state whether it shows a model estimate, laboratory observation, simulated result, or assumption.

## 9.8 SDAIF mathematics and decisions

Show equations and visualizations for:

- candidate set
- fixed test budget
- loss
- regret
- expected regret
- worst-case regret
- robustness parameter
- mixed-integer plan
- sequential posterior update
- information-value proxy
- adversarial model
- abstention certificate

Generate:

- SDAIF optimization flowchart
- expected-versus-worst-case regret plot
- plan-space comparison
- posterior-weight evolution
- adversarial-model explanation
- certified-versus-abstaining decision diagram
- round-by-round decision timeline

## 9.9 Policy comparison

Compare:

- deterministic random
- routine frequency
- historical positive rate
- best single model
- fixed ensemble
- adaptive Bayesian
- adaptive SDAIF

Generate:

- ranked testing-list examples
- positives found within first k tests
- tests to first positive
- missed-positive-round rate
- positive-discovery regret
- paired policy differences
- bootstrap confidence intervals
- many-random-permutation distribution

## 9.10 Sequential risk-map updates

For at least one authentic monitoring round show:

1. initial risk map
2. initial selected sites
3. first revealed result
4. updated model weights
5. updated risk map
6. next selection
7. final three-test plan

Generate a multi-panel sequential decision figure.

## 9.11 BWFLnet real-network validation

Keep this separate from biological risk.

Show:

- network topology
- boundary sensors
- internal nodes
- physics prediction
- residual correction
- observed-versus-predicted pressure
- per-logger error
- error distribution
- interval coverage

Every figure must visibly state:

> Hydraulic state estimation only; not biological contamination localization.

## 9.12 Simulated source tracing

Keep Net3 and L-TOWN separate from authentic evidence.

Show:

- source assumptions
- tracer-affected nodes
- candidate source paths
- scenario overlap
- coverage@k
- transfer stress

Every figure must visibly state:

> Simulated network evidence; not field biological validation.

## 9.13 Dashboard and decision card

Show a professional decision card containing:

- ordered test list
- calibrated probability
- uncertainty
- worst-case regret
- adversarial model
- transfer support
- abstention reason
- evidence origin
- laboratory-confirmation status

## 9.14 Provenance and reproducibility

Show:

- Git commit
- dataset hashes
- configuration hashes
- result hashes
- random seeds
- environment manifest
- commands
- test status
- frozen-result protection
- claim-to-artifact traceability

The notebook must never silently retrain, alter a split, or select a result using locked-test labels.

# Phase 10 — Scientific contribution and novelty audit

Determine the narrowest defensible contribution.

Potential contributions may include:

- executable evidence-to-action architecture
- transparent fixed-budget testing prioritization
- explicit model uncertainty and regret
- abstention under transfer weakness
- authentic retrospective testing prioritization
- separate real-network hydraulic feasibility validation
- evidence-class and provenance separation

Do not claim:

- direct E. coli detection from ordinary sensors
- drinking-water contamination localization
- Delhi/Ghaziabad deployment validation
- illness reduction
- universal transfer
- unified biological-hydraulic validation
- superiority of SDAIF when the strongest comparator ties it
- novelty merely because familiar modules are combined

Deliver:

- `reports/phase_10_prior_art_and_novelty_audit.md`
- `reports/claim_to_evidence_matrix.csv`
- `reports/approved_claims.md`
- `reports/prohibited_claims.md`

# Phase 11 — Final manuscript

Write:

- title
- abstract
- introduction
- related work
- problem formulation
- evidence classes
- authentic microbial-risk method
- calibration
- SDAIF mathematics
- experimental protocol
- comparator policies
- authentic results
- hydraulic validation
- simulation and transfer stress tests
- robustness and abstention
- limitations
- safety and deployment boundaries
- reproducibility
- conclusion
- references
- supplementary audit tables

Rewrite the abstract last from measured results only.

# Phase reporting rules

After every phase, create a report containing:

- files inspected
- commands run
- changes made
- tests run
- results
- failures and fixes
- uncertainties
- evidence status
- remaining risks
- exact inputs for the next phase

Do not proceed to the next phase until the phase report exists and its acceptance checks pass.

# Final acceptance criteria

The project is complete only when:

- one canonical entry path exists
- historical work is clearly archived
- authentic and simulated evidence are separated
- frozen results cannot be overwritten accidentally
- data lineage is explicit
- semantic tests pass
- clean-environment reproduction works
- every performance claim maps to an artifact
- prohibited inferences are automatically audited
- the dashboard uses canonical APIs
- the notebook executes end-to-end
- risk maps distinguish estimates from observations
- hydraulic figures are not presented as biological detection
- the manuscript matches measured evidence
- no source, dataset, or result is deleted without a migration record
- a new researcher can understand the project without private conversation history

Final objective:

Transform NADI from a multi-generation research workspace into one coherent, auditable, reproducible, evidence-separated water-safety decision-intelligence project with a professional executable notebook, meaningful publication-quality figures, a narrow research contribution, and a complete evidence-based manuscript draft.

Maximize scientific quality through structure, tests, provenance, visualization, and reproducibility. Never maximize apparent performance by hiding uncertainty or changing the evidence boundary.
