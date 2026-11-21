# NADI Claim Matrix

| Claim | Status | Evidence / boundary |
|---|---|---|
| NADI runs from frozen resources to a decision card | Demonstrated | Reproduction script and integration tests |
| Forecast uses only information available before the target day | Demonstrated | Feature contract and leakage tests |
| Risk output is E. coli-referenced | Demonstrated in source domain | Public laboratory E. coli observations; surface water only |
| NADI directly detects E. coli | Prohibited | No biological assay or paired drinking-water sensor labels |
| NADI estimates plausible affected regions | Demonstrated in simulation | 24 EPANET/WNTR TRACE scenarios on public Net3 |
| NADI represents Delhi/Ghaziabad pipes | Prohibited | No calibrated local topology or operations |
| SDAIF matches strongest fair baseline | Demonstrated in simulation | Locked V4 nonempty-event Coverage@3 equivalence |
| SDAIF outperforms strongest fair baseline | Not demonstrated | Paired difference and CI are exactly zero |
| SDAIF produces a finite-set regret certificate | Demonstrated | V3 certificate rate and engine tests |
| Unsupported transfer causes abstention | Demonstrated | Delhi-domain API test returns `[0,1]` and abstains |
| Location-adaptive normalisation is causal and sparse-site safe | Demonstrated | Robust local median/MAD module, global fallback, and unit tests; see `docs/LOCATION_ADAPTATION_EVIDENCE.md` |
| Telemetry/intrusion evidence is kept separate from biological truth | Demonstrated | Typed proxy/evidence domains, intrusion abstention on missing observations, and fusion tests |
| Protective actions are ranked by consequence, coverage, cost and delay | Demonstrated in simulation | Operator-reviewed action module; no automatic actuation or field response claim |
| NADI reduces illness or exposure | Not established | Requires prospective field and health evidence |
| SDAIF is globally mathematically novel | Not established | Requires exhaustive prior art and independent proof review |
