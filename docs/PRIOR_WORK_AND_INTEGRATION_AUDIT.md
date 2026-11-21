# NADI prior-work and methodology integration audit

**Purpose.** This document reviews the datasets and prior methods currently available in the NADI workspace and defines how they can be connected without treating incompatible observations as one training table. It is the integration plan for the CBSE and Xylem software-first submissions.

## 1. What the project is actually trying to do

NADI has four distinct outputs:

1. estimate current faecal-risk evidence (`nowcast`);
2. estimate near-future risk (`forecast`);
3. estimate where a contaminated or suspicious parcel could travel (`affected-region`);
4. choose the limited tests/actions with the greatest expected decision value (`SDAIF`).

The outputs require different evidence. A weather/E. coli model cannot locate a parcel in a pipe network; a hydraulic tracer cannot prove E. coli; an industrial telemetry anomaly is not a biological label. The correct design is therefore a **federated evidence architecture**, not one giant model trained on unrelated rows.

## 2. Dataset audit

| Resource | What it contains | Legitimate use | Do not claim |
|---|---|---|---|
| Marion WQP + NOAA Indianapolis | 6,000-ish surface-water observations, laboratory E. coli, weather | Reconstruct ISEF-style nowcast/forecast; compare model families and calibration | Delhi drinking-water or pipe-level E. coli |
| Bangladesh MICS replication data | 6,069 household records with separate source (`WQ27`) and household (`WQ26`) E. coli fields | Transfer stress-test and endpoint-definition audit | Pipe-network localisation; combine source and household labels |
| People’s Water Data Chennai paper | Indian household point-of-use E. coli study (3,023 collected; 2,207 retained in the report) | Scientific analogue for Indian drinking-water endpoint and sampling/QC design | Raw sample-level table/code is not in the current workspace; cannot be used as a local training table |
| GECCO 2017–2019 | High-frequency industrial water-quality telemetry (`pH`, conductivity, turbidity, SAC, PFM, temperature) and event labels | Reproduce anomaly/event detection and feature engineering | E. coli detection or drinking-water safety |
| Bristol POU telemetry | 2019–2022 operational membrane/point-of-use telemetry: flow, pressure, TMP, ORP, FAC, flux | Operational sensor drift, regime and fault features | Microbial truth |
| WDSEventDB | Clean, leakage, cyberattack and sensor-failure testbed events | Robust telemetry ingestion, fault rejection and missingness tests | Biological contamination |
| BattLeDIM L-TOWN | EPANET network, SCADA pressures/flows/levels, leakage scenarios | Hydraulic calibration-style exercises, anomaly and transfer tests | Real Delhi/Ghaziabad network |
| EPANET/WNTR + Net3 | Hydraulic and tracer simulation | Travel-time, source-trace, affected-zone ensembles | Empirical contamination evidence |
| L-TOWN second network | 782 junctions, 905 pipes; independent topology from Net3 | Out-of-network transfer and source-localisation stress test | Universal hydraulic performance |
| ISEF/Open E. coli Models methods | Weather feature windows, model-family comparison, ETL and validation patterns | Replication and fair baselines | Exact bit-for-bit reproduction when source code/splits are unavailable |

The frozen provenance manifest records hashes, domains, allowed inferences and prohibited inferences. It must remain the authority for every dataset join.

## 3. Methodology review and what is reused

### Biological-risk forecasting

The ISEF-style pipeline supplies lagged precipitation/temperature features, seasonal terms, chronological splitting and model-family comparison. NADI now implements validation-only selection among logistic regression, random forest, ExtraTrees, decision tree, gradient boosting and XGBoost, followed by probability calibration and an uncertainty radius. The current Marion test result is approximately 0.689 nowcast accuracy/F1 0.470 and 0.598 forecast accuracy/F1 0.439; it is a real result, not a failure to hide.

The Open E. coli Models repository contributes reproducible ETL, validation and provenance patterns. Its recreational/surface-water target remains a separate domain.

### Household-water transfer

Bangladesh data are valuable because they demonstrate an Indian-region household-water endpoint. The audit found that the stored `e_coli` variable follows source-water `WQ27`, while household water is `WQ26`; 2,904 valid rows differ. NADI therefore keeps both endpoints and reports transfer stress separately. The high household positive-class F1 is dominated by prevalence and does not establish discrimination; an always-positive baseline is mandatory.

### Telemetry and anomaly evidence

GECCO methods provide robust distance, isolation forest and supervised event classifiers. The best current test result has high ROC-AUC but only about 0.483 positive F1, while the always-negative accuracy is already about 0.994. This proves why accuracy alone is unsafe. GECCO and Bristol outputs enter NADI as **proxy anomaly evidence** with domain labels, not as E. coli labels.

Bristol telemetry has now been audited separately: 209,584 five-minute
operational records were chronologically partitioned, missingness and cadence
were measured, and unsupervised robust-distance/Isolation-Forest scores were
generated. Because the resource has no independent event or microbiology labels,
it contributes proxy operational evidence only and no accuracy/F1 claim.

WDSEventDB adds a missing operational control: the system must distinguish contamination-like changes from sensor failure, leakage, cyberattack or missing packets before increasing risk.

### Hydraulic and network methods

EPANET/WNTR supply the conservation/transport layer: pressure-dependent demand, tank state, source tracing, water age and conservative-tracer travel. Net3 and L-TOWN supply distinct topologies. NADI generates ensembles over source, demand, tank and valve scenarios, then carries their reachable-region uncertainty into SDAIF. L-TOWN and unseen-source tests are intentionally retained as negative evidence: they prevent the system from claiming exact source identification when the true source is outside the enumerated hypotheses.

### SDAIF decision mathematics

SDAIF consumes calibrated risk intervals and hydraulic scenario sets, then selects tests/actions by consequence-weighted minimax regret. Its adaptive value-of-information step chooses the next test only after the previous test is selected and only uses its result after that decision. Delayed evidence, pending tests, domain abstention and finite-set certificates are implemented and tested. V5 shows equivalence to adaptive Bayesian on the simulated decision task, not superiority.

## 4. The integration architecture

Every evidence stream is converted to a common record:

`{domain, endpoint, location/time, probability_or_score, interval, support, provenance, latency, reliability}`.

The pipeline is:

```text
Marion/NOAA ───────┐
Bangladesh ────────┤  calibrated biological/context evidence
GECCO/Bristol/WDS ─┤  anomaly and sensor-health evidence
                    ├─> transfer/support gate ─> uncertainty set Q
EPANET/WNTR/Net3 ──┤  possible movement and affected-zone scenarios
L-TOWN ─────────────┘

Q + population/consequence weights + test budget
        └─> SDAIF robust regret / VOI policy
                └─> ranked tests, affected-region probabilities, abstention reason
```

No row-level join is created between Marion E. coli, GECCO telemetry, Bangladesh labels and EPANET scenarios. They are connected only through typed evidence objects and a declared transfer rule. This is the central integrity requirement.

## 5. How to pursue the 91% request correctly

The project cannot honestly promise 91% E. coli accuracy/F1 from the current public data. The biological track has different domains and the Marion endpoint currently does not reach that threshold. The correct performance programme is:

1. lock the biological endpoint and positive definition before tuning;
2. use chronological and site/event-held-out splits;
3. compare all prior families plus weather-only, anomaly-only, household-transfer and calibrated ensemble baselines;
4. tune thresholds only on validation data;
5. report positive F1, sensitivity, specificity, precision, PR-AUC, calibration and false negatives, not accuracy alone;
6. reserve a final untouched test set;
7. separately target high performance on the operational event/anomaly track only if its endpoint and class balance justify it;
8. use SDAIF decision utility—not classifier accuracy—as the final system metric.

If a future local labelled dataset produces ≥91% on an untouched, independent endpoint, NADI may report it. If not, the submission must report the measured value and use the stronger claim: **NADI remains decision-valid under uncertainty and knows when to abstain.**

## 6. Work sequence to complete the integrated system

### Stage A — freeze and audit

- Freeze provenance hashes, endpoint definitions, split IDs and policy configs.
- Add dataset cards for every resource above.
- Re-run the ISEF reconstruction, Bangladesh endpoint audit, GECCO evaluation and all hydraulic benchmarks from a clean environment.

### Stage B — component models

- Keep the calibrated Marion nowcast/forecast heads.
- Add a documented Bangladesh transfer head with local-normal and support diagnostics.
- Add GECCO/Bristol/WDS sensor-health/anomaly heads.
- Add an explicit unknown-event and sensor-failure rejection layer.

### Stage C — uncertainty fusion

- Convert each component output into an interval plus support score.
- Inflate uncertainty under covariate shift, missingness, latency or endpoint mismatch.
- Abstain rather than convert an unsupported proxy into an E. coli claim.

### Stage D — network consequences

- Generate Net3 and L-TOWN scenario ensembles.
- Add alternate source/valve/demand/tank states and travel-time intervals.
- Calculate affected-zone probabilities and population-weighted consequences.
- Mark exact-source results as conditional; retain unknown-source rejection.

### Stage E — SDAIF decision layer

- Run random, routine, weather-only, anomaly-only, hydraulic-only, Bayesian, inverse-probability, robust and adaptive SDAIF baselines.
- Evaluate tests-to-first-positive, time-to-confirmation, missed positives, regret, cost and population-weighted exposure avoided.
- Include delayed laboratory evidence and pending tests in the decision timeline.

### Stage F — final evidence package

- Produce one dashboard card separating observed, model-estimated and simulated values.
- Show model selection table, calibration plot, shift/abstention result, affected-region map, adversarial scenario and action ranking.
- Present V5 equivalence and every negative result; do not call simulated reach biological validation.

## 7. The resulting Xylem/CBSE claim

> **NADI is a software-first mathematical decision system that combines separately validated microbial-risk, operational-anomaly and hydraulic evidence, propagates their uncertainty and delay into a robust action problem, and tells a water utility which locations to test or protect first—or when the evidence is insufficient to make that claim.**

This is stronger and more defensible than claiming a universal E. coli detector. It makes SDAIF the core: prior ML methods provide evidence; network models provide possible consequences; SDAIF converts both into a constrained, auditable decision.
