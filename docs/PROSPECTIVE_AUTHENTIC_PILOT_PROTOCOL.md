# Prospective authentic pilot protocol

## Objective

Test whether a frozen NADI ranking finds independent laboratory-confirmed high E. coli results with fewer tests than the partner's routine order.

## Minimum partner data

- pseudonymous monitoring-location identifier;
- sample collection timestamp and timezone;
- exact location or an agreed coarse spatial identifier;
- E. coli result, unit, method, detection limit, qualifier, and validity flag;
- sampling reason and programme;
- result-return timestamp if operational delay will be evaluated;
- routine sampling order or rule used by the partner.

No customer names, household addresses, pipe-control commands, or fabricated variables are required.

## Machine-checkable data contract

Before any outcome is compared, provide two UTF-8 CSV files. All timestamps
must be ISO-8601 UTC. Identifiers are pseudonymous; this protocol deliberately
does not require household data or security-sensitive control information.

`samples.csv` must contain: `pilot_round_id`, `location_id`,
`collected_at_utc`, `result_available_at_utc`, `ecoli_result`, `ecoli_unit`,
`ecoli_method`, `valid_result`, and `sampling_reason`.

`rankings.csv` must contain: `pilot_round_id`, `location_id`, `policy`,
`rank`, `information_cutoff_utc`, `ranking_frozen_at_utc`,
`risk_probability`, and `abstained`. At minimum, it must include both
`nadi_sdaif` and the partner's declared `routine` policy over the same eligible
locations in every round.

Run the fail-closed audit before analysis:

```powershell
.\.venv\Scripts\python scripts\audit_prospective_pilot_bundle.py `
  --samples samples.csv --rankings rankings.csv --endpoint-json endpoint.json
```

The audit rejects a ranking frozen after its information cutoff, any laboratory
result available before the cutoff, missing laboratory records for ranked
locations, unequal eligible-location universes, missing routine/NADI policies,
or an incomplete endpoint definition. A passing audit validates **design and
provenance**, not NADI's effectiveness.

## Pre-registration before the first pilot round

Freeze:

- biological endpoint;
- eligible locations and round definition;
- feature code and information cutoff;
- model versions and calibration method;
- SDAIF robustness weight;
- test budget;
- comparators;
- primary and secondary metrics;
- exclusions and missing-data rules;
- analysis script and random seed.

## Evaluation

For each round, every policy receives the same information available before sampling. NADI and each comparator produce an ordered list before laboratory outcomes are available. A separate custodian preserves the outcomes until rankings are timestamped.

Primary metric: confirmed positives found within the first `k` tests.

Secondary metrics:

- tests to first confirmed positive;
- missed-positive rounds;
- positive-discovery regret;
- calibration and abstention;
- turnaround time only when authentic result-return timestamps exist.

Use paired round-level confidence intervals. Publish a negative result. Do not tune the policy on the prospective outcomes.

## Safety and authority

NADI supplies research decision support only. The partner retains responsibility for sampling, laboratory methods, public communication, treatment, closure, flushing, or any protective action. The pilot must not delay routine or legally required testing.
