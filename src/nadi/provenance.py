from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from .paths import PACKAGE_ROOT, RESOURCE_ROOT


@dataclass(frozen=True)
class ResourceRecord:
    resource_id: str
    local_path: str
    sha256: str | None
    bytes: int | None
    origin: str
    domain: str
    allowed_inference: str
    prohibited_inference: str
    evidence_kind: str
    version: str | None = None


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _repo_commit(path: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(path), "rev-parse", "HEAD"], text=True
    ).strip()


def core_resources() -> list[ResourceRecord]:
    d = RESOURCE_ROOT / "datasets"
    r = RESOURCE_ROOT / "repositories"
    records = [
        ResourceRecord("WQP_MARION_ECOLI", str(d / "WQP_Marion_IN_Ecoli_2003_2022" / "wqp_marion_in_ecoli_2003_2022.zip"), None, None, "US Water Quality Portal frozen query", "SURFACE_WATER_CONTEXT", "E. coli-referenced model reconstruction", "drinking-network validation", "LAB_CONFIRMED"),
        ResourceRecord("WQP_MARION_STATIONS", str(d / "WQP_Marion_IN_Ecoli_2003_2022" / "wqp_marion_in_ecoli_stations_2003_2022.zip"), None, None, "US Water Quality Portal frozen query", "SURFACE_WATER_CONTEXT", "monitoring-location metadata", "utility topology", "OBSERVED"),
        ResourceRecord("NOAA_INDIANAPOLIS", str(d / "NOAA_Indianapolis_GHCND" / "USW00093819.csv.gz"), None, None, "NOAA GHCN-D", "WEATHER", "past-only weather covariates", "microbial truth", "OBSERVED"),
        ResourceRecord("BANGLADESH_MICS", str(d / "existing_verified" / "replication_data.sav"), None, None, "Bangladesh MICS/Figshare replication snapshot", "HOUSEHOLD_DRINKING_WATER", "household/source drinking-water transfer stress", "pipe-network localisation", "LAB_CONFIRMED"),
        ResourceRecord("WDSEVENTDB", str(d / "existing_verified" / "WDSEventDB_zenodo_17547955.zip"), None, None, "WDSEventDB Zenodo record 17547955", "PHYSICAL_TESTBED", "telemetry/event ingestion", "E. coli detection", "OBSERVED"),
        ResourceRecord("BATTLEDIM_LTOWN", str(d / "BattLeDIM_4017659" / "L-TOWN.inp"), None, None, "BattLeDIM Zenodo record 4017659", "SIMULATED_NETWORK", "hydraulic/anomaly benchmark", "field validation", "SIMULATED"),
        ResourceRecord("GECCO_2019_TRAIN", str(d / "GECCO" / "gecco2019_train_water_quality.csv"), None, None, "GECCO/Zenodo record 4304080", "INDUSTRIAL_WATER_PROCESS", "anomaly benchmark", "microbial truth", "OBSERVED"),
        ResourceRecord("EA_ECOLI_2024", str(d / "EA_ECOLI_AUTHENTIC" / "ea_ecoli_confirmed_mf_2024.csv"), None, None, "Environment Agency official observation API", "SURFACE_WATER_CONTEXT", "E. coli surface-water replication", "Delhi-NCR drinking-network validation", "LAB_CONFIRMED"),
        ResourceRecord("EA_ECOLI_PHYSCHEM_PANEL_Q1_2024", str(d / "EA_ECOLI_AUTHENTIC" / "ea_ecoli_physchem_panel_q1_2024.csv"), None, None, "Environment Agency official observation API, sample-URI join", "SURFACE_WATER_CONTEXT", "sample-matched physicochemical benchmark", "direct sensor detection and drinking-network validation", "LAB_CONFIRMED"),
        ResourceRecord("EA_OPENMETEO_WEATHER_PANEL_Q1_2024", str(d / "EA_ECOLI_AUTHENTIC" / "ea_openmeteo_weather_panel_q1_2024.csv"), None, None, "Open-Meteo historical weather API, coordinates transformed from EA sampling points", "WEATHER", "past-only weather covariates", "microbial truth", "OBSERVED"),
        ResourceRecord("BRISTOL_POU_TELEMETRY", str(d / "Bristol_POU_Telemetry" / "extracted" / "data" / "pou-dwts_operationaltelemetrydata_uk_nov2019-sep2022_1.csv"), None, None, "Bristol operational telemetry archive", "OPERATIONAL_TELEMETRY", "regime/anomaly evidence", "microbial truth", "OBSERVED"),
    ]
    for key, folder, origin, domain in [
        ("EPANET", "EPANET2.2", "USEPA GitHub", "SOFTWARE"),
        ("WNTR", "WNTR", "USEPA GitHub", "SOFTWARE"),
        ("OPEN_ECOLI_MODELS", "Open-Ecoli-Models", "Cognizant RDMAI GitHub", "SURFACE_WATER_CONTEXT"),
        ("WATER_BENCHMARK_HUB", "WaterBenchmarkHub", "WaterFutures GitHub", "SIMULATED_NETWORK"),
    ]:
        path = r / folder
        records.append(ResourceRecord(key, str(path), None, None, origin, domain, "method/software replication", "new empirical validation", "MODEL_ESTIMATE", _repo_commit(path)))
    complete = []
    for item in records:
        path = Path(item.local_path)
        complete.append(ResourceRecord(
            **{**asdict(item), "sha256": sha256(path) if path.is_file() else None,
               "bytes": path.stat().st_size if path.is_file() else None}
        ))
    return complete


def freeze_manifest() -> dict:
    records = core_resources()
    payload = {
        "schema_version": "0.1.0",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "records": [asdict(record) for record in records],
    }
    target = PACKAGE_ROOT / "provenance" / "resource_manifest.json"
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def audit_manifest() -> dict:
    manifest_path = PACKAGE_ROOT / "provenance" / "resource_manifest.json"
    if not manifest_path.exists():
        freeze_manifest()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    checks = []
    for record in manifest["records"]:
        path = Path(record["local_path"])
        exists = path.exists()
        hash_ok = True
        version_ok = True
        if exists and path.is_file() and record["sha256"]:
            hash_ok = sha256(path) == record["sha256"]
        if exists and path.is_dir() and record.get("version"):
            version_ok = _repo_commit(path) == record["version"]
        checks.append({"resource_id": record["resource_id"], "exists": exists, "hash_ok": hash_ok, "version_ok": version_ok})
    return {"passed": all(x["exists"] and x["hash_ok"] and x["version_ok"] for x in checks), "checks": checks}

