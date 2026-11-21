# NADI — Xylem Application Draft (Authentic-Evidence Version)

## One-sentence solution

NADI is an applied-mathematical water-quality decision system that estimates location-specific E. coli risk from earlier authentic observations and decides which real monitoring locations should be tested first when testing capacity is limited.

## Problem and user

Water authorities collect laboratory samples, but cannot test every possible location at once. Serious contamination may remain unconfirmed while teams follow a fixed routine or choose sites without a quantified priority. NADI addresses the decision bottleneck: **given only information already available, where should the next limited tests begin to find severe contamination sooner?** The immediate user is a water-quality monitoring or sampling team.

## How NADI works

1. It turns each authentic site's earlier laboratory history, regional history, season and location into strictly past-only features.
2. Logistic regression, histogram gradient boosting and an XGBoost prior-art family produce calibrated probabilities.
3. SDAIF treats disagreement among those calibrated models as mathematical uncertainty. A mixed-integer optimisation balances posterior expected regret and worst-case regret to choose a test list under a fixed budget.
4. Within that robust list, the most informative result is requested first. Only after the actual historical laboratory outcome is revealed are model weights and the remaining list recomputed.
5. Real coordinates connect predicted high-risk monitoring sites into clearly labelled monitoring zones. These are not represented as pipe routes.

## Innovation

Most forecasting studies stop at a probability or colour-coded map. NADI continues from calibrated predictions to a constrained testing decision. It keeps model uncertainty visible, optimises an auditable operational objective, updates after each real result, and reports how it compares with random, routine, historical-risk, single-model and Bayesian policies.

## Authentic experiment

The experiment uses 13,405 authentic 2024 site-day records from the UK Environment Agency E. coli monitoring data, representing 920 sites and 285 sampling dates. No generated contamination label, generated laboratory result, or generated pipeline event is used. Features for every date are frozen before any result from that date updates history.

The chronology is fixed: training through 31 May; probability calibration from 1 June to 15 July; model and policy selection from 16 July to 30 September; and locked testing from 1 October onward.

## Locked result

On 545 untouched site-day records, the selected XGBoost model achieved F1 **0.838**, ROC-AUC **0.866**, PR-AUC **0.916**, sensitivity **0.966**, balanced accuracy **0.678**, and Brier score **0.141**. The always-positive comparator had F1 0.782 but balanced accuracy 0.500 and specificity 0.000, showing why F1 alone would be misleading.

Across 41 untouched authentic sampling rounds containing 5–25 simultaneously observed sites, with a budget of three tests:

- adaptive SDAIF found **114** confirmed high-E.-coli results;
- deterministic random testing found **80**;
- routine sampling-frequency priority found **84**;
- SDAIF missed no positive round; random and routine each missed 4.9%.

SDAIF equalled the strongest single-model, fixed-ensemble and adaptive-Bayesian policies on total positives found in this holdout. This supports non-inferiority to the strongest comparator, not superiority over it.

An explicit transfer stress test contained 50 records from 31 sites that had supplied no model-training labels. Performance fell to F1 0.722, ROC-AUC 0.705 and balanced accuracy 0.555. We therefore do not claim plug-and-play geographic transfer; local calibration remains necessary.

## Practical output

For each real monitoring date, NADI outputs calibrated risk, an ordered three-site test list, uncertainty across model families, the posterior/robust decision objective, the actual laboratory result revealed after selection, comparison with routine and random policies, and model-estimated monitoring zones based on authentic coordinates.

## Claim boundary

This experiment validates retrospective prioritisation in an authentic UK surface-water monitoring programme. It does **not** establish direct E. coli detection by ordinary sensors, drinking-water-pipeline tracing, a contaminated branch, Delhi-NCR performance, prospective deployment, or illness reduction.

## Scale pathway and ask

A prospective partner would provide its historical laboratory table and location metadata; NADI would retrain, calibrate locally, pass a transfer-support gate, and be evaluated against the partner's existing sampling order. We seek Xylem mentorship and access to a bounded prospective monitoring programme so the next experiment can measure whether a frozen NADI ranking finds independent laboratory positives sooner than routine sampling in live operation.
