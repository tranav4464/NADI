# NADI canonical evidence report

## Approved scope

NADI is a retrospective testing-prioritization and decision-intelligence system. The primary evidence is UK Environment Agency mixed environmental-water E. coli observations. It does not establish direct sensor detection, drinking-water pipe contamination localization, Delhi-NCR performance, health impact, or an integrated biological-hydraulic field model.

## Authentic microbial-risk and decision track

- Locked period: 545 observations; positive prevalence 0.642.
- Selected validation model: `xgboost`; locked F1 0.838, ROC-AUC 0.866, PR-AUC 0.916, sensitivity 0.966, specificity 0.390.
- Across 41 eligible rounds at a three-test budget, SDAIF found 114 high results; routine frequency found 84; the deterministic random comparator found 80.
- SDAIF ties the best-single-model and adaptive-Bayesian policies on total positives. No superiority claim is supported.
- The sequential reveal is a retrospective same-round replay; actual laboratory-result release times are unavailable.

## Separate measured hydraulic track

- BWFLnet: 18171 stored predictions over 673 timestamps and 27 internal loggers.
- Median logger MAE 0.278 m; aggregate MAE 0.415 m; declared baseline improvement 66.3%.
- This is pressure reconstruction, not microorganism evidence. Its validation period was previously inspected.

## Reproducibility

Authentic run manifest: `C:\Users\TRANAV\OneDrive\Desktop\STEM PROJECT\nadi\results\canonical\authentic\audit_20261120_07/run_manifest.json`<br>
Hydraulic run manifest: `C:\Users\TRANAV\OneDrive\Desktop\STEM PROJECT\nadi\results\canonical\hydraulics\audit_20261120_01/run_manifest.json`
