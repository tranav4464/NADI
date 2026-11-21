"""Add hashes for authentic datasets and acquired prior-art repositories."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "provenance" / "resource_manifest.json"


def digest(path: Path) -> tuple[str, int]:
    h = hashlib.sha256()
    total = 0
    if path.is_file():
        with path.open("rb") as f:
            for block in iter(lambda: f.read(1024 * 1024), b""):
                h.update(block)
                total += len(block)
        return h.hexdigest().upper(), total
    entries = sorted(p for p in path.rglob("*") if p.is_file())
    for p in entries:
        rel = p.relative_to(path).as_posix().encode()
        h.update(rel + b"\0")
        with p.open("rb") as f:
            for block in iter(lambda: f.read(1024 * 1024), b""):
                h.update(block)
                total += len(block)
    return h.hexdigest().upper(), total


def main() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    records = {r["resource_id"]: r for r in data.get("records", [])}
    additions = [
        ("EA_ECOLI_2024", ROOT.parent / "nadi_resources/datasets/EA_ECOLI_AUTHENTIC/ea_ecoli_confirmed_mf_2024.csv", "Environment Agency official observation API", "SURFACE_WATER_CONTEXT", "LAB_CONFIRMED", "E. coli surface-water replication", "Delhi-NCR drinking-network validation"),
        ("EA_ECOLI_PHYSCHEM_PANEL_Q1_2024", ROOT.parent / "nadi_resources/datasets/EA_ECOLI_AUTHENTIC/ea_ecoli_physchem_panel_q1_2024.csv", "Environment Agency official observation API, sample-URI join", "SURFACE_WATER_CONTEXT", "LAB_CONFIRMED", "sample-matched physicochemical benchmark", "direct sensor detection and drinking-network validation"),
        ("BRISTOL_POU_TELEMETRY", ROOT.parent / "nadi_resources/datasets/Bristol_POU_Telemetry/extracted/data/pou-dwts_operationaltelemetrydata_uk_nov2019-sep2022_1.csv", "Bristol operational telemetry archive", "OPERATIONAL_TELEMETRY", "OBSERVED", "regime/anomaly evidence", "microbial truth"),
        ("OPEN_ECOLI_MODELS_SNAPSHOT", ROOT.parent / "nadi_resources/prior_art/Open-Ecoli-Models", "Cognizant RDMAI GitHub commit 4bca9807a0b62ee83df97d68b52430a3b1cda3b9", "SOFTWARE", "MODEL_ESTIMATE", "prior-art method reproduction", "published performance equivalence"),
        ("WNTR_SNAPSHOT", ROOT.parent / "nadi_resources/prior_art/WNTR", "USEPA GitHub commit 39e6b34f37d4b2d074f107d822752c989bf108aa", "SOFTWARE", "MODEL_ESTIMATE", "hydraulic computation", "field validation"),
        ("EPANET_SNAPSHOT", ROOT.parent / "nadi_resources/prior_art/EPANET2.2", "USEPA GitHub commit 598ee6cd214de07a0d62e7dafc1bdbf09173645a", "SOFTWARE", "MODEL_ESTIMATE", "hydraulic/water-quality computation", "field validation"),
        ("LIRA_PIPED_WATER", ROOT.parent / "nadi_resources/datasets/NADI_NETWORK_PRIORITY_2026_11_19/lira_uganda_mendeley_jv6drgtvzc/extracted/A water quality dataset of physicochemical, microb/Water Quality dataset Final.xlsx", "Mendeley Data jv6drgtvzc.1", "DRINKING_WATER_CROSS_SECTION", "LAB_CONFIRMED", "piped-water E. coli endpoint/chemistry transfer stress", "pipeline localisation, forecasting, or downstream response"),
        ("SLOVAK_UTILITY_LEAKS", ROOT.parent / "nadi_resources/datasets/NADI_NETWORK_PRIORITY_2026_11_19/slovak_utility_zenodo_15096167", "Zenodo 15096167", "UTILITY_OPERATIONS", "OBSERVED", "operational-anomaly and documented-leak evidence", "microbial or E. coli detection"),
        ("CITY_D_LEAK_RECORDS", ROOT.parent / "nadi_resources/datasets/NADI_NETWORK_PRIORITY_2026_11_19/city_d_field_leaks", "wdsgpu City D open leak-record release", "UTILITY_OPERATIONS", "OBSERVED", "pipe-failure prior and source-hypothesis evidence", "microbial or contamination-response outcome"),
        ("TEXAS_PHYSICAL_PIPE_TESTBED", ROOT.parent / "nadi_resources/datasets/NADI_NETWORK_PRIORITY_2026_11_19/texas_physical_pipe_testbed_tbrnp6vrnj/texas_pipe_leak_benchmark.zip", "Mendeley Data tbrnp6vrnj.1", "PHYSICAL_TESTBED", "OBSERVED", "controlled physical pressure/leak validation", "E. coli detection or municipal field validation"),
        ("IITB_FLOW_STARVED_MODEL", ROOT.parent / "nadi_resources/datasets/NADI_NETWORK_PRIORITY_2026_11_19/iitb_flow_starved_zenodo_7162154/Supplementry information-2.rar", "Zenodo 7162154", "INTERMITTENT_HYDRAULIC_MODEL", "MODEL_ESTIMATE", "India-relevant hydraulic structure", "observed contamination or field validation"),
    ]
    for rid, path, origin, domain, kind, allowed, prohibited in additions:
        if not path.exists():
            continue
        sha, size = digest(path)
        records[rid] = {"resource_id": rid, "local_path": str(path), "sha256": sha, "bytes": size, "origin": origin, "domain": domain, "allowed_inference": allowed, "prohibited_inference": prohibited, "evidence_kind": kind}
    data["records"] = list(records.values())
    data["generated_utc"] = datetime.now(timezone.utc).isoformat()
    MANIFEST.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(data["records"]), "added_or_updated": [x[0] for x in additions]}, indent=2))


if __name__ == "__main__":
    main()
