# NADI partner data request — bounded pilot

## Purpose

NADI is a student research prototype asking whether a frozen mathematical
ranking can prioritise independent confirmatory *E. coli* testing better than
a partner's existing routine order. It is **not** a drinking-water control
system and will not direct treatment, public communication, isolation, flushing
or any other utility action.

## Minimum request

For one small pressure zone or monitoring programme, please provide a future
set of anonymised records, after any required institutional approval:

1. **Laboratory samples:** pseudonymous location ID; collection time in UTC;
   result-return time in UTC; *E. coli* value; unit; method; detection limit;
   qualifier; validity flag; sampling reason.
2. **Eligible locations per round:** pseudonymous IDs only. No customer names,
   household addresses or precise public-facing coordinates are needed.
3. **Routine comparator:** the normal testing order or an explicit routine
   rule for each round.
4. **Pre-decision operational context where available:** coarse supply
   start/stop/restart state, pressure/flow/residual-chlorine aggregates, and
   an anonymised source/tank/zone identifier. Missing fields are permitted and
   will be declared rather than fabricated.

Optional, only if policy permits: a connectivity-only pseudonymous node/pipe
graph and coarse valve/source-state flags. NADI does not require consumer data
or security-sensitive SCADA commands.

## What the partner receives

- A timestamped NADI ranking and the declared routine ranking before results
  are unblinded.
- A public, reproducible analysis of: positives within the first `k` tests,
  tests to first confirmed positive, missed-positive rounds, abstentions and
  uncertainty.
- All negative and inconclusive results reported.
- A de-identified evidence bundle; the partner controls whether any result is
  publicly released.

## Safeguards

- NADI never delays statutory, routine or emergency sampling.
- A separate custodian retains laboratory outcomes until rankings are frozen.
- NADI does not claim direct *E. coli* detection from ordinary sensors.
- A passing data preflight validates timestamps and provenance only; it does
  not validate a model or authorise operational action.
- The utility/laboratory retains all responsibility for sample collection,
  methods, public-health decisions and data governance.

## Send-ready message

> Subject: Bounded anonymised water-monitoring data request for supervised
> student research
>
> Dear Sir/Madam, I am developing NADI, a supervised student applied-
> mathematics project that evaluates whether limited confirmatory *E. coli*
> tests can be prioritised more efficiently. We request data for one small
> future pilot area only: anonymised location IDs, sample collection and
> result-return times, *E. coli* results with method/QC fields, the normal
> routine sampling order, and—if available—coarse supply state or aggregated
> pressure/flow/chlorine context. We do not require names, household addresses,
> customer records, raw control commands or city-wide topology. All results
> would be treated as research decision support and independently reviewed
> before any public claim. We can provide the full protocol and data schema in
> advance. Thank you for considering this educational research request.

## Before transfer

Run the supplied preflight after filling the two CSV files:

```powershell
.\.venv\Scripts\python scripts\audit_prospective_pilot_bundle.py `
  --samples samples.csv --rankings rankings.csv --endpoint-json endpoint.json
```

See `docs/PROSPECTIVE_AUTHENTIC_PILOT_PROTOCOL.md` for the exact schema and
leakage checks.
