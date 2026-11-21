# Biological performance baseline for the 88% target

The current trained heads were evaluated without retraining or changing the
2021–2022 test period. A binary alert threshold was selected by maximum F1 on
the 2019–2020 calibration period from the grid 0.01, 0.02, ..., 0.99. The
selected threshold was 0.12 for both heads. The resulting test outcomes are:

| Head | Test n | Accuracy | Precision | Recall | Positive F1 | TN | FP | FN | TP |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Nowcast | 4,186 | 0.6063 | 0.3542 | 0.6720 | 0.4639 | 1,825 | 1,300 | 348 | 713 |
| Forecast | 4,186 | 0.5984 | 0.3399 | 0.6202 | 0.4391 | 1,847 | 1,278 | 403 | 658 |

The endpoint is surface-water E. coli count >=1,000 per 100 mL, not E. coli
presence in drinking water. The test prevalence is 25.35%; always predicting
negative would produce 74.65% accuracy and zero positive F1. The current
models miss the 88% accuracy and F1 target by a wide margin. No parameter was
chosen using the 2021–2022 results in this audit. The threshold selection is
an exploratory retrospective audit of an already reported test period, so any
future model comparison requires a new untouched split.

The next modelling step must use a coherent drinking-water dataset and a
predeclared endpoint. Its accuracy and positive F1 must be assessed with
precision, recall, confusion matrix, calibration, site/event holdout and
prevalence reported together. The target is not a license to change labels,
exclude difficult samples or select a favorable final test period.
