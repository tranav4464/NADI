# V4 data and evidence gate

The Xylem build follows the CBSE synopsis and plans 11, 13 and 14. This ledger
records which acquired tracks have actually been executed, so possession of a
file is not confused with validated integration.

| Track | Local evidence | Present status | Next required proof |
|---|---|---|---|
| Marion County E. coli + NOAA | 6,134 processed rows, 128 sites | I1 in current pipeline; surface-water endpoint only | Compare original ISEF model families, fixed-threshold F1, temporal/site ablations |
| Bangladesh MICS | 6,069-row `.sav`; source/household raw endpoint audit and district-held-out baseline | I1 separately evaluated; no pipe-network linkage | Resolve paper/derived-label discrepancy; improve beyond always-positive baseline before decision-layer use |
| Chennai PWD | Paper locally available | R0 identified; row data unverified | Obtain row-level table or retain as prior art only |
| Hubli-Dharwad | Published paired intermittent-supply study | R0 identified; row data unverified | Verify paired row data and same-zone topology accessibility |
| Bristol operational telemetry | 209,584 local CSV rows, flow/pressure/ORP/FAC | R1 acquired | Reproduce telemetry method and event-held-out anomaly test |
| GECCO 2019 | 132,480 training rows plus chronological validation/test; real drinking-water sensor `Event` flag | I1: event baseline test F1 0.483, recall 0.586; no microbial labels | Calibrate anomaly signal for NADI and measure transfer; never call it E. coli detection |
| BattLeDIM L-TOWN | INP, pressure/flow/level/leak files; eight-scenario ensemble and four held-out decision cases | I2: SDAIF Coverage@3 0.257 vs adaptive Bayesian 0.359; one abstention on incompatible evidence | Correct SCADA parsing, reproduce leak benchmark, design and test model-mismatch fallback |
| WDSEventDB | Local archive | R1 acquired | Inspect schema, event labels and physical-testbed applicability |
| Net3 EPANET/WNTR | 24 generated scenarios | I1 simulated hydraulic demonstration | Source-localisation metrics, out-of-ensemble truth, arrival-time validation |
| Prior NADI mathematics | Historical scripts and references | Partly regression checked | Execute original reference, semantics audit, controlled modification |

No cross-track row-level join is authorised without common event, location,
time and endpoint identifiers. An 88% accuracy/F1 claim requires independent
biological truth in the evaluated domain; a simulated reach score cannot
substitute for it.

The frozen V3 headline is not the V4 primary metric: 44 of its 120 events have
no affected candidate, and the former metric scored each as perfect coverage.
V4 corrected conditional budget accounting, separated empty events and was
run from a frozen protocol. Its nonempty-event Coverage@3 is 0.504 for SDAIF
and 0.504 for adaptive Bayesian. The V3 headline remains superseded.

The full prioritized list of remaining work is `docs/OPEN_ISSUES_REGISTER.md`.
