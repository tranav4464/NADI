# NADI: An Evidence-Separated Decision System for Retrospective E. coli Test Prioritization and Water-Network Research

## Abstract

Water utilities have limited capacity to collect and analyze confirmatory
microbiological samples. NADI (Network-Adaptive Decision Intelligence for Water
Safety) is a reproducible decision system that prioritizes a fixed testing
budget while retaining the distinction between laboratory evidence, hydraulic
measurement, and simulation. Its primary experiment uses 13,405 UK Environment
Agency site-day E. coli observations collected in 2024 across mixed
environmental-water materials. A chronological model-training, calibration,
validation, and locked-test protocol selected a calibrated XGBoost model. On
545 locked observations, it obtained F1 0.838, ROC-AUC 0.866, PR-AUC 0.916,
sensitivity 0.966, and specificity 0.390 for a project-defined high-count
endpoint of at least 500 per 100 mL. Across 41 historical rounds with a
three-test budget, the SDAIF decision policy found 114 high results, compared
with 84 for routine-frequency selection and 80 for one deterministic random
ordering. A subsequent 2,000-permutation common-candidate random audit had a
mean of 82.62 high results and a 95% range of 75–90. SDAIF tied the best single-model and adaptive-Bayesian policies at
114; superiority is therefore not claimed. A separate BWFLnet study
reconstructed measured network pressure with median internal-logger MAE 0.278
m over 18,171 stored held-out predictions. A separate Net3 simulation reran
the V5 decision benchmark, where SDAIF tied adaptive Bayesian Coverage@3 at
0.615; L-TOWN stress testing was negative. NADI therefore demonstrates a
reproducible retrospective testing-prioritization architecture, not direct
sensor-based E. coli detection, drinking-water pipe localization, municipal
deployment, or avoided illness.

## 1. Introduction

Microbiological water safety decisions are difficult because the biological
endpoint normally arrives after sample collection and laboratory processing.
Testing every location is rarely feasible. The practical mathematical question
is not simply whether a classifier predicts a high result: given evidence that
was available before a testing round, which few locations should receive the
next confirmatory tests?

Water-quality ML, hydraulic modeling, and anomaly detection have often been
evaluated in different domains. A surface-water E. coli model cannot by itself
validate pipe-network pathogen movement. A pressure reconstruction does not
measure a microorganism. An EPANET tracer event is not a confirmed field
contamination event. NADI was designed around that distinction.

## 2. Related work

NADI builds on three established method families. First, environmental
microbiology studies use water-quality, weather, location, and historical
features to predict indicator-bacteria outcomes. Second, EPANET and WNTR make
hydraulic and water-quality scenario analysis possible in modeled distribution
networks. Third, robust and Bayesian sequential decision methods allocate a
limited test budget under uncertain outcomes. These antecedents mean NADI does
not claim invention of E. coli ML, network tracing, minimax regret, or Bayesian
updating.

Its contribution is an executable, provenance-controlled implementation that
keeps evidence classes separate, carries calibrated-model uncertainty into an
auditable testing decision, and explicitly retains ties and negative transfer
results. The exact close-method and evidence comparison is maintained in
`reports/phase_9_prior_art_and_novelty_audit.md`.

## 3. Problem formulation

Let a testing round have candidates \(V\), a test plan \(A \subseteq V\), a
fixed budget \(k\), model-specific probability estimates \(p_m(i)\), and
model weights \(w_m\). For the authentic replay, uncertainty is represented by
the finite set of calibrated model vertices. SDAIF selects a plan that combines
posterior expected value with worst-case regret. After a selected result is
revealed in the retrospective replay, model weights are updated and the next
test is recomputed.

For a simulated network scenario, a separate loss can combine a risk estimate,
affected set, consequence weights, and test cost. That formulation is evaluated
only on declared simulation scenarios. It is not merged row-wise with the EA
laboratory record.

## 4. Evidence classes

NADI uses four evidence labels:

- `LAB_CONFIRMED`: an E. coli laboratory outcome in its source dataset.
- `OBSERVED`: a recorded pressure, flow, weather, or telemetry input.
- `MODEL_ESTIMATE`: a classifier probability or pressure reconstruction.
- `SIMULATED`: an EPANET/WNTR event, tracer reach, or hidden benchmark truth.

An observed or simulated quantity cannot become laboratory truth merely because
it appears in a shared dashboard. The canonical CLI, manifests, dashboard, and
claim audit preserve these labels.

## 5. Authentic microbial-risk model

The primary dataset contains 14,069 raw EA records and 13,405 unique site-day
records after replication consolidation. It includes sea, river, estuarine,
surface-drainage, effluent, and other material types. The endpoint is a
project-defined indicator: reported E. coli at or above 500 per 100 mL. It is
not a drinking-water regulatory threshold.

For each date, site, regional, and global history features are constructed
before any outcome from that date updates history. Training ended 31 May 2024;
calibration used 1 June–15 July; validation used 16 July–30 September; the
locked period began 1 October. Logistic regression, XGBoost, and
histogram-gradient candidates were compared. The selected XGBoost model uses
past-only history, seasonal terms, coordinates, region, material, and sampling
purpose. The latter two fields are retained as an availability and selection
bias limitation.

## 6. Probability calibration

Each fitted estimator is calibrated with Platt scaling on the calibration
period. Thresholds are selected on that period only. The canonical workflow has
separate `train-risk`, `calibrate-risk`, and `evaluate-authentic` stages. The
locked evaluator verifies hashes of the raw-preparation and calibration
artifacts before running.

## 7. SDAIF mathematics

For authentic rounds, posterior model weights after observed selected outcomes
are proportional to prior model weight times the selected outcome likelihood.
SDAIF uses a mixed-integer plan to balance posterior expected capture and
worst-case regret over calibrated model vertices. It reports selected tests,
model disagreement, information value, posterior weights, adversarial model,
and worst-case regret.

The resulting certificate is conditional on its finite declared uncertainty
set. It is not a safety certificate, disease-risk estimate, or guarantee about
unmodeled contamination pathways.

## 8. Experimental protocol

The authentic test-prioritization replay includes only rounds with 5–25
observed candidates. Each policy receives the same candidates and budget of
three. Comparator policies include deterministic random ordering, routine
sampling frequency, historical positive rate, a best single model, fixed
ensemble, and adaptive Bayesian selection. The true same-round laboratory
outcome is revealed only after that location is selected in the replay. The
frozen deterministic-random order is retained for exact replay; a separate
2,000-permutation audit samples random selections from the same candidates in
every round without modifying the historical event table.

This timing is an analytical assumption. The EA data do not contain laboratory
result-release timestamps, so the replay cannot demonstrate that a culture
result would be available in time to alter a second same-round test in practice.

## 9. Comparator policies

The decision report is judged against routine and deterministic random ordering
for practical comparison, plus best-single-model and adaptive-Bayesian policies
for method comparison. The same record is used to identify the positive result
after selection for all policies. The 2,000-permutation audit quantifies the
random-policy distribution; it does not establish superiority over the tied
best-single or adaptive-Bayesian comparators.

## 10. Authentic results

On the 545-row locked period, the selected XGBoost model has F1 0.838,
ROC-AUC 0.866, PR-AUC 0.916, sensitivity 0.966, precision 0.740, and
specificity 0.390. The high prevalence of 0.642 and low specificity are
material limitations.

Across 41 eligible rounds, SDAIF found 114 high results within three tests,
compared with 84 under routine-frequency order and 80 under deterministic
random order. Best-single-model, fixed-ensemble, adaptive-Bayesian, and SDAIF
all found 114. Thus the appropriate conclusion is that SDAIF achieved the same
top yield while exposing robust-decision information; it did not outperform the
strongest model-based comparators in this replay.

## 11. Hydraulic validation

BWFLnet is a separate published drinking-water hydraulic network with 2,548
nodes and 2,606 links. A hybrid pressure-state estimator was assessed on 18,171
stored predictions at 27 internal pressure loggers over 673 timestamps. Median
per-logger MAE is 0.278 m; aggregate MAE is 0.415 m. The declared training-mean
baseline has median MAE 0.827 m, giving a 66.3% relative median-MAE improvement.

This is a pressure reconstruction result. It contains no paired E. coli label,
and its validation week was previously inspected in development. It cannot
validate microbial intrusion, a contamination source, or an affected pipe
branch.

## 12. Simulation and transfer stress tests

The canonical Net3 V5 simulation uses 120 declared events, 76 of which have a
nonempty affected candidate set. SDAIF and adaptive Bayesian both achieve
Coverage@3 0.615, with a paired bootstrap difference of zero. L-TOWN stress
testing has four nonempty hidden cases, where SDAIF reaches 0.257 and
hydraulic/adaptive Bayesian reaches 0.359. These simulation results are useful
for limiting claims: robust selection is not automatically superior under a
shifted network/scenario ensemble.

In an EA unseen-site physicochemical holdout, F1 is 0.737 on 140 records; the
authentic model's internal unseen-site subgroup has F1 0.722 and ROC-AUC 0.705.
Neither estimates city-to-city, drinking-water, or Delhi-NCR transfer.

## 13. Robustness and abstention

NADI has explicit no-support and incompatible-evidence abstention paths.
These are appropriate when an uncertain domain shift, sensor anomaly, or
unrepresented source makes the finite model set unreliable. The dashboard and
API should show an abstention reason rather than convert absent evidence into a
confident alert.

## 14. Limitations

The central limitation is the absence of a shared event-level dataset linking a
verified drinking-water network location/time, operational state, sensor stream,
and independent microbiological result. Current-sample sampling purpose may
encode reactive sampling. Candidate sets are reconstructed from already
observed agency samples. Result availability time is unknown. The hydraulic
validation is not a pristine final holdout. Net3 and L-TOWN are simulated.

These constraints prohibit direct E. coli detection, real pipe localization,
prospective exposure reduction, and municipal deployment claims.

## 15. Safety and deployment boundaries

NADI is research decision support. A real response would require a qualified
laboratory, an approved sampling protocol, utility operator review, validated
network data, and public-health governance. The system must not automatically
isolate, flush, advise the public, or substitute a risk score for a
microbiological result.

## 16. Reproducibility

The canonical `nadi` CLI requires explicit configuration and a unique run ID.
It includes preparation, input verification, model training, calibration,
authentic evaluation, SDAIF reconciliation, hydraulic evaluation, simulation,
reporting, manifest building, auditing, and tests. Each canonical artifact
records SHA-256 hashes for its inputs, configuration, source, and outputs.
Historical results remain indexed and retained rather than deleted.

## 17. Conclusion

NADI provides an auditable way to convert historical laboratory risk evidence
into a limited confirmatory-testing order. It also demonstrates that a
measurement-based hydraulic reconstruction and a simulated network-decision
benchmark can be retained as separate research tracks without overstating what
they prove. The strongest current conclusion is a reproducible retrospective
E. coli testing-prioritization result, with transparent ties, transfer limits,
and evidence boundaries.

## 18. References

1. Environment Agency. Water-quality monitoring records, determinand 2348,
   2024. Exact downloaded-file identity is recorded in the NADI preparation
   manifest.
2. Waldron, R., Pecci, F., and Stoianov, I. BWFLnet network and data. Mendeley
   Data, DOI: 10.17632/srt4vr5k38.3.
3. Rossman, L. A. *EPANET 2 Users Manual*. U.S. Environmental Protection
   Agency, EPA/600/R-00/057.
4. Klise, K. A., et al. Water Network Tool for Resilience (WNTR) user and
   developer documentation. Sandia National Laboratories / U.S. EPA ecosystem.
5. Cognizant Research. *Open E. coli Models* repository, bounded adaptation
   recorded in `results/open_ecoli_prior_art_adaptation_v1.json`.
6. NADI canonical artifacts, performance matrix, integrity audit, and claim
   matrix in this repository.

## 19. Supplementary audit tables

- `reports/canonical_performance_matrix.csv`
- `reports/claim_to_evidence_matrix.csv`
- `reports/phase_6_integrity_and_leakage_audit.md`
- `reports/phase_9_prior_art_and_novelty_audit.md`
- `reports/migration_manifest.csv`
