# GECCO 2019 drinking-water sensor-event replication

The [primary GECCO 2019 dataset record](https://zenodo.org/records/3884444)
describes real-world water-quality telemetry supplied for an online event
detection challenge. The endpoint is the dataset's `Event` flag. It is **not**
an E. coli or faecal-contamination label.

`configs/gecco_event_v1.json` froze six sensor features (`Tp`, `pH`, `Cond`,
`Turb`, `SAC`, `PFM`), three baseline models, chronological train/validation/test
files, and validation-only model and threshold selection. The models are a
robust multivariate distance, isolation forest, and supervised random forest.
The selected model is robust distance. The final November 2017 test set was
used only after calibration selection.

| Test outcome | Value |
|---|---:|
| Rows | 31,650 |
| Event-positive rows | 191 (0.603%) |
| Accuracy | 0.9924 |
| Positive precision | 0.4103 |
| Positive recall | 0.5864 |
| Positive F1 | 0.4828 |
| ROC AUC | 0.9370 |
| Average precision | 0.4453 |
| Event runs with any alert | 8 of 12 |
| False positive rows | 161 |
| False negative rows | 79 |

The always-negative rule has 0.9940 accuracy and zero positive recall, so
accuracy alone is misleading here. Full validation candidates, hashes and
confusion counts are in `results/gecco_event_v1.json`.

This replicates the *task and data track* with simple baselines, not the exact
winner algorithm of the 2019 challenge. GECCO event scores can enter NADI only
as a sensor-anomaly signal with an explicit domain check. They cannot serve as
microbial ground truth or be joined row by row to Marion E. coli or Net3/L-TOWN
simulation because those sources have no common event identifiers.
