"""Run small authentic-data prior-art replications and record exact status."""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT.parent / "nadi_resources"
OUT = ROOT / "results" / "authentic_prior_art_replication_v1.json"


def main() -> dict:
    result = {"replication_id": "NADI-AUTHENTIC-PRIOR-ART-SMOKE-V1", "generated_utc": datetime.now(timezone.utc).isoformat(), "tracks": {}}
    # Real BattLeDIM network/SCADA assets are already used by NADI's leakage
    # and localisation scripts; verify a WNTR hydraulic run independently.
    try:
        import wntr
        inp = RES / "datasets" / "BattLeDIM_4017659" / "L-TOWN.inp"
        wn = wntr.network.WaterNetworkModel(str(inp))
        sim = wntr.sim.EpanetSimulator(wn)
        outputs = sim.run_sim()
        result["tracks"]["battledim_wntr"] = {
            "status": "REPRODUCED_SMOKE",
            "network": "L-TOWN.inp",
            "junctions": len(wn.junction_name_list),
            "pipes": len(wn.pipe_name_list),
            "pressure_rows": int(outputs.node["pressure"].shape[0]),
            "claim_boundary": "Real benchmark network and SCADA context; leak/tracer task, not E. coli.",
        }
    except Exception as exc:
        result["tracks"]["battledim_wntr"] = {"status": "FAILED", "error": repr(exc)}
    # The Open E. coli repository is authentic source code, but its notebooks
    # require external EA/NRW/SEPA files not shipped in the repository. Verify
    # that dependency boundary explicitly instead of fabricating a run.
    repo = RES / "prior_art" / "Open-Ecoli-Models"
    req = repo / "requirements.txt"
    notebooks = sorted(repo.glob("*.ipynb"))
    result["tracks"]["open_ecoli_models"] = {
        "status": "INPUT_DATA_REQUIRED",
        "notebook_count": len(notebooks),
        "requirements_present": req.exists(),
        "required_external_sources": ["Environment Agency", "Natural Resources Wales", "SEPA", "Open-Meteo", "CORINE", "MODIS"],
        "claim_boundary": "Authentic prior-art workflow identified; no performance claim until source files are acquired and executed.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    main()
