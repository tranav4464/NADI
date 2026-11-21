# NADI Xylem open issues register

Scope: CBSE synopsis; execution plan 11; reuse map 13; replication plan 14;
current software and measured outputs. This is the single status list. A
component counts as complete only after the stated evidence exists. Priority
reflects the effect on the central nowcast → affected region → testing decision.

| ID | Priority | Issue and evidence | Work needed to close |
|---|---|---|---|
| N01 | Critical | No paired drinking-water E. coli, sensor, supply-cycle and node records; `docs/V4_DATA_AND_EVIDENCE_GATE.md`. | Obtain or collect linked observations, or keep biological and network claims separate. |
| N02 | Critical | Current Net3 benchmark outcome is tracer reach, not E. coli; `docs/CORE_COUPLING_AUDIT.md`. | Define a coherent biological state and validate test ranking against independent microbial labels. |
| N03 | Critical | Surface-water forecast remains a common scalar risk across test nodes; the completed ablation confirms point/wide risk changes regret and certification but not node selection or Coverage@3. It cannot locate E. coli within a network. | Add defensible node-specific evidence or constrain the claim to event-level risk plus hydraulic reach. |
| N04 | Critical | The 88% accuracy **and** meaningful positive F1 target is unmet: Marion nowcast 0.606/0.464, forecast 0.598/0.439; Bangladesh source 0.553/0.508, household 0.806/0.893 but below always-positive F1. | Reproduce stronger methods with locked endpoint/splits; retain independent baseline and report actual result if still below target. |
| N05 | High | Bangladesh derived `e_coli` follows source `WQ27`, while the paper describes household water; 2,904 valid household labels differ. | Keep raw source/household endpoints separate; seek author clarification before exact paper-replication claim. |
| N06 | High | L-TOWN held-out parameter cases: SDAIF Coverage@3 0.257 vs adaptive Bayesian/hydraulic 0.359; one scenario-set mismatch abstention. | Design a prespecified mismatch response and evaluate on additional held-out networks/events. Do not claim cross-network superiority. |
| N07 | High | Current finite-set regret certificate applies only if the actual state is inside the enumerated scenario/risk set. | Test coverage of that set under held-out conditions; invalidate the certificate and issue an explicitly uncertified fallback when contradicted. |
| N08 | High | Lab-delay semantics now exist in the engine and synthetic sequence, but measured turnaround, real alert timing, and dashboard integration are absent. | Add timed event records and decision deadline to application/API; evaluate decision value with realistic arrival times. |
| N09 | High | No independent real-network topology, valve-state, calibrated demand or field tracer observations for Delhi/Ghaziabad. | Keep Net3/L-TOWN simulated; acquire a bounded verified network only before local route claims. |
| N10 | High | No prospective event-level utility response trial or independently adjudicated contamination events. | Log prospective alerts, actions and control sampling; compare discovery time and tests to confirmation. |
| N11 | High | Source consistency is implemented; L-TOWN top rank 3/4, but all 12 unseen Net3 source cases would be falsely attributed if the rank were interpreted as exact origin. | Broaden source hypotheses, improve test placement and evaluate unknown-source rejection on independent cases; label ranks as conditional on enumerated scenarios. |
| N12 | High | GECCO drinking-water sensor-event baseline is reproduced (test F1 0.483); Bristol is now audited with 209,584 chronological operational records but has no event or biological labels. Neither has biological truth paired to NADI's network events. | Keep Bristol scores as bounded proxy evidence; no microbial detection claim. A labelled operational evaluation remains external. |
| N13 | High | Transfer to Delhi-NCR has no endpoint-compatible labelled holdout; Bangladesh and Marion differ in domain. | Add support/shift diagnostics, local-normal recalibration, uncertainty inflation and abstention; do not claim Delhi performance. |
| N14 | Medium | Net3 misses unseen-source routes; L-TOWN placement holdout shows a source-pair set-cover heuristic can rank source well while leaving 4/8 cases with no affected candidate. Balanced cover did not beat original Coverage@3. | Formulate and benchmark a joint coverage/discrimination/access objective across more networks; do not claim the attempted heuristic is superior. |
| N15 | Medium | The full historical SDAIF reference, nine-method benchmark, semantics table and controlled migration required by plan 14 are not yet executed end to end. | Re-run references without overwriting historical artefacts; reconcile conditional/ex-ante and static/contingent definitions. |
| N16 | Medium | ISEF weather–E. coli method is reconstructed only in broad form; exact original cleaned data/code and feature/split choices are not verified. | Reproduce documented model-family baselines and mark unverified details rather than calling exact replication. |
| N17 | Medium | The Xylem hardware-free path uses separate observed datasets and simulated network scenarios, with no common event key. | Make provenance and evidence-domain labels visible throughout dashboard and output cards; reject false row-level joins. |
| N18 | Medium | Protective actions and population consequences remain simulated or advisory; no operational actuation or response outcome. A consequence/cost/delay action-ranking module is now exposed in the demo. | Compare action policies and obtain operator review; do not claim automatic actuation or field response. |
| N19 | Medium | V4 includes placeholder `risk_only`, `context_only`, `anomaly_only` fixed orders, not separately replicated models. The next declared policy set excludes them, and benchmark code now respects the declared policy list. | Build actual component models before reintroducing their names; run a new locked comparison without them. |
| N20 | Medium | A fresh Python 3.10 environment now reproduces the test suite, claim audit and performance matrix; external mathematical/water-network review remains outstanding. | Share `docs/CLEAN_ENV_REPRODUCTION.md` and the repository with an external reviewer. |
| N21 | Medium | Claim matrix, Xylem pitch and dashboard now expose measured baselines and negative transfer/equivalence findings; final mentor/judge review remains external. | Use the revised claim matrix and pitch for submission; obtain an independent reviewer’s critique before final filing. |
| N22 | Medium | Location-adaptive normalisation was previously described but not separately evidenced. | Added a causal robust-normal module with sparse-group fallback and unit tests; apply it only where a training window and group identifier exist. |

## Closed or partially closed controls

- V3 empty-event Coverage@k flaw and conditional budget error were corrected
  for V4; V4 uses 76 nonempty events for its primary metric.
- Raw Bangladesh source and household endpoints, censoring and invalid codes
  are audited in `results/bangladesh_endpoint_audit.json`.
- Pending tests cannot be reused or counted as revealed evidence in the SDAIF
  engine; delayed scheduling has unit tests. Application integration remains N08.
- A second-network hydraulic run and held-out decision test exist; they reveal
  weakness rather than establish cross-network transfer (N06).

The goal stays active until the required build and evidence are complete. A
missing field dataset does not justify substituting simulated reach for
biological confirmation.
