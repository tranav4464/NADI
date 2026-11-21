# Bristol POU telemetry audit

`scripts/evaluate_bristol_telemetry.py` audited the acquired Bristol operational dataset without inventing an event or E. coli label.

- 209,584 rows from 2019-11-01 through 2022-09-27.
- Seven operational channels: flow, discharge pressure, TMP, ORP, FAC, filtration flux and UF membrane pressure.
- Median cadence: five minutes; 5th–95th percentile both five minutes.
- Missingness ranges from 0% (filtration flux and UF membrane pressure) to 8.19% (TMP).
- A chronological 60/20/20 split was used.
- Robust-distance and Isolation Forest scores were fitted on the early partition and thresholded on the calibration partition.
- Isolation Forest flagged 47 of 41,917 test rows (0.112%); the robust-distance threshold flagged none in the test window.
- A regime-adaptive robust-normal audit grouped observations by operating hour,
  fitting each baseline on the training partition only. Its q=.995 calibration
  threshold flagged none of the test rows; this is a stability result, not a
  contamination result.

There is no independent event or biological reference label in this resource. Therefore the audit reports data quality and unsupervised score behaviour only; it does not report accuracy, F1, E. coli detection or contamination performance. Bristol scores may enter NADI as operational proxy evidence after domain and sensor-health gating.
