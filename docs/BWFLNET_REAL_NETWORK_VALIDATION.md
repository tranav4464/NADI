# BWFLnet real-network validation

Source: Waldron, Pecci and Stoianov, *BWFLnet + data*, DOI 10.17632/srt4vr5k38.3 (CC BY 4.0). The four downloaded source files were checked against the publisher's SHA-256 hashes.

Full hybrid run: `.\.venv_clean\Scripts\python.exe scripts\train_bwflnet_full_hybrid.py`

The original simple offset benchmark remains reproducible with `.\.venv_clean\Scripts\python.exe scripts\evaluate_bwflnet_real_network.py`.

The published 2,548-node, 2,606-link EPANET network was run with its supplied controls and 15-minute schedule. The publisher's separate 24-hour logger folder trained one constant observed-minus-model offset per logger. The separate one-week folder was held out for evaluation. The benchmark also includes the uncalibrated physical model and the logger's training-day mean as a simple baseline. No test measurement was used to fit an offset.

| Held-out measure | Loggers | Raw EPANET median logger MAE | Calibrated EPANET median logger MAE | Training-mean median logger MAE |
|---|---:|---:|---:|---:|
| Pressure (m water) | 37 | 1.571 | 0.964 | 0.934 |
| Flow (L/s) | 6 | 1.918 | 1.138 | 3.066 |

## Full hybrid experiment

All six roughness variants published with BWFLnet were compared on the training day only. Grouped Hazen-Williams roughness had the lowest normalized training error. The hybrid estimator then combined this physical prediction with 16 contemporaneous boundary pressure/flow measurements and periodic time features. Ridge, partial least squares, Extra Trees and Random Forest candidates were compared using four expanding-window folds within the training day. Ridge with alpha 1 was selected and refitted on all available training-day rows.

The hybrid predicts the 27 internal pressure loggers; boundary sensors are inputs and are not included as hybrid targets. The six measured flows retain the selected physical model plus a training-only offset.

| Held-out measure | Model | Median logger MAE | Comparison |
|---|---|---:|---:|
| Internal pressure | Hybrid state estimator | **0.278 m** | 66.3% lower than training-mean baseline |
| Internal pressure | Training-mean baseline | 0.827 m | — |
| Internal pressure | Selected raw physics | 1.056 m | — |
| Flow | Selected physics + offset | **1.104 L/s** | 64.0% lower than training-mean baseline |
| Flow | Training-mean baseline | 3.066 L/s | — |

The hybrid beat the training-mean baseline at all 27 internal pressure loggers. Median per-logger R² was 0.730 and 24/27 loggers had positive R². Across 18,171 held-out internal-pressure observations, MAE was 0.415 m and RMSE was 0.706 m. Aggregate R² is not used as the headline because differences in mean pressure between nodes inflate a pooled R².

Training-CV residuals defined a nominal 90% absolute-error interval. Its held-out coverage was 84.9%, with median half-width 0.749 m, so the uncertainty interval is somewhat under-calibrated.

These are genuine measured hydraulic comparisons, not E. coli, chlorine, tracer-transport or affected-branch validation. The publisher's validation week had already been inspected during development of the simple offset benchmark, so it is a held-out evaluation but no longer a pristine untouched test.

The trained artifact, report, per-logger errors and 18,171 held-out predictions are under `results/bwflnet_full_hybrid/`. The next scientific step would be a newly frozen external network or later time period. This result is a separate hydraulic evidence track; it must not be combined row-wise with the Environment Agency E. coli records.
