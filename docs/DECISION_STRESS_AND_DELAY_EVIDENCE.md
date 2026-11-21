# Decision-core stress and delayed-evidence evidence

The reference Net3 ensemble contains 24 simulated tracer scenarios. All test
outcomes below mean **tracer reached this node at the 1% threshold**, never
laboratory-confirmed E. coli.

## Prespecified hidden-parameter tests

`configs/out_of_ensemble_v1.json` held out six Net3 combinations of demand,
tank level and closed pipe. Four had at least one affected candidate. SDAIF
matched the adaptive Bayesian comparator on mean Coverage@3 (both 0.339).
Every hidden candidate-node reach pattern was still represented in the
reference ensemble. Thus V1 tests numerical parameter shift, not genuinely
unrepresented reach states.

`configs/out_of_ensemble_v2.json` added six source nodes never included as
reference tracer sources, with two operating settings each. Eight of 12 cases
had affected candidates. SDAIF and adaptive Bayesian both reached 0.295 mean
Coverage@3; one-round-delayed SDAIF also reached 0.295. Again, all candidate
reach patterns were represented. Some unseen sources had zero reach at the
chosen 12 nodes, showing that the placement design is narrow. This does not
prove source localisation or generalisation to arbitrary source nodes.

## Independent L-TOWN network

`scripts/generate_ltown_ensemble.py` generated eight L-TOWN tracer scenarios
from two reservoir sources, two demand multipliers and two tank levels. Its
12 selected candidates distinguish all eight reference reach patterns.
`configs/ltown_decision_stress_v1.json` held out four intermediate operating
settings. Three of their candidate reach patterns were absent from the eight
reference patterns. Results:

| Policy | Mean Coverage@3 on four nonempty cases |
|---|---:|
| Adaptive SDAIF | 0.257 |
| SDAIF with one extra result round | 0.229 |
| Adaptive Bayesian | 0.359 |
| Hydraulic-only | 0.359 |

SDAIF abstained after observed test evidence in one of the four cases. This is
the mathematically correct signal that its enumerated compatible set has
failed, but the current decision workflow stops instead of automatically
providing an uncertified fallback or requesting another observation. The
comparison is exploratory and small; it disproves a blanket superiority claim
on this second network.

## Delayed evidence implementation

The SDAIF engine now accepts a pending-test set and counts those tests against
the original budget. Pending results do not filter the compatible scenarios.
If a newly selected test will return after the action deadline, the engine
uses its static robust plan and does not report contingent information value.
`src/nadi/sdaif/delayed.py` simulates result arrival by selection round. Unit
tests verify no duplicated pending tests, no early disclosure and budget
accounting. This is a synthetic scheduling model, not measured laboratory
turnaround.

The core next step is a prespecified model-mismatch policy: when observed
evidence excludes all enumerated scenarios, flag the uncertainty certificate
as invalid and issue a separately labelled conservative fallback or request
expanded scenarios. The finite-set certificate applies only when the true
state lies in the set; none of these experiments proves that condition in a
municipal network.
