"""Independent L-TOWN transport smoke test; retains synthetic reach labels."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import wntr


def run(network: Path, output: Path) -> dict:
    model = wntr.network.WaterNetworkModel(str(network))
    model.options.time.duration = 24 * 3600
    model.options.time.report_timestep = 3600
    model.options.hydraulic.demand_model = "PDA"
    model.options.hydraulic.minimum_pressure = 0.0
    model.options.hydraulic.required_pressure = 20.0
    model.options.hydraulic.pressure_exponent = 0.5
    model.options.quality.parameter = "TRACE"
    model.options.quality.trace_node = model.reservoir_name_list[0]
    scratch = Path("data_interim") / "second_network"
    scratch.mkdir(parents=True, exist_ok=True)
    prefix = scratch / "ltown_trace"
    result = wntr.sim.EpanetSimulator(model).run_sim(file_prefix=str(prefix))
    quality = result.node["quality"]
    pressure = result.node["pressure"]
    values = quality[model.junction_name_list].to_numpy()
    if not np.isfinite(values).all() or not np.isfinite(pressure.to_numpy()).all():
        raise ValueError("L-TOWN trace produced nonfinite values")
    affected = (values >= 1.0).any(axis=0)
    output_data = {
        "network": "BattLeDIM L-TOWN",
        "network_sha256": hashlib.sha256(network.read_bytes()).hexdigest().upper(),
        "wntr_version": wntr.__version__,
        "source": model.options.quality.trace_node,
        "junction_count": len(model.junction_name_list),
        "pipe_count": len(model.pipe_name_list),
        "affected_junctions_1pct_trace": int(affected.sum()),
        "minimum_pressure_m": float(pressure.min().min()),
        "origin": "SIMULATED",
        "boundary": "One 24-hour trace smoke test on a second public network; no E. coli, calibrated field transport, or decision comparison",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(output_data, indent=2) + "\n", encoding="utf-8")
    return output_data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--network", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("results/second_network_ltown.json"))
    args = parser.parse_args()
    print(json.dumps(run(args.network, args.output), indent=2))


if __name__ == "__main__":
    main()
