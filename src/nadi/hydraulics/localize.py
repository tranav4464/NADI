"""Source consistency under the enumerated hydraulic scenario ensemble."""
from __future__ import annotations

from .ensemble import HydraulicEnsemble


def source_consistency(ensemble: HydraulicEnsemble, observed: dict[str, bool]) -> dict:
    """Return source support among scenarios matching revealed tracer tests.

    Scenario fractions are conditional on a uniform *enumerated* scenario
    count. They are not calibrated probabilities of a real contamination source.
    """
    unknown_nodes = set(observed).difference(ensemble.candidates)
    if unknown_nodes:
        return {"status": "INVALID_NODE", "unknown_nodes": sorted(unknown_nodes),
                "ranked_sources": [], "compatible_scenarios": 0}
    matching = [scenario for scenario in ensemble.scenarios
                if all((node in scenario.affected) == result for node, result in observed.items())]
    if not matching:
        return {"status": "OUT_OF_MODEL", "ranked_sources": [],
                "compatible_scenarios": 0, "certificate_valid": False,
                "unknown_source_not_excluded": True,
                "unique_among_enumerated": False}
    counts: dict[str, int] = {}
    for scenario in matching:
        counts[scenario.source] = counts.get(scenario.source, 0) + 1
    ranked = [{"source": source, "scenario_count": count,
               "scenario_fraction": count / len(matching)}
              for source, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))]
    return {"status": "IN_MODEL", "ranked_sources": ranked,
            "compatible_scenarios": len(matching),
            "certificate_valid": False,
            "unique_among_enumerated": len(ranked) == 1,
            "unknown_source_not_excluded": True,
            "interpretation": "Rank among enumerated tracer sources only; unmodelled sources remain possible and no biological source probability is estimated"}
