# EPA authentic distribution-water dataset audit

The U.S. EPA 2023–2024 distribution-water workbook materially improves the domain evidence because it contains authentic microbial, disinfectant, physicochemical, metals, and disinfection-byproduct measurements collected within public water-system distribution networks.

It does not close NADI's network-level evidence gap.

## Findings

- 144 dated authentic records;
- multiple public-water-system utilities and distribution location categories;
- measured chlorine, temperature, pH, ammonia, hardness, dissolved oxygen, HPC, total coliform, and E. coli fields;
- no positive E. coli record among the 144 dated samples;
- no machine-readable pipe topology, valve state, demand, flow direction, or matched downstream route outcome.

## Decision

Do not train or score an E. coli classifier on this workbook. With no positive record, sensitivity, F1, PR-AUC, and transfer performance cannot be estimated. Use the dataset to document authentic drinking-water prevalence and domain differences only.

The scored NADI model therefore remains the authentic surface-water monitoring experiment, with its domain boundary stated explicitly. The EPA workbook supports the conclusion that a public, positive-rich, topology-linked drinking-water dataset remains unavailable.

## Reproduction

Run:

```powershell
.\.venv_clean\Scripts\python.exe scripts/audit_epa_distribution_water.py
```

Machine-readable result: `results/epa_distribution_water_2023_2024_audit.json`.
