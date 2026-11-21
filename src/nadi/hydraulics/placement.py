"""Greedy placement for source discrimination in a finite hydraulic ensemble."""
from __future__ import annotations

import itertools

from .ensemble import HydraulicScenario


def greedy_source_discrimination(scenarios: tuple[HydraulicScenario, ...], budget: int) -> list[str]:
    """Cover cross-source scenario pairs with distinguishable binary reach tests.

    This is a standard greedy set-cover heuristic, not an optimality or
    novelty claim. Ties prefer larger reach variance, then node ID.
    """
    if budget < 0:
        raise ValueError("budget must be nonnegative")
    nodes = sorted(set().union(*(scenario.affected for scenario in scenarios)))
    pairs = [(i, j) for i, j in itertools.combinations(range(len(scenarios)), 2)
             if scenarios[i].source != scenarios[j].source]
    signatures = {node: tuple(node in scenario.affected for scenario in scenarios) for node in nodes}
    remaining_pairs = set(pairs)
    selected: list[str] = []
    for _ in range(min(budget, len(nodes))):
        best = None
        for node in nodes:
            if node in selected:
                continue
            signature = signatures[node]
            gain = sum(signature[i] != signature[j] for i, j in remaining_pairs)
            frequency = sum(signature) / len(signature)
            variance = frequency * (1.0 - frequency)
            # max gain; then variance; then smallest ID for determinism.
            key = (-gain, -variance, node)
            if best is None or key < best[0]:
                best = (key, node)
        if best is None:
            break
        node = best[1]
        selected.append(node)
        signature = signatures[node]
        remaining_pairs = {(i, j) for i, j in remaining_pairs if signature[i] == signature[j]}
    return selected


def distinguishable_cross_source_pairs(scenarios: tuple[HydraulicScenario, ...], nodes: list[str] | tuple[str, ...]) -> tuple[int, int]:
    pairs = [(a, b) for a, b in itertools.combinations(scenarios, 2) if a.source != b.source]
    distinguished = sum(any((node in a.affected) != (node in b.affected) for node in nodes)
                        for a, b in pairs)
    return distinguished, len(pairs)


def balanced_source_placement(scenarios: tuple[HydraulicScenario, ...], budget: int) -> list[str]:
    """Greedy cross-source discrimination with worst-scenario coverage balance.

    After a source pair is distinguished, further sensors are selected to
    increase the least-monitored hydraulic scenario, then to diversify reach
    signatures. This is a heuristic, not an optimality guarantee.
    """
    if budget < 0:
        raise ValueError("budget must be nonnegative")
    nodes = sorted(set().union(*(scenario.affected for scenario in scenarios)))
    pairs = [(i, j) for i, j in itertools.combinations(range(len(scenarios)), 2)
             if scenarios[i].source != scenarios[j].source]
    signatures = {node: tuple(node in scenario.affected for scenario in scenarios) for node in nodes}
    remaining_pairs = set(pairs)
    coverage = [0] * len(scenarios)
    selected: list[str] = []
    selected_signatures: set[tuple[bool, ...]] = set()
    for _ in range(min(budget, len(nodes))):
        best = None
        for node in nodes:
            if node in selected:
                continue
            signature = signatures[node]
            pair_gain = sum(signature[i] != signature[j] for i, j in remaining_pairs)
            new_coverage = [count + int(hit) for count, hit in zip(coverage, signature)]
            worst_scenario_gain = min(new_coverage) - min(coverage)
            unique_signature = signature not in selected_signatures
            frequency = sum(signature) / len(signature)
            variance = frequency * (1.0 - frequency)
            key = (-pair_gain, -worst_scenario_gain, -int(unique_signature),
                   -variance, -sum(signature), node)
            if best is None or key < best[0]:
                best = (key, node)
        if best is None:
            break
        node = best[1]
        selected.append(node)
        signature = signatures[node]
        selected_signatures.add(signature)
        coverage = [count + int(hit) for count, hit in zip(coverage, signature)]
        remaining_pairs = {(i, j) for i, j in remaining_pairs if signature[i] == signature[j]}
    return selected
