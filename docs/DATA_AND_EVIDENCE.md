# Data and Evidence Policy

NADI uses public and research datasets with different licences, purposes and
evidence strengths. Raw third-party datasets are not committed to this public
repository unless redistribution is explicitly permitted and necessary.

## What is included

- acquisition and preprocessing scripts;
- dataset and resource manifests;
- hashes and provenance metadata where available;
- schema and integrity tests;
- canonical configurations;
- canonical derived tables and model bundles required by the public test suite;
- structured, non-sensitive result summaries;
- figures and reports generated from declared artifacts.

## What is excluded

- local Python environments and caches;
- raw third-party datasets in `data/external/`;
- temporary hydraulic solver files;
- redundant distribution archives;
- credentials, API keys and machine-local paths where avoidable.

## Recreating data

Use the scripts under `scripts/acquisition/` and the dataset-specific download
scripts in `scripts/`. Verify downloaded files against
`provenance/resource_manifest.json` and the manifests under `data/manifests/`.
Some datasets require their original provider's terms or download workflow.

## Evidence labels

NADI uses the following labels throughout its reports and interfaces:

- `LAB_CONFIRMED`: accepted microbiological result in the source dataset;
- `OBSERVED`: recorded contextual, telemetry, weather or network input;
- `MODEL_ESTIMATE`: output produced by a fitted model;
- `SIMULATED`: constructed network scenario or hidden benchmark truth;
- `RECONSTRUCTED`: state inferred from observed boundary measurements;
- `ASSUMED`: scenario input not independently observed;
- `HISTORICAL`: retained non-canonical artifact;
- `CURRENT_CANONICAL`: current guarded result or configuration.

These labels prevent hydraulic feasibility, simulation and biological evidence
from being conflated.
