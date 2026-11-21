# NADI Mathematical Method

## Central applied-mathematics problem

NADI does not ask only whether contamination risk is high. It asks which
limited sequence of confirmatory tests has the smallest defensible decision
loss when biological risk and water movement are both uncertain.

For candidate nodes `V`, a test plan `A`, risk `p`, affected set `S`, node
consequence `w_i`, and per-test cost `c`, NADI uses

`L(A; p,S) = p * sum_{i in S\A} w_i + c|A|`.

The first term penalises consequential affected nodes missed by the plan; the
second prevents unlimited testing. The oracle loss for a scenario is the best
plan that could have been chosen if that scenario were known.

## SDAIF minimax-regret decision

The calibrated risk interval and hydraulic ensemble form a finite uncertainty
set `Q`. SDAIF chooses

`A* = argmin_A max_{q in Q} [L(A;q) - min_B L(B;q)]`.

This carries uncertainty into the action itself. The maximum term also returns
an adversarial witness: the compatible risk/network scenario under which the
chosen plan performs worst.

## Typed evidence fusion

Independent evidence streams are represented as intervals with reliability,
support, domain and availability time. The fusion layer uses reliability times
support weights and widens the combined interval when contributors disagree:

`p_f = sum_j w_j p_j / sum_j w_j`.

An explicit disagreement inflation and dominant-uncertainty label are retained.
An unsupported intrusion or sensor stream contributes no false confidence; it
causes wider uncertainty or abstention.

## Protective-action support

For each advisory action `a`, NADI computes an operator-review score:

`U(a) = risk_upper * consequence * coverage(a) - cost(a) - delay_penalty(a)`.

This ranks sampling, inspection, flushing, isolation and precautionary notices;
it never actuates a utility and remains separate from laboratory confirmation.

## Adaptive evidence acquisition

For each untested node `j`, SDAIF evaluates both possible revealed results and
re-optimises the remaining plan. Its robust evidence value is

`VOI(j) = R_static - max_{y in {0,1}} R_after(j,y)`.

The next test maximises robust regret reduction, with deterministic tie-breaking.
Only after that location is selected may its hidden result be revealed. The
result filters the compatible scenario set before the next decision.

## Certificate and abstention

If worst-case post-test regret is at most a declared `epsilon`, the action has
an epsilon-regret certificate relative to the finite declared uncertainty set.
It is not a universal safety guarantee. If domain support is inadequate or
revealed evidence is inconsistent with every scenario, NADI abstains.

## What is original here

The project contribution is an executable integration of calibrated
E. coli-referenced evidence, domain gating, uncertain hydraulic reach,
consequence-weighted minimax regret, sequential evidence value, adversarial
explanation and abstention. Global theorem novelty is not claimed. Each part
has established antecedents; NADI's research question is whether this coupled
decision chain improves limited testing and remains auditable.

## Verification map

The precise equation-to-code-and-test map is maintained in
`docs/MATHEMATICAL_ASSURANCE_CASE.md`. It distinguishes implementation
properties proved by tests from environmental claims that require field data.

- `microbial_risk/weather_model.py`: temporal and site-held-out calibration.
- `transfer/gate.py`: support inflation and abstention.
- `hydraulics/generate.py`: 24 EPANET/WNTR scenario ensemble.
- `sdaif/engine.py`: loss, oracle, regret, robust plan and adaptive VOI.
- `sdaif/fusion.py`: typed interval fusion and disagreement inflation.
- `hazards/intrusion.py`: monotone bounded intrusion-context evidence.
- `decision/actions.py`: consequence/cost/delay protective-action ranking.
- `evaluation/benchmark.py`: hidden truth, fair information timing and locked metrics.
- `tests/`: future-feature exclusion, split integrity, monotonic/hand cases,
  adaptive timing, hydraulic diversity and dashboard abstention.

## Proven boundary

The corrected V4 benchmark shows equivalence to the strongest fair adaptive baseline,
not superiority. The certificate applies to the enumerated uncertainty set.
The microbial model uses surface-water evidence, and network consequences are
simulated on public Net3. Confirmatory laboratory testing remains necessary.
