# Phase 3 code ownership and dependency audit

**Files inspected:** Authentic site-round, model, policy and benchmark modules; SDAIF engine; evaluation metrics and benchmark; Marion weather model; BWFLnet trainer; hydraulic ensemble/generator; L-TOWN ensemble and out-of-ensemble runners; reporting builder; Flask server; CLI; configs and versioned result summaries. See `phase_3_code_ownership_matrix.csv` for 13 principal modules and `phase_3_dependency_graph.md` for flows.

**Commands:** `rg --files`, function/import/read/write searches, targeted PowerShell reads, CSV-shape check and notebook file search. The ownership CSV parses as 13 rows and 12 columns. No experimental output was regenerated in this phase.

**Changes:** Added the dependency graph, ownership CSV, duplicate-logic report and this audit. Existing code, data and results were not moved or deleted.

**Tests:** No new test run was needed to establish static ownership. Phase 1's clean-environment test suite and fresh authentic reproduction are prior evidence; they do not validate the reporting builder's fallback behavior.

**Results:** Authentic and simulated SDAIF implementations have different losses and uncertainty semantics. Authentic and simulated metrics have different denominators. The package CLI currently owns the older/simulated path; standalone scripts own the headline EA path. The dashboard directly reads named result files and exposes all historical outcomes in one API response. The L-TOWN stress runner has Net3 defaults unless given explicit config. The generated evidence report silently falls back V5 -> V4 and has a V4 chart title even when using V5.

**Failures and uncertainty:** Default generators can overwrite named locked artifacts. The current report generator can present a mixed-domain chain in language stronger than the underlying evidence. Static source inspection cannot certify all dynamic consumers. No canonical run manifest or single guarded API exists yet.

**Evidence status and next inputs:** Phase 4 can now record a no-delete migration map, keep historical files at their current paths unless a move is demonstrably safe, and introduce an explicit canonical namespace. Phase 5 must guard outputs and make every command require configuration. Phase 6 must examine current-sample features and release times; Phase 7 must test dashboard and report semantics.
