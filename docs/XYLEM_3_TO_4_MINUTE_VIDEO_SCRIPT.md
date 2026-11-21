# NADI Xylem 3–4 minute presentation and demo script

## 0:00–0:25 — Introduction

Hello, we are competing in the high-school Water Quality Challenge. Our project is NADI, an applied-mathematical system that helps a water-monitoring team decide where limited confirmatory E. coli testing should begin.

E. coli cannot be confirmed by sight, smell, or ordinary water-quality sensors. Authorities therefore depend on laboratory testing, but they cannot collect and process every possible sample at the same time. Our question is simple: if only three tests are available now, which locations should be checked first?

## 0:25–1:05 — Authentic evidence

NADI uses earlier laboratory history for each monitoring site, regional history, season, and real coordinates. We tested logistic regression, histogram gradient boosting, and XGBoost. Each model produces a calibrated risk estimate.

We used 14,069 authentic Environment Agency laboratory observations. After combining same-site results from the same date, we obtained 13,405 site-day records from 920 sites. Every feature for a date was frozen before any result from that date updated the history. We separated training, probability calibration, model selection, and the final locked test chronologically.

No generated contamination label, generated laboratory outcome, pipe event, or affected population enters our scored experiment.

## 1:05–1:50 — Applied mathematics

The three calibrated models do not always agree. SDAIF converts that disagreement into a decision.

For each model, we define missed-risk loss as the total predicted E. coli risk at locations that we do not select. We then calculate regret: how much worse our selected list is than the best list for that model.

Our mixed-integer programme chooses three locations by balancing two quantities. The first is posterior average regret, using model weights learned from validation log loss. The second is the maximum regret across the credible models. A robustness parameter controls this balance and was selected before the locked test.

Within the robust list, NADI tests the location that provides the most information about model disagreement. After its authentic laboratory result is revealed, Bayes' rule updates the model weights and NADI recalculates the remaining list.

## 1:50–2:35 — Live demonstration

On the dashboard, I first choose an authentic sampling date. The red numbered points show NADI's frozen test order on real monitoring coordinates. Blue intensity shows predicted risk, and the table reports disagreement among the calibrated models.

The laboratory outcomes begin hidden. I click “Reveal authentic laboratory outcomes” only after the test order is visible. The screen then shows which selected sites actually had results at or above our declared 500 endpoint.

The map shows monitoring locations. It does not claim a pipeline route or prove that contamination travelled between sites.

## 2:35–3:15 — Locked results

On 545 untouched site-day records, XGBoost achieved F1 0.838, ROC-AUC 0.866, PR-AUC 0.916, and balanced accuracy 0.678. We also reported the always-positive comparator because F1 alone can mislead when positives are common.

Across 41 authentic sampling rounds, every policy received the same information and a budget of three tests. Deterministic random testing found 80 confirmed high results. Routine sampling-frequency priority found 84. Adaptive SDAIF found 114 and did not miss any round containing a positive site.

SDAIF tied the best single model and adaptive Bayesian policy on total discoveries, so we claim non-inferiority to the strongest comparator, not universal superiority.

## 3:15–3:45 — Limit and next step

The transfer stress test was weaker on sites absent from training. This means a new city needs local calibration. We do not claim direct E. coli detection, drinking-water-pipeline tracing, Delhi deployment, or illness reduction.

Our next step is a prospective partnership with a monitoring authority. We will freeze NADI before sampling and compare its test order with routine practice. The measured impact will be confirmed contamination found with the same testing capacity.

AI assistance supported software and document development. Every scientific result remains traceable to the repository and authentic source records.
