# NADI Technical Evidence Summary

## Decision bottleneck

When confirmatory microbiological tests are limited, NADI decides which network locations should be tested first under uncertain E. coli-referenced risk and uncertain water movement.

## Executable mathematical chain

`calibrated risk interval -> 24-scenario reach set -> consequence loss -> adaptive minimax-regret testing -> certificate or abstention`

## Frozen evidence

- Surface-water endpoint: `Surface-water E. coli context model; not direct sensor detection and not drinking-network validation`
- Forecast untouched test: n=4186, ROC AUC=0.652, AP=0.456, ECE=0.123.
- Geographic audit: 30 unseen sites, n=1313, ROC AUC=0.606, ECE=0.054.
- Hydraulics: 24 EPANET/WNTR TRACE scenarios with source, demand, tank and pipe-state uncertainty. These are simulated benchmark scenarios, not pathogen concentrations or a city twin.
- Locked V3: 120 events; SDAIF Coverage@3=0.686; strongest fair baseline `adaptive_bayesian`=0.686.
- Result: `PASS` for equivalence margin 0.02. Superiority supported: `False`.

## Interpretation

SDAIF matches the strongest fair sequential comparator and adds a worst-case regret certificate, an adversarial witness, abstention, and the value of each next test. The frozen benchmark does **not** establish superiority, direct E. coli detection, Delhi-NCR performance, field validation, or prevented illness.

## Traceability

- Benchmark config SHA-256: `2CA1F47F26D6B66A555BF84D0EC02E2BD4CCB25CC74AC590C8053327804773F5`
- Event table SHA-256: `0186FC8D8BFAE3D6DCC447C6F2576E2CA5FE12204F14F0940596436A88005042`
- Aggregate SHA-256: `8A415B7160B1AE647355EA7AAD796190200656CEBEF9B392F278F3CF32F4C4DA`
- Hydraulic network SHA-256: `EA3E825C4FEF0B5CBA47FB06301BC85253F18B6364DC96C44D9FB492C40FAA52`
