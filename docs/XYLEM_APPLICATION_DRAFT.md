# NADI — Xylem Application Draft

## One-sentence solution

NADI is an applied-mathematics decision system that combines calibrated
E. coli-referenced risk, uncertain water-network movement and limited testing
capacity to decide where confirmatory water testing should begin.

## Problem and user

Faecal contamination is invisible, laboratory confirmation takes time, and a
water utility cannot immediately sample every tank, branch and outlet. During a
suspected event, the operational bottleneck is choosing which locations to test
first before the potentially affected boundary is known. The immediate user is
a utility sampling or incident-response team operating under a fixed test budget.

## How NADI works

1. A calibrated model produces a nowcast or 24-hour E. coli-risk interval from
   historical microbiology and past-only environmental evidence.
2. A transfer gate measures support, widens uncertainty and abstains for an
   unsupported target rather than presenting false confidence.
3. EPANET/WNTR simulations estimate reach and arrival intervals across uncertain
   source, demand, tank and pipe-state scenarios.
4. SDAIF minimises worst-case avoidable decision loss and selects the next test.
5. After a result is revealed, incompatible scenarios are removed and the next
   location is recalculated.
6. The decision card reports the test order, regret bound, adversarial scenario,
   dominant uncertainty and evidence that would be most valuable next.

## Innovation

Most monitoring tools end with a risk score, alert or map. NADI carries
uncertainty through to a constrained action and makes the evidence-acquisition
sequence adaptive. It can also refuse unsupported transfer. The innovation
claim is this coupled, auditable uncertainty-to-action workflow—not a claim of
direct E. coli sensing or globally new mathematics.

## Prototype and measured result

The working software ingests frozen public resources, trains calibrated
nowcast/forecast heads, generates a 24-scenario public benchmark network,
executes adaptive decisions and serves the output through a dashboard. In a
locked set of 120 simulated network events with three tests, SDAIF achieved
0.686 Coverage@3, exactly matching the strongest fair adaptive Bayesian
baseline. It did not demonstrate superiority. It additionally returned a
finite-set regret certificate, adversarial witness and explicit abstention.

## Impact pathway

If validated locally, a utility could use NADI to avoid blind city-wide
sampling, send limited teams to the most decision-relevant outlets, update the
affected boundary after each confirmed result, and identify when evidence is
too weak for a recommendation. Impact will be measured first as fewer tests or
less time to find an independently confirmed affected location—not as assumed
illness prevention.

## Feasibility and scale

The software framework is network-agnostic. A new city package would provide a
bounded topology, operating states, local weather/context, calibration history
and independent microbiology. The same mathematics then runs with local
uncertainty. Until minimum support is met, NADI abstains. A utility pilot should
start with one pressure zone, not an entire city.

## Current limitations

- Microbial evidence is from surface water, not a paired intermittent drinking network.
- Net3 is simulated and not Delhi/Ghaziabad infrastructure.
- No direct E. coli assay or field installation is claimed.
- The locked benchmark establishes equivalence, not superiority.
- Prospective utility and independent laboratory validation remain future work.

## Ask from Xylem

Technical mentorship on distribution-network calibration, access to a bounded
anonymised pilot topology/operating scenario, and review of the decision metric
would enable the next decisive test: whether NADI’s prospective ranking finds
independently confirmed affected locations sooner than routine sampling.
