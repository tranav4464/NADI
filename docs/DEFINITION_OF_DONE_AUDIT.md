# Definition-of-done audit

Audited against `nadi_xylem_2026_plan/11_END_TO_END_GOAL_AND_EXECUTION_PLAN.md`
after the final local reproduction run. “Demonstrated” means supported by a
current executable artefact; “simulated” means valid only inside the declared
benchmark; “external” means it requires a utility, laboratory or independent
reviewer.

| Requirement | Status | Evidence |
|---|---|---|
| Scripted resource verification and deterministic preparation | Demonstrated | `scripts/reproduce.ps1`, CLI audit/prepare commands |
| Provenance, checksums, licences and exclusions | Demonstrated | `provenance/resource_manifest.json`, `results/reproducibility_manifest_v1.json` |
| Reproducible E. coli-referenced model with uncertainty | Demonstrated in source domain | `data_processed/risk_model_card.json`, risk-model tests; surface-water context only |
| Honest nowcast and forecast modes | Demonstrated | temporal split and leakage tests; declared endpoint/horizon |
| Geographic/domain transfer, inflation and abstention | Demonstrated in stress tests | geographic audit, transfer gate, unsupported-domain dashboard test |
| EPANET/WNTR affected-region ensembles | Demonstrated in simulation | `data_processed/hydraulic_ensemble.json`, locked V5 scenarios |
| Fair common comparator interface | Demonstrated | V5 no-placeholder policy set and benchmark tests |
| Adaptive SDAIF with regret, delay and evidence value | Demonstrated in simulation | engine, delayed tests, V5 benchmark, ablations |
| Locked event-level no-leakage evaluation | Demonstrated | V5 summary/events/aggregate and claim audit |
| Working dashboard driven by model outputs | Demonstrated | Flask dashboard, `/api/latest`, `/api/benchmark`, `/api/evidence` |
| Replication pack, mathematical report, negative-results log and claim matrix | Demonstrated | `docs/`, `logs/protocol_deviations.md`, evidence pack |
| Two-minute pitch, demo and jury defence tied to evidence | Demonstrated as artefacts | `docs/XYLEM_2MIN_PITCH.md`, `docs/XYLEM_EVIDENCE_PACK.md` |

## Requirements not established by software alone

The following remain deliberately external and are not silently converted into
simulation claims:

- independently paired intermittent drinking-water sensor and microbiology;
- calibrated Delhi/Ghaziabad topology, valve states and demand operations;
- prospective utility event/response comparison;
- independent clean-environment reproduction and mathematical/water-network
  review;
- direct E. coli detection, reduced illness or prevented exposure.

Therefore the project is locally reproducible and competition-demonstrable, but
not field-validated. The correct submission claim is a software-first applied
mathematical decision prototype with a bounded pilot pathway.
