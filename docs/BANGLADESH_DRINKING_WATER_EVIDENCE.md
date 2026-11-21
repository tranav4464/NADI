# Bangladesh MICS drinking-water replication and endpoint audit

Source snapshot: `nadi_resources/datasets/existing_verified/replication_data.sav`,
SHA-256 `441F2CD18674C1A51CC6CA99B1D74C9B032F404CF8C2B21944EAA3971464F8A9`.
The [published machine-learning study](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0343606)
links its minimal replication data to Figshare. The independent
[Bangladesh 2019 MICS water-quality report](https://psb.gov.bd/policies/wqtr2019.pdf)
reports roughly 40% E. coli positivity at the source and 82% at the point of
use. Those are distinct endpoints.

## Raw endpoint finding

The supplied 6,069-row file includes `WQ27` (source-water E. coli per 100 mL)
and `WQ26` (household-water E. coli per 100 mL). Code `0` means none detected,
`1`–`100` are positive counts, `101` means more than 100 and remains positive;
`991` and `992` are unreadable/lost and are excluded. The stored binary
`e_coli` equals `WQ27 > 0` for every row, including invalid-code rows. On
valid raw results, 2,904 household labels disagree with this stored binary
variable. It must never be treated as the household outcome.

See `results/bangladesh_endpoint_audit.json` for the exact paired 2×2 table.
The derived file and the paper's wording about “household drinking water”
therefore require a source-data clarification before exact paper replication
is claimed. We evaluate each raw endpoint separately.

## Leakage-safe baseline

`scripts/evaluate_bangladesh_drinking_water.py` uses household characteristics
known before laboratory results; it excludes all WQ test results and stored
binary E. coli variables. Districts are disjoint across model fitting,
calibration and the untouched test. Logistic regression and random forest
compete on calibration F1; the threshold is chosen there and then applied once
to the district-held-out test. This differs from the paper's random household
split and is a harder geographical transfer test.

| Raw endpoint | Test samples | Positive prevalence | Accuracy | Positive F1 | AUC | Always-positive F1 |
|---|---:|---:|---:|---:|---:|---:|
| Source `WQ27` | 1,169 | 0.380 | 0.553 | 0.508 | 0.609 | 0.551 |
| Household `WQ26` | 1,165 | 0.809 | 0.806 | 0.893 | 0.578 | 0.894 |

Neither model beats its simple always-positive baseline on positive F1. The
household model's apparently high F1 reflects high prevalence and weak
discrimination. The original [paper](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0343606)
reports 81.6% accuracy, 89.8% F1 and 0.686 AUC for its selected AdaBoost
model, and itself notes limited discrimination. Our held-out evaluation does
not reproduce that model or split and is not a direct score comparison.

The full confusion matrices, calibration scores, partitioned district IDs and
source hash are in `results/bangladesh_district_heldout.json`. These survey
results support a drinking-water transfer-stress track, not an intermittent
pipe-network nowcast, forecast, or affected-zone claim. The 88% accuracy plus
F1 objective has not been met on a biologically relevant held-out endpoint.
