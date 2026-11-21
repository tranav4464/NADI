# Prior-method integration: calibrated forecasting risk head

NADI now reproduces the disclosed ISEF model-family comparison inside the production weather/E. coli risk head. The six families are represented as separate candidates (logistic regression, random forest, ExtraTrees, decision tree, gradient boosting, and XGBoost). A candidate is fitted on the chronological development partition, calibrated on a later calibration partition, and selected using **positive-class F1 on calibration data with Brier score as the tie-break**. The untouched test partition is used only once for reporting.

This is a method-selection layer, not a claim that any physicochemical sensor directly detects E. coli. The current risk head is trained on Marion County surface-water E. coli with weather covariates, so its claim boundary remains surface-water context forecasting. Household drinking-water and GECCO telemetry are evaluated in separate endpoint tracks.

## Current locked training result

Using the existing temporal split (development through 2018, calibration 2019–2020, untouched test 2021–2022):

- **Nowcast:** validation selected random forest (positive F1 0.3667); untouched test ROC AUC 0.6838, average precision 0.4853, Brier 0.1891, ECE 0.1290.
- **24-hour forecast:** validation selected logistic regression (positive F1 0.3651); untouched test ROC AUC 0.6518, average precision 0.4556, Brier 0.1947, ECE 0.1227.
- The model card records the full candidate table, selected threshold, calibration radius and claim boundary.

These values are not a guarantee of 88% accuracy/F1. They are a leakage-safe result on a surface-water endpoint and should not be presented as Delhi-NCR drinking-water performance. The lower scores are useful evidence: model-family selection alone does not solve domain shift or the missing paired drinking-water sensor/microbiology dataset.

## How this integrates into NADI

1. Weather/E. coli candidates provide a calibrated risk interval.
2. GECCO-derived anomaly methods remain a separate telemetry-anomaly evidence stream.
3. Local-normal, network and delayed-evidence layers contribute their own uncertainty objects.
4. SDAIF consumes the resulting evidence intervals and optimises a testing/protective-action policy; it does not silently treat one model probability as biological truth.
5. The final reports compare the selected model with all candidates and fixed baselines, preserving the untouched test set.

## Decision-layer regression after integration

The new no-placeholder-policy benchmark (`results/locked/benchmark_v5_no_placeholders_summary.json`) evaluated 120 simulated events, of which 76 had non-empty affected sets. At budget 3, adaptive SDAIF matched adaptive Bayesian at mean Coverage@3 = **0.6149** (paired difference 0.0000; 95% interval [0.0000, 0.0000]). The benchmark therefore passes the predeclared equivalence gate but does **not** support superiority. This result is an implementation regression check on the simulated network decision track, not evidence of E. coli detection or municipal performance.

The integration is therefore a reproducible reuse-and-modify step: prior methods supply candidate estimators and calibration practice; NADI adds endpoint separation, uncertainty propagation and decision-level evaluation.
