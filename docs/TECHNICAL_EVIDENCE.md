# NADI Technical Evidence Summary

## Decision bottleneck

When confirmatory microbiological tests are limited, NADI decides which network locations should be tested first under uncertain E. coli-referenced risk and uncertain water movement.

## Executable mathematical chain

`calibrated risk interval -> 24-scenario reach set -> consequence loss -> adaptive minimax-regret testing -> certificate or abstention`

## Frozen evidence

- Surface-water endpoint: `Surface-water E. coli context model; not direct sensor detection and not drinking-network validation`
- Forecast untouched test: n=4186, ROC AUC=0.652, AP=0.456, ECE=0.123.
- Geographic audit: 30 unseen sites, n=1313, ROC AUC=0.584, ECE=0.054.
- Hydraulics: 24 EPANET/WNTR TRACE scenarios with source, demand, tank and pipe-state uncertainty. These are simulated benchmark scenarios, not pathogen concentrations or a city twin.
- Locked benchmark (V5 no-placeholder policy set): 76 nonempty simulated events (44 empty events excluded from affected-node coverage); SDAIF Coverage@3=0.615; strongest fair baseline `adaptive_bayesian`=0.615.
- Result: `PASS` for equivalence margin 0.02. Superiority supported: `False`.
- Bristol operational telemetry and local-normal audit: 209,584 five-minute records, seven channels, no event or biological labels; evidence is proxy-only.
- Location adaptation uses training-only robust median/MAD baselines with sparse-group global fallback; see `src/nadi/telemetry/normal.py`.
- SDAIF component ablations and the complete non-biological domain coverage map are maintained in `docs/SDAIF_ABLATION_EVIDENCE.md` and `docs/NON_BIOLOGICAL_COVERAGE_MATRIX.md`.

## Interpretation

SDAIF matches the strongest fair sequential comparator. The initial regret bound applies only to the enumerated risk and hydraulic scenarios; it is not a real-world safety guarantee. The frozen benchmark does **not** establish superiority, direct E. coli detection, Delhi-NCR performance, field validation, or prevented illness.

## Traceability

- Benchmark config SHA-256: `B868A1A537E8AC946BDBEF8533F80C014E3BC5728C2A85DDFBB413C01352580B`
- Event table SHA-256: `F83E889A2D9A4CCC7EBE3C7F8AE14A8C49A7B501709853059DB9B82E24C68016`
- Aggregate SHA-256: `2EE61579D9BCA4C596A39F68245DC0CDD8706AAA0987447870D8933A1FA05A18`
- Hydraulic network SHA-256: `EA3E825C4FEF0B5CBA47FB06301BC85253F18B6364DC96C44D9FB492C40FAA52`
