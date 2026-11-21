from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / "nadi_resources" / "datasets" / "EPA_DISTRIBUTION_WATER_2023_2024" / "scihub_Dis_Water_2324_dataset_V2.xlsx"
OUTPUT = ROOT / "results" / "epa_distribution_water_2023_2024_audit.json"


def main() -> dict:
    raw = pd.read_excel(SOURCE, sheet_name=" scihub Final", header=1)
    raw["collection_date"] = pd.to_datetime(raw["Water Collection Date"], errors="coerce", format="mixed")
    data = raw[raw["collection_date"].notna()].copy()
    ecoli = pd.to_numeric(data["Colilert-E.coli"], errors="coerce")
    total_coliform = pd.to_numeric(data["Colilert"], errors="coerce")
    result = {
        "dataset": "EPA_DISTRIBUTION_WATER_2023_2024",
        "data_origin": "AUTHENTIC_OBSERVED",
        "source_url": "https://pasteur.epa.gov/uploads/10.23719/d-hsdm/scihub_Dis_Water_2324_dataset_V2.xlsx",
        "source_path": str(SOURCE.resolve()),
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "records": int(len(data)),
        "date_range": [str(data["collection_date"].min().date()), str(data["collection_date"].max().date())],
        "utilities": int(data["Utility Designation"].nunique()),
        "location_categories": sorted(data["Location"].dropna().astype(str).unique()),
        "ecoli_nonmissing": int(ecoli.notna().sum()),
        "ecoli_positive_records": int((ecoli > 0).sum()),
        "total_coliform_nonmissing": int(total_coliform.notna().sum()),
        "total_coliform_positive_records": int((total_coliform > 0).sum()),
        "available_water_quality_fields": [
            field for field in [
                "pH ", "Temperature", "Nitrite", "Utility Total Chlorine",
                "Utility Free Chlorine", "Researcher Total Chlorine",
                "Researcher Free Chlorine", "Free Ammonia", "Hardness",
                "Disolved Oxygen", "HPC ", "Colilert", "Colilert-E.coli",
            ] if field in data.columns
        ],
        "model_gate": "NOT_SUITABLE_FOR_E_COLI_CLASSIFIER_TRAINING",
        "gate_reason": "No positive E. coli record is present, so discrimination and sensitivity cannot be estimated.",
        "usable_role": "Authentic drinking-water domain and prevalence audit; not a topology, forecasting, or branch-localisation dataset.",
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    main()
