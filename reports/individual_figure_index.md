# NADI individual research figures

These figures are generated from the locked canonical authentic prediction table:

`results/canonical/authentic/audit_20261120_07/authentic_locked_site_predictions_and_zones.csv`

They are derived visualisations only. No model was retrained, no frozen result was changed, and no synthetic observations were added.

| Figure | Research question | Evidence |
|---|---|---|
| 01 | How does declared endpoint prevalence vary by round? | LAB_CONFIRMED |
| 02 | How uneven is site observation density? | LAB_CONFIRMED |
| 03 | Do estimated probabilities separate observed endpoints? | LAB_CONFIRMED + MODEL_ESTIMATE |
| 04 | Are probabilities reliable on the locked data? | LAB_CONFIRMED + MODEL_ESTIMATE |
| 05 | What are locked ROC and precision–recall curves? | LAB_CONFIRMED + MODEL_ESTIMATE |
| 06 | Where do model probabilities disagree? | MODEL_ESTIMATE |
| 07 | How does current risk relate to historical site evidence? | LAB_CONFIRMED + MODEL_ESTIMATE |
| 08 | How many positives are captured as the test budget increases? | LAB_CONFIRMED + MODEL_ESTIMATE |
| 09 | Where is calibration over- or under-confident? | LAB_CONFIRMED + MODEL_ESTIMATE |
| 10 | How do candidate counts and positives vary by round? | LAB_CONFIRMED |
| 11 | How does site-support status relate to prevalence? | LAB_CONFIRMED |
| 12 | How does the decision threshold trade off metrics? | LAB_CONFIRMED + MODEL_ESTIMATE |
| 13 | Where is estimated risk in rounded coordinate space? | MODEL_ESTIMATE |
| 14 | Where are observed high endpoints in rounded coordinate space? | LAB_CONFIRMED |
| 15 | How do model-family probability distributions differ? | MODEL_ESTIMATE |
| 16 | How many confirmed results does each policy capture? | LAB_CONFIRMED |
| 17 | How uncertain is the random-policy comparator? | LAB_CONFIRMED |
| 18 | Does SDAIF tie or exceed the declared comparators? | LAB_CONFIRMED |
| 19 | How much does the BWFLnet pressure estimator improve over baseline? | OBSERVED + MODEL_ESTIMATE |
| 20 | How often do hydraulic prediction intervals cover observations? | OBSERVED + MODEL_ESTIMATE |
| 21 | What is the conditional Net3 tracer coverage result? | SIMULATED |
| 22 | How do the separate evidence tracks compare? | MIXED, LABELLED |
| 23 | How does model disagreement relate to estimated risk? | MODEL_ESTIMATE + LAB_CONFIRMED |
| 24 | Where are estimated risk hotspots concentrated by region? | MODEL_ESTIMATE |
| 25 | How does the confirmatory-testing budget change capture? | LAB_CONFIRMED + MODEL_ESTIMATE |

All files are in `figures/nadi_individual_research/` and carry an evidence-status footer.
