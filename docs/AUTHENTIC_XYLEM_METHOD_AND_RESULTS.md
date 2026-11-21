# Authentic-only NADI method and locked result

## Frozen question

Among the real sites sampled in the same authentic monitoring round, which `k=3` sites should be processed first to maximise confirmed high-E.-coli discoveries while controlling decision regret across credible calibrated models?

## Endpoint

The endpoint is an authentic reported E. coli result at or above 500 in the EA record. This is a severe surface-water monitoring endpoint, not a drinking-water standard.

## Mathematical decision rule

For model vertex `m`, site `i`, calibrated probability `p_mi`, and binary test decision `x_i`, the missed-risk loss is

\[
L_m(x)=\sum_i p_{mi}(1-x_i),\qquad \sum_i x_i=k.
\]

The model-specific regret compares the chosen list with the best list for that model:

\[
R_m(x)=L_m(x)-\min_{z:\sum z_i=k}L_m(z).
\]

SDAIF solves

\[
\min_x (1-\rho)\sum_m w_mR_m(x)+\rho\max_mR_m(x),
\]

where `w_m` comes from validation log loss and `rho` is chosen only on validation. The finite problem is solved exactly as a mixed-integer linear programme. After a selected site's authentic result is revealed, Bayes' rule updates `w_m` and the optimisation is solved again.

All history features for a date are calculated before any result on that date updates history. Model choice, probability threshold and `rho` are fixed before the locked period is evaluated.

## Reproducible results

- `results/authentic_locked/authentic_experiment_report.json`
- `results/authentic_locked/authentic_test_events.csv`
- `results/authentic_locked/authentic_test_summary.csv`
- `results/authentic_locked/authentic_locked_site_predictions_and_zones.csv`

The strongest policies tie on total discoveries, so SDAIF's current result is non-inferiority plus transparent robustness—not a claim that it universally beats every simpler model.

## Transfer stress test

The locked period included 50 records from 31 sites that supplied no labels to model training. On this subgroup, XGBoost achieved F1 0.722, ROC-AUC 0.705, PR-AUC 0.749 and balanced accuracy 0.555. This is materially weaker than the full temporal holdout and is evidence against claiming automatic transfer to a new city. NADI therefore requires local calibration or abstention before deployment.
