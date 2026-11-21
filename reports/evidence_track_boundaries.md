# NADI evidence-track boundaries — Phase 2

| Track | Dataset and truth | Valid output | Invalid inference | Current status |
|---|---|---|---|---|
| EA authentic microbiology | UK EA determinand 2348, 2024, 14,069 raw records/13,405 site-days; mixed sea, river, estuarine, drainage and small effluent/other categories | Retrospective >=500 per 100 mL risk/ranking in observed agency candidates | Drinking-water safety or pipe E. coli detection | Authentic outputs rerun byte-identically from current processed file; prospective label availability unknown |
| BWFLnet authentic hydraulics | Published operational network and measured pressure/flow; 2,548 nodes/2,606 links | Internal pressure-state estimation under observed boundary conditions | Pathogen presence, source or affected region | Stored predictions independently re-aggregated; validation week previously inspected |
| EPANET/WNTR simulation | Net3/L-TOWN models, assumed sources/demand/valves, synthetic tracer reach | Conditional movement and policy stress under declared scenarios | Field biological validation | Net3 tie and L-TOWN negative transfer retained |
| Telemetry/anomaly | GECCO, Bristol and other operational records | Anomaly/regime detection in their source systems | Microbial truth | Supporting studies, not canonical EA labels |
| External transfer | Bangladesh, Lira, EA site-held-out and other domain-specific sets | Domain-limited stress tests and abstention evidence | Automatic Delhi/Ghaziabad performance | Weak unseen-site results retained |
| Historical benchmarks | V1–V5 configurations, events and protocol deviation log | Method-development history and corrected simulation comparisons | One combined current result | V3 and earlier defects must remain visible |
| Dashboard/demo | Stored authentic and simulated outputs | Explicit replay of each track with origin labels | Live contamination alarm | Route ownership and canonical API remain to be audited |

Evidence-class rules: an observed pressure is `OBSERVED`; a laboratory E. coli result is `LAB_CONFIRMED`; a classifier probability is `MODEL_ESTIMATE`; an EPANET tracer case is `SIMULATED`; an unverified valve/source assumption is `ASSUMED`. A physical measurement of one quantity does not validate another quantity. No graph route or model score is permitted to turn a simulated source into a confirmed contaminated pipe.

The public-facing canonical statement must disclose high locked prevalence (0.642), low specificity (0.390), the 114-way top-three tie, weak unseen-site performance and the timing assumption in same-round sequential replay. Current metadata that labels all EA rows as `surface_water_laboratory_observations` needs a versioned correction because the raw material field shows a wider mixture. The original metadata must remain preserved for audit.

This report is a boundary decision, not a claim that every software path already enforces it. Phase 3 must trace each route; Phase 7 must test evidence-class propagation and prohibited-inference checks.
