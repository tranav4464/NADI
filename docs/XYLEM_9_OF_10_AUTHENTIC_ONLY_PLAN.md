# NADI Xylem 9/10 Authentic-Only Plan

## Governing rule

The Xylem submission will use only authentic observed measurements and laboratory results for every scored performance claim. No simulated or synthetic contamination event, label, pipeline, affected region, exposure reduction or laboratory outcome will be used as validation evidence.

## Consequence of this rule

The current public resources do not contain time-matched drinking-water E. coli, pipe-network topology, operating state and downstream laboratory outcomes. Therefore the authentic-only submission cannot claim that it traces contamination through a municipal pipe, identifies a contaminated branch or validates affected-household predictions.

The scored Xylem project will instead solve a closely related decision bottleneck that can be tested entirely with real observations:

> When a water-monitoring authority has more possible locations than it can test immediately, which real locations should be sampled or processed first to find serious E. coli contamination with the smallest testing budget?

## Final authentic-only claim

> NADI is an applied-mathematical water-quality decision system that learns from authentic laboratory E. coli observations, weather, physicochemical measurements, location and sampling history. It produces calibrated location-specific risk, identifies observed high-risk spatial zones and prioritises the next real monitoring locations under a limited testing budget. Its performance is evaluated retrospectively on untouched authentic laboratory results.

## Evidence separation

- `LAB_CONFIRMED`: authentic E. coli result from the source laboratory dataset.
- `OBSERVED`: authentic date, coordinate, weather or physicochemical observation.
- `MODEL_ESTIMATE`: prediction or uncertainty calculated from past authentic observations.
- `SIMULATED`: prohibited from the Xylem scored results and headline demonstration.

Hydraulic simulation may remain in the historical repository but must not appear in the Xylem performance claim, primary dashboard or headline figures.

---

# Phase 0 — Freeze endpoint and decision unit

## Endpoint candidates

Evaluate authentic, domain-appropriate endpoints separately:

1. laboratory E. coli detection;
2. E. coli at or above 500 CFU/100 mL as a surface/recreational-water severity endpoint;
3. count regression or ordered severity bands where reporting quality supports it.

Do not call the 500-CFU endpoint a drinking-water safety standard.

## Decision unit

Build authentic sampling rounds from actual collection records. A round may be a day or a prespecified short window only when multiple real locations have independent laboratory results. Each candidate in a round must have an authentic hidden outcome.

## Primary operational question

With a budget of `k` tests among the authentically observed candidates in a round, how many confirmed high-E. coli locations are found and how quickly is the first confirmed positive found?

## Exit gate

Freeze endpoint, round definition, information cutoff, budget, splits, policies and metrics before the untouched test is evaluated.

---

# Phase 1 — Construct the authentic longitudinal site table

## Inputs

- EA authentic E. coli laboratory records;
- authentic sample coordinates and site identifiers;
- authentic collection date/time;
- sample-matched pH, temperature and conductivity where available;
- observed weather joined by location and date;
- past laboratory history available before each decision time.

## Required features

- past-only site prevalence;
- days since previous sample;
- previous E. coli count/result;
- rolling site and regional history;
- season and past weather;
- available field physicochemistry;
- distance to previously observed high-result locations;
- missingness and measurement-availability indicators.

No future or same-result laboratory information may enter the prediction.

## Selection-bias warning

Public monitoring sites were not sampled randomly. Preserve sampling programme, site and reason fields where available. Restrict conclusions to the observed monitoring programme and test inverse-probability or sensitivity corrections where defensible.

## Exit gate

Every row has immutable site, time, endpoint, feature cutoff, provenance and split identifiers. Leakage tests prove that all features existed before the target result.

---

# Phase 2 — Authentic location-specific risk model

## Baselines

- always-positive/majority;
- last-observation-carried-forward;
- site historical prevalence;
- seasonal logistic regression;
- current authentic HGB/XGBoost models.

## Strong candidates

- calibrated gradient boosting;
- hierarchical site/region model;
- graph-regularised risk model using authentic spatial coordinates;
- conformal or bootstrap uncertainty intervals;
- ensemble only if it improves untouched decision metrics.

## Required validation

- chronological holdout;
- unseen-site holdout;
- combined future-time and unseen-site holdout;
- repeated grouped validation;
- seasonal stress test;
- calibration and abstention under shift.

## Required metrics

- sensitivity, specificity, precision and NPV;
- F1, balanced accuracy and MCC;
- ROC-AUC and PR-AUC;
- Brier score and calibration error;
- confidence intervals;
- improvement over trivial baselines.

The current 0.934 F1 result cannot be used as a headline because an always-positive rule is approximately 0.930 at that prevalence.

## Exit gate

Choose the simplest model that improves the authentic decision outcome, not the model with the most flattering in-domain F1.

---

# Phase 3 — Authentic spatial-zone estimation

## Purpose

Replace simulated pipeline affected regions with authentic observed monitoring zones.

## Method

- construct a spatial graph from real monitoring-site coordinates;
- connect sites using prespecified distance or watershed-aware rules where authentic catchment information exists;
- estimate a calibrated risk surface or graph-smoothed risk using past data only;
- identify connected high-risk monitoring zones;
- quantify uncertainty and abstain where spatial support is weak.

## Claim boundary

These are high-risk monitoring zones, not water-distribution branches and not proof that contamination physically travelled between sites.

## Exit gate

Zone predictions are evaluated against later authentic laboratory observations at held-out sites and dates.

---

# Phase 4 — Authentic SDAIF testing policy

## State

For each authentic round, NADI receives only information available before the laboratory outcomes in that round. Laboratory outcomes remain hidden until a policy selects the corresponding real location.

## Decision loss

Use a consequence-weighted testing loss:

\[
L(A,y)=\sum_{i:y_i=1,\ i\notin A}w_i+c|A|,
\]

with sensitivity analysis for consequence weights. If population or vulnerability is unavailable, use uniform weights and do not invent values.

## Policies

Compare under identical authentic rounds:

1. random;
2. routine/fixed-site;
3. last-result priority;
4. risk-only;
5. uncertainty-only;
6. Bayesian expected-utility;
7. static robust;
8. adaptive SDAIF.

Adaptive policies may reveal a result only after selecting that authentic location. Result time must not be fabricated; the central metric is test order unless authentic result timestamps exist.

## Primary metrics

- positives found within first `k` tests;
- fraction of observed positives found in first `k`;
- tests to first positive;
- missed-positive rounds;
- cost per confirmed positive using declared test-cost scenarios;
- worst-case regret;
- abstention rate and error.

## Exit gate

SDAIF must be non-inferior to the strongest comparator on average and demonstrate a clear advantage in worst-case loss, uncertainty-aware abstention or evidence efficiency. Otherwise retain the strongest simpler method.

---

# Phase 5 — Locked real-data experiment

## Splits

- Development: earlier dates/sites used for feature development.
- Validation: later grouped rounds used for model and threshold selection.
- Locked test: untouched latest rounds and/or held-out geographic groups.

All samples from the same site-date/round remain in the same partition.

## Statistics

- event/round-level paired bootstrap confidence intervals;
- prespecified non-inferiority margin;
- effect sizes;
- separate results by prevalence, season and geographic support;
- no tuning on locked outcomes.

## Exit gate

Publish the locked result whether positive or negative. Do not replace the endpoint after seeing it.

---

# Phase 6 — Authentic-only dashboard

The main screen must show:

1. date and authentic source dataset;
2. real monitoring locations on a map;
3. calibrated location-specific risk;
4. uncertainty/support;
5. ordered first tests;
6. revealed authentic laboratory result after selection;
7. comparison with routine/random policy;
8. cumulative positives found and tests used;
9. explicit statement that this is retrospective evaluation on authentic monitoring records.

Do not show simulated pipelines, simulated affected populations or assumed protective actions in the scored demonstration.

---

# Phase 7 — Practical outcome

The demonstrated outcome is:

> For authentic historical monitoring rounds, NADI determines which observed locations should have been tested first and measures whether the ordered list found laboratory-confirmed high-E. coli locations using fewer tests than routine alternatives.

The future deployment pathway is prospective monitoring support. It is not presented as completed municipal deployment.

---

# Phase 8 — Submission and scrutiny

- freeze repository, data hashes, splits and model versions;
- remove simulated results from the primary evidence pack;
- reproduce in a clean environment;
- obtain independent review of endpoint, sampling-round construction and mathematics;
- verify Xylem rules and AI-disclosure requirements;
- create a two-minute pitch centred on the authentic decision result;
- ensure every number links to a real laboratory record or derived model output.

---

# Immediate work order

- [x] Audit the 14,069-record authentic EA table for counts, sites, dates and multi-site sampling rounds.
- [x] Define authentic endpoints and trivial baselines.
- [x] Construct past-only longitudinal features.
- [x] Create development, validation and untouched grouped test partitions.
- [x] Train calibrated location-specific baselines.
- [x] Build authentic round-based policy evaluation.
- [x] Adapt SDAIF to real revealed laboratory outcomes.
- [x] Compare policies with paired confidence intervals.
- [x] Build an authentic-only map and sequential-result demonstration.
- [x] Rewrite the evidence pack, pitch and application around the locked authentic result.

The software work order is complete. External prospective validation, independent review and target-location data remain future evidence requirements and are not represented as completed work.

# Hard stops

- no synthetic labels;
- no simulated contamination event in scored results;
- no pipeline or affected-household claim without real paired evidence;
- no invented laboratory delay, population, cost or operating state;
- no use of future results in features;
- no headline accuracy/F1 without prevalence and trivial baselines;
- no claim of exposure or illness reduction.
