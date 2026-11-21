from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

import numpy as np
import wntr

from ..paths import INTERIM_ROOT, PROCESSED_ROOT, RESOURCE_ROOT

NETWORK = RESOURCE_ROOT / "repositories" / "WNTR" / "examples" / "networks" / "Net3.inp"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _simulate(
    source: str, demand_multiplier: float, tank_fraction: float,
    closed_pipe: str | None, label_override: str | None = None,
    network: Path = NETWORK,
) -> dict:
    model = wntr.network.WaterNetworkModel(str(network))
    model.options.time.duration = 24 * 3600
    model.options.time.report_timestep = 3600
    # Pressure-dependent demand avoids the physically impossible implication
    # that every requested demand is delivered even when pressure collapses.
    # These values are explicit modelling assumptions for the public benchmark,
    # not calibrated utility parameters.
    model.options.hydraulic.demand_model = "PDA"
    model.options.hydraulic.minimum_pressure = 0.0
    model.options.hydraulic.required_pressure = 20.0
    model.options.hydraulic.pressure_exponent = 0.5
    model.options.quality.parameter = "TRACE"
    model.options.quality.trace_node = source
    for junction in model.junctions():
        for demand in junction[1].demand_timeseries_list:
            demand.base_value *= demand_multiplier
    for _, tank in model.tanks():
        span = tank.max_level - tank.min_level
        tank.init_level = tank.min_level + tank_fraction * span
    if closed_pipe:
        model.get_link(closed_pipe).initial_status = wntr.network.LinkStatus.Closed
    run_dir = INTERIM_ROOT / "hydraulic_runs"
    run_dir.mkdir(parents=True, exist_ok=True)
    label = label_override or f"src-{source}_d-{demand_multiplier:.1f}_tank-{tank_fraction:.1f}_close-{closed_pipe or 'none'}"
    result = wntr.sim.EpanetSimulator(model).run_sim(file_prefix=str(run_dir / label))
    quality = result.node["quality"]
    pressure = result.node["pressure"][model.junction_name_list]
    if not np.isfinite(quality.to_numpy()).all() or not np.isfinite(pressure.to_numpy()).all():
        raise ValueError(f"Nonfinite hydraulic result: {label}")
    first, maximum = {}, {}
    for node in model.junction_name_list:
        values = quality[node]
        crossing = values[values >= 1.0]
        first[node] = None if crossing.empty else float(crossing.index[0]) / 3600.0
        maximum[node] = float(values.max())
    return {
        "scenario_id": label,
        "source": source,
        "demand_multiplier": demand_multiplier,
        "tank_initial_fraction": tank_fraction,
        "closed_pipe": closed_pipe,
        "affected": sorted(node for node, value in maximum.items() if value >= 1.0),
        "first_arrival_hours": {node: value for node, value in first.items() if value is not None},
        "minimum_pressure_m": float(pressure.min().min()),
        "negative_pressure_node_count": int((pressure < 0).any().sum()),
        "mass_trace_sanity": {"minimum_percent": float(quality.min().min()), "maximum_percent": float(quality.max().max())},
        "origin": "SIMULATED",
    }


def generate() -> dict:
    scenarios = []
    for source, demand, tank, closed in itertools.product(
        ("101", "151"), (0.8, 1.2), (0.35, 0.75), (None, "103", "107")
    ):
        scenarios.append(_simulate(source, demand, tank, closed))
    output = {
        "schema_version": "0.1.0",
        "network": "EPA Net3 public benchmark",
        "network_sha256": _sha(NETWORK),
        "wntr_version": wntr.__version__,
        "trace_threshold_percent": 1.0,
        "scenario_count": len(scenarios),
        "varied_factors": ["source", "demand_multiplier", "tank_initial_fraction", "closed_pipe"],
        "hydraulic_demand_model": {
            "type": "PDA",
            "minimum_pressure_m": 0.0,
            "required_pressure_m": 20.0,
            "pressure_exponent": 0.5,
            "status": "benchmark assumption; not field calibrated",
        },
        "scenarios": scenarios,
        "interpretation": "TRACE source-contribution ensemble under simulated operating uncertainty; not pathogen concentration or field validation",
    }
    target = PROCESSED_ROOT / "hydraulic_ensemble.json"
    target.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    return {"scenario_count": len(scenarios), "output": str(target), "network_sha256": output["network_sha256"]}

