"""Independent L-TOWN reach ensemble from prespecified hydraulic factors."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path

import wntr

from nadi.hydraulics.generate import _simulate


def run(network: Path, output: Path) -> dict:
    scenarios = []
    for source, demand, tank in itertools.product(("R1", "R2"), (0.8, 1.2), (0.35, 0.75)):
        scenarios.append(_simulate(source, demand, tank, None,
                                   label_override=f"ltown-src-{source}-d-{demand}-t-{tank}",
                                   network=network))
    result = {
        "network": "BattLeDIM L-TOWN",
        "network_sha256": hashlib.sha256(network.read_bytes()).hexdigest().upper(),
        "wntr_version": wntr.__version__,
        "trace_threshold_percent": 1.0,
        "scenario_count": len(scenarios),
        "varied_factors": ["reservoir_source", "demand_multiplier", "tank_initial_fraction"],
        "origin": "SIMULATED",
        "scenarios": scenarios,
        "interpretation": "Independent-network source-tracing demonstration; no E. coli or field validation",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return {"output": str(output), "scenario_count": len(scenarios)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--network", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("data_processed/ltown_hydraulic_ensemble.json"))
    args = parser.parse_args()
    print(json.dumps(run(args.network, args.output)))


if __name__ == "__main__":
    main()
