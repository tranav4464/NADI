# NADI final goal requirements audit

Audit date: 19 November 2026. This document evaluates the active project goal
against current executable evidence. It does not treat a simulation, a
prototype, or an intended future partner study as field validation.

| Original objective requirement | Current status | Authoritative evidence | Exact boundary |
|---|---|---|---|
| Concentration-/hydraulic-event modelling | **Bounded** | EPANET/WNTR scenario code; `results/locked/`; `results/texas_physical_pressure_v1.json` | Digital-twin tracer events are simulated. Texas pressure data are real controlled leak/no-leak measurements, not concentration or microbial events. |
| Imperfect, delayed confirmatory tests | **Implemented in decision engine** | `src/nadi/sdaif/engine.py`; delay tests in `tests/test_sdaif.py` | No observed laboratory turnaround-time dataset has been supplied; no real delay-performance claim. |
| Node-specific uncertainty | **Implemented in simulation; unvalidated in a utility** | hydraulic ensemble, state scenarios, uncertainty tests | No calibrated, field-verified Delhi/Ghaziabad valve, demand, source or topology data. |
| Adaptive SDAIF decisions | **Demonstrated** | `src/nadi/authentic/policy.py`; authentic locked replay and its leakage test | Authentic replay uses model disagreement between risk models at observed monitoring locations; it does not localise contamination in a pipe network. |
| Fair locked baselines | **Demonstrated** | `results/authentic_locked/authentic_test_summary.csv`; policy code and audit | 41 authentic monitoring rounds, equal three-test budget: 114 SDAIF discoveries vs 80 deterministic random and 84 routine. Strongest fair model/Bayesian comparators tie SDAIF. |
| Operational impact metrics | **Demonstrated retrospectively only** | authentic event summary, paired-policy comparisons | “Confirmed results found within k tests” is measured; utility time, actuation, exposure and illness outcomes are not. |
| Understandable dashboard | **Demonstrated** | `app/templates/authentic.html`; `/api/authentic-xylem`; `/api/pilot-preflight` tests | Dashboard explains a historical monitor-site decision. It does not display a live municipal control interface. |
| Reproducible evidence | **Demonstrated** | `results/reproducibility_manifest_v1.json`; 71-test suite; submission and claim audits | Reproducibility proves identity and execution, not field effectiveness. |
| Honest pitch/application package | **Demonstrated** | `docs/XYLEM_*`; `scripts/audit_xylem_submission_pack.py` | Student-controlled upload, names, eligibility, consent, public video and team details remain outside the repository. |
| Real prospective validation | **Ready but external** | `docs/PROSPECTIVE_AUTHENTIC_PILOT_PROTOCOL.md`; `docs/PARTNER_DATA_REQUEST.md`; `src/nadi/pilot/schema.py`; preflight API | A partner must supply future independent lab results and frozen rankings. The project will reject timestamp leakage before computing a score. |

## Completion judgment

The software-first, reproducible competition deliverable is complete at its
authentic evidence boundary. The **full original field-validation objective is
not complete** because no publicly available or locally provided dataset joins
one drinking-water event's sensor/operations state, verified network nodes and
independent E. coli results. The remaining work is external data collection and
review, not an unimplemented local code feature.

## Non-negotiable final wording

> NADI retrospectively prioritised authentic surface-water monitoring locations
> with pre-round information and an equal three-test budget. It demonstrated a
> reproducible mathematical decision workflow and a separate real physical
> pressure-evidence layer. It has not yet proven municipal pipe localisation,
> direct E. coli detection, Delhi-NCR performance, avoided exposure, or illness
> reduction.
