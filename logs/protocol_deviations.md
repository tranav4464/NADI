# Protocol deviations and negative findings

## 2026-11-18 — V1 comparator fairness

The V1 locked benchmark gave adaptive SDAIF sequential test-result access while its Bayesian comparator remained static. Although this reflected the intended difference between adaptive and static policies, it was insufficient for the claim “strongest fair baseline.”

Action taken before promoting a headline result:

1. V1 outputs and hashes were preserved unchanged.
2. An adaptive Bayesian value comparator was added.
3. V2 was frozen in a new configuration before execution.
4. Only V2 may support the strongest-baseline comparison.

## 2026-11-18 — V2 configuration-hash reporting bug

The first V2 summary hashed the default V1 configuration path even though the V2 configuration object governed execution. Event decisions and metrics were unaffected; the summary provenance field was wrong.

The benchmark now hashes the exact canonical configuration object passed to the runner. V2 was rerun under the unchanged decision configuration, and the corrected summary supersedes the hash-defective summary.

# V3 hydraulic enhancement (pre-registered before execution)

V2 used the historical six-scenario reference ensemble. Before inspecting V3
decision results, the hydraulic layer was replaced with 24 independently
generated EPANET/WNTR TRACE scenarios. The ensemble varies source, demand,
tank initial level and one closed pipe and uses pressure-dependent demand.
V3 retains the V2 fair adaptive Bayesian comparator. V1 and V2 remain preserved.

