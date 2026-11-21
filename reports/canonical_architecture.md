# Canonical NADI architecture — Phase 2

## Evidence-supported system

The present canonical empirical claim is: **On a retrospective set of UK Environment Agency environmental-water E. coli observations with mixed sample materials, NADI uses past laboratory history and site context to rank a limited number of confirmatory tests.** In 41 eligible locked monitoring dates with a three-test budget, its adaptive SDAIF policy found 114 recorded high-count results, compared with 84 under routine-frequency ordering and 80 under one deterministic random order. The 114 count ties the best single model, fixed ensemble and adaptive Bayesian comparator. This is a retrospective prioritisation result within an agency sampling programme, not validated performance on drinking-water distribution pipes.

A separate authentic BWFLnet experiment estimates internal drinking-water-network pressure from sparse boundary observations. It validates hydraulic state estimation at monitored nodes under its stated training/validation protocol. It supplies no E. coli outcomes and does not turn the EA test into a network-contamination detector.

## Canonical execution contract

```text
EA historical laboratory records (mixed environmental materials)
  -> source hash and schema/domain check
  -> site-day consolidation and past-only features
  -> chronological train/calibrate/validation/test split
  -> calibrated candidate risk probabilities
  -> model-family weights and disagreement/support checks
  -> fixed-budget SDAIF plan, regret and adversarial model
  -> ordered site tests and auditable decision card
  -> laboratory result recorded when actually available
  -> later decision update using only released evidence
```

The current implementation executes the chain through `scripts/build_authentic_site_rounds.py`, `scripts/run_authentic_xylem_experiment.py`, `src/nadi/authentic/{site_rounds,models,policy,benchmark}.py` and the authentic dashboard route. Its same-round adaptive replay reveals historical outcomes immediately after each simulated selection. A deployable interface must carry result-release time; until that is measured, the primary operational output is the **initial fixed-budget list** and any update is a later-round operation. The mathematical objective is an implemented posterior/robust mixed-integer plan over calibrated model vertices. The current experiment has not shown greater total top-three yield than simpler leading comparators.

## Module responsibilities

| Module | Role | Input/outputs | Claim boundary |
|---|---|---|---|
| `authentic` | EA parsing, site-day history, chronological replay | Raw laboratory table -> processed rows, probabilities, policy events | Mixed environmental water only |
| `microbial_risk` | Other historical/transfer models | Named external datasets -> domain-specific estimates | Never silently pooled with EA |
| `decision` / `sdaif` | Fixed-budget actions, posterior update, regret | Candidate probabilities and budget -> plan and explanations | Policy validity conditional on input and model set |
| `hydraulics` | Real BWFLnet pressure study and separate source-tracing algorithms | Network/observed telemetry or scenario ensemble -> state or conditional reach | Pressure observation and simulated tracer are distinct |
| `simulation` (to be isolated) | Net3/L-TOWN scenarios and stress tests | Network model and declared assumptions -> simulated outcomes | No microbial field truth |
| `transfer` | Site/network support checks | Source/new-location metadata -> support or abstention | No universal-transfer certificate |
| `telemetry` | Operational anomaly/local-normal studies | Observed telemetry -> regime features | No E. coli label by itself |
| `reporting` / `provenance` | Hashes, metrics, claim matrix, reproducibility | All track artifacts -> traceable reports | A report cannot promote evidence class |
| `dashboard` | Read-only presentation and bounded replay | Canonical result API -> UI | Must display origin, date, endpoint and limitations |

## Data contracts

Every input and output must record `evidence_class` (`LAB_CONFIRMED`, `OBSERVED`, `MODEL_ESTIMATE`, `SIMULATED` or `ASSUMED`), `domain`, dataset/version/hash, location/time semantics, endpoint, split and generation command. A record from one track cannot acquire another track's label through a join on approximate geography or date. A biological/network join requires a verified common event with location, collection and release timestamps, laboratory label, network node, operating state and independent evaluation. No such joined dataset has been verified in this repository.

## Decision card

The canonical decision card should include decision time; candidate sites and available budget; ordered tests; endpoint and source domain; calibrated model probabilities; model disagreement and support; SDAIF objective and worst-case regret; adversarial model; evidence availability cutoff; abstention reason; model/data/config hashes; and a reminder that a recommendation is not a laboratory result. The current code implements many fields but lacks a single enforced schema and release-time field. Those are implementation tasks, not completed capabilities.

## Verification status and next inputs

Phase 1 independently reproduced the authentic files from the current processed CSV and recomputed BWFLnet metrics from stored predictions. It identified mixed sample materials, uncertain historical result availability, a potentially post-selection `sampling_purpose` feature, overwriteable locked paths and non-pristine hydraulic validation. Phase 3 must trace actual ownership and duplicates; Phases 5–7 must make the above execution contract enforceable and tested.
