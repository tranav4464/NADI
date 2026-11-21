# NADI domain coverage matrix

NADI is not a biological-detector project. Biological labels are one reference
track used to calibrate the risk layer where they exist. The mathematical core
operates on uncertainty, movement, evidence quality and constrained action.

| NADI function | Non-biological input | Mathematical operation | Verified artefact | Claim boundary |
|---|---|---|---|---|
| Physical network intelligence | pressure/flow/chlorine/turbidity/telemetry | causal robust normalisation, missingness and anomaly scores | Bristol + GECCO audits | operational proxy; no pathogen claim |
| Location adaptation | site/regime histories | local median/MAD with sparse-group fallback | `telemetry.normal` tests | no universal threshold assumed |
| Intrusion pathway | pressure loss, restart, defects, flooding, sewage proximity | bounded monotone evidence interval | intrusion unit tests/demo | heuristic evidence, not measured entry |
| Evidence fusion | forecasts, anomalies, hazards, source reliability | typed interval fusion with disagreement inflation | fusion tests/demo | uncertainty is retained, not hidden |
| Hydraulic movement | network topology, demands, tanks, valve scenarios | EPANET/WNTR trace and travel-time ensemble | Net3/L-TOWN results | simulated tracer reach unless field-calibrated |
| Affected region | scenario reach sets | probabilistic node coverage and consequence weighting | localization/placement audits | conditional on enumerated scenarios |
| Decision optimisation | test budget, cost, delay, consequence | adaptive Bayesian / minimax-regret ranking and certificates | V4/V5 + ablations | equivalence, not superiority |
| Delayed evidence | result-arrival times and deadlines | pending-state updates and re-ranking | delayed SDAIF tests | measured turnaround still external |
| Transfer | new sites/cities/networks | support diagnostics, fallback and abstention | geographic and second-network audits | Delhi performance not established |
| Biological reference | independent E. coli labels where available | endpoint-specific calibration/evaluation | Marion/Bangladesh audits | never inferred from ordinary sensors |

The deliverable is therefore a decision system: **evidence → uncertainty set →
network consequences → constrained action**. A biological sample is one way to
validate a risk component; it is not the definition of the framework.
