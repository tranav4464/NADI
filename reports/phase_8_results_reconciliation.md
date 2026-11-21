# Phase 8 — results reconciliation

## Output

The canonical matrix is `reports/canonical_performance_matrix.csv`. It has ten
rows covering the nine required evidence tracks, with authentic microbial
classification represented by separate F1 and ROC-AUC rows. Every row records
dataset, evidence status, split, sample count, metric, result, baseline,
confidence-interval availability, randomization method, artifact, generating
command, and limitation.

## Reconciled current facts

- The authentic EA locked model has F1 0.838 and ROC-AUC 0.866 on 545 mixed
  environmental-water observations. Its locked prevalence is 0.642 and
  specificity is 0.390.
- In 41 historical three-test rounds, SDAIF found 114 high results versus 84
  routine and 80 deterministic-random. Across 2,000 common-candidate random
  permutations, random selection averaged 82.62 high results (95% range 75–90).
  SDAIF still ties both the best single model and adaptive Bayesian policy at 114.
- Unseen-site EA transfer is weaker: F1 0.737 on 140 records; this is not a
  Delhi-NCR result.
- BWFLnet pressure reconstruction has median logger MAE 0.278 m across 18,171
  predictions, but has no microbial labels and used a previously inspected
  validation period.
- Net3 is simulation: SDAIF Coverage@3 0.615 ties adaptive Bayesian. L-TOWN
  transfer is negative: SDAIF 0.257 versus 0.359 for hydraulic/adaptive
  Bayesian ranking over four hidden nonempty cases.
- GECCO telemetry, Texas pressure-wave runs, and the bounded Open E. coli
  prior-art adaptation remain separate supporting or stress-test tracks.

## Preserved negative results

The matrix deliberately retains the Net3 tie, L-TOWN deficit, weak unseen-site
transfer, low EA specificity, high locked prevalence, the frozen deterministic
random ordering (now accompanied by a 2,000-permutation uncertainty audit),
unavailable culture release times, and BWFLnet's
non-pristine validation period. No row converts a pressure or simulated
endpoint into biological evidence.

## Verification

`python scripts/canonical/build_canonical_performance_matrix.py` rebuilt the
matrix from canonical/retained artifacts. `tests/test_canonical_performance_matrix.py`
checks required tracks, artifact/limitation fields, Net3's simulated label and
the L-TOWN negative comparison.

## Remaining uncertainty

Confidence intervals are only retained where previously computed; no new
interval was invented. Several supporting tracks are historical artifacts that
have not yet been migrated. Phase 9 must determine the narrowest defensible
scientific contribution from this reconciled evidence.
