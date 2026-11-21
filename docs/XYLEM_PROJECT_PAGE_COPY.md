# Xylem project page copy

## Project title

NADI: Mathematical Prioritisation of Limited E. coli Testing

## Challenge

Water Quality: Safeguarding water resources from pollution and degradation

## Short description

NADI helps a water-monitoring team decide which locations should receive limited confirmatory E. coli testing first. It combines calibrated predictions with a mathematical regret optimisation and updates the test list after each authentic laboratory result.

## Problem

E. coli cannot be confirmed visually, and a monitoring authority cannot collect and process every possible sample simultaneously. Fixed sampling routines may spend scarce capacity at low-yield locations while serious contamination remains unconfirmed elsewhere. The operational bottleneck is deciding where the next limited tests should begin using only evidence already available.

## Solution

NADI creates strictly past-only features from authentic site and regional laboratory history, season, and location. Logistic regression, histogram gradient boosting, and XGBoost produce calibrated probabilities. SDAIF then solves a mixed-integer optimisation that balances posterior average regret with worst-case regret across the calibrated models.

The system returns an ordered testing list. After a selected site's authentic result is revealed, Bayes' rule updates model credibility and NADI recalculates the remaining locations. The dashboard displays risk, model disagreement, observed coordinates, the frozen test order, and the real laboratory outcomes.

## Demonstrated result

The experiment used 14,069 authentic Environment Agency laboratory observations, aggregated into 13,405 site-day records from 920 monitoring sites. Training, probability calibration, policy selection, and locked testing were separated chronologically.

On 545 untouched site-day records, the selected XGBoost model achieved F1 0.838, ROC-AUC 0.866, PR-AUC 0.916, sensitivity 0.966, and balanced accuracy 0.678.

Across 41 authentic multi-site sampling rounds, every policy received the same information and a three-test budget. Adaptive SDAIF found 114 confirmed high-E.-coli results. Deterministic random testing found 80, and routine sampling-frequency priority found 84. SDAIF missed no positive round. It tied the strongest single-model and adaptive-Bayesian comparators on total discoveries.

## Innovation

Most prediction studies stop at a probability or risk map. NADI continues to an auditable resource-allocation decision. It carries disagreement among calibrated models into the final test list, balances expected and worst-case regret, and updates sequentially after authentic results.

The contribution is the coupled uncertainty-to-testing workflow and its authentic operational evaluation. We do not claim that each mathematical ingredient is globally new.

## Impact and feasibility

The demonstrated impact is more confirmed high-E.-coli results found with the same testing capacity. A monitoring organisation could adapt NADI using its historical laboratory table and location metadata. The next validation step is prospective: freeze the model before sampling, then compare its test order with routine practice.

Transfer performance fell on sites absent from model training. NADI therefore requires local calibration and must abstain when support is weak.

## Limitations

This project does not claim direct E. coli detection by ordinary sensors, drinking-water-pipeline tracing, a contaminated branch, Delhi-NCR performance, prospective deployment, or illness reduction. The current evidence comes from authentic UK surface-water monitoring.

## Outside assistance and AI disclosure

AI assistance supported software implementation, data auditing, mathematical documentation, dashboard development, and presentation preparation. The student directed the project, selected the scientific problem and claims, and remains responsible for checking all results. Every reported performance number is reproducible from the repository and authentic source records.

Add all human assistance before submission:

- Teacher or supervisor: `[name and contribution]`
- External mentor: `[name and contribution]`
- Laboratory or organisation: `[name and contribution]`

## Links to add

- Public 3–4 minute video: `[URL]`
- Public slide deck or PDF: `[URL]`
- Source repository or reproducibility archive: `[URL]`
- Optional live dashboard: `[URL]`
