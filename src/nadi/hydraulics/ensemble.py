from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from ..paths import HISTORICAL_MATH_ROOT, PROCESSED_ROOT
from ..types import ReachEstimate, RiskEstimate

REFERENCE = HISTORICAL_MATH_ROOT / "wntr_reference" / "transport_reference_results.json"


@dataclass(frozen=True)
class HydraulicScenario:
    scenario_id: str
    source: str
    threshold_percent: float
    affected: frozenset[str]
    arrival_hours: dict[str, float]
    origin: str = "SIMULATED"


@dataclass(frozen=True)
class HydraulicEnsemble:
    network: str
    scenarios: tuple[HydraulicScenario, ...]
    candidates: tuple[str, ...]
    consequence_weights: dict[str, float]
    source_hash: str

    def reach_estimates(self) -> list[ReachEstimate]:
        estimates = []
        for node in self.candidates:
            hits = [s for s in self.scenarios if node in s.affected]
            arrivals = [s.arrival_hours[node] for s in hits if node in s.arrival_hours]
            estimates.append(ReachEstimate(
                node_id=node,
                probability=len(hits) / len(self.scenarios),
                earliest_hours=min(arrivals) if arrivals else None,
                latest_hours=max(arrivals) if arrivals else None,
                consequence_weight=self.consequence_weights[node],
            ))
        return estimates


def _stable_weight(node: str) -> float:
    raw = int(hashlib.sha256(f"NADI-CONSEQUENCE:{node}".encode()).hexdigest()[:8], 16)
    return 0.5 + (raw % 1501) / 1000.0


def load_reference_ensemble(candidate_count: int = 12) -> HydraulicEnsemble:
    generated = PROCESSED_ROOT / "hydraulic_ensemble.json"
    if generated.exists():
        payload = json.loads(generated.read_text(encoding="utf-8"))
        scenarios = [HydraulicScenario(
            scenario_id=row["scenario_id"], source=str(row["source"]), threshold_percent=float(payload["trace_threshold_percent"]),
            affected=frozenset(row["affected"]), arrival_hours={k: float(v) for k, v in row["first_arrival_hours"].items()}
        ) for row in payload["scenarios"]]
        source_hash = hashlib.sha256(generated.read_bytes()).hexdigest().upper()
    else:
        payload = json.loads(REFERENCE.read_text(encoding="utf-8"))
        scenarios = []
        thresholds = (0.1, 1.0, 5.0)
        for run in payload["runs"]:
            maximum = run["maximum_trace_percent"]
            first = run["first_reach_hours"]
            for threshold in thresholds:
                affected = frozenset(node for node, value in maximum.items() if float(value) >= threshold)
                arrivals = {node: float(first[node]) for node in affected if first.get(node) is not None}
                scenarios.append(HydraulicScenario(
                    scenario_id=f"source-{run['source']}-trace-{threshold:g}", source=str(run["source"]),
                    threshold_percent=threshold, affected=affected, arrival_hours=arrivals,
                ))
        source_hash = hashlib.sha256(REFERENCE.read_bytes()).hexdigest().upper()
    all_nodes = sorted(set().union(*(s.affected for s in scenarios)))
    # Nodes with the same reach signature are redundant for source
    # discrimination.  Round-robin across signatures prevents lexical ties
    # from selecting only one hydraulic branch.
    groups: dict[tuple[bool, ...], list[tuple[float, float, str]]] = {}
    for node in all_nodes:
        signature = tuple(node in scenario.affected for scenario in scenarios)
        p = sum(signature) / len(signature)
        disagreement = p * (1.0 - p)
        earliest = min((s.arrival_hours.get(node, 1e9) for s in scenarios), default=1e9)
        groups.setdefault(signature, []).append((disagreement, -earliest, node))
    ranked_groups = [
        [node for _, _, node in sorted(rows, reverse=True)]
        for signature, rows in sorted(groups.items(), key=lambda item: (-sum(item[0]), item[0]))
        if any(signature) and not all(signature)
    ]
    selected: list[str] = []
    depth = 0
    while len(selected) < candidate_count and any(depth < len(group) for group in ranked_groups):
        for group in ranked_groups:
            if depth < len(group) and len(selected) < candidate_count:
                selected.append(group[depth])
        depth += 1
    candidates = tuple(selected)
    return HydraulicEnsemble(
        network="EPA Net3 public benchmark",
        scenarios=tuple(scenarios),
        candidates=candidates,
        consequence_weights={node: _stable_weight(node) for node in candidates},
        source_hash=source_hash,
    )


def scenario_vertices(ensemble: HydraulicEnsemble, risk: RiskEstimate) -> list[dict[str, Any]]:
    vertices: list[dict[str, Any]] = []
    for probability in sorted(set([risk.lower, risk.upper])):
        for scenario in ensemble.scenarios:
            vertices.append({
                "vertex_id": f"p-{probability:.6f}:{scenario.scenario_id}",
                "risk": float(probability),
                "scenario_id": scenario.scenario_id,
                "affected": sorted(scenario.affected.intersection(ensemble.candidates)),
                "state_probability": float(probability / len(ensemble.scenarios)),
                "origin": "SIMULATED",
            })
    return vertices

