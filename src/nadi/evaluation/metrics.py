from __future__ import annotations


def testing_metrics(selected: list[str], affected: set[str], consequence: dict[str, float]) -> dict:
    hits = [node for node in selected if node in affected]
    first = next((index + 1 for index, node in enumerate(selected) if node in affected), None)
    total_weight = sum(consequence[node] for node in affected) or 1.0
    captured_weight = sum(consequence[node] for node in hits)
    return {
        "tests": len(selected),
        "affected_candidates": len(affected),
        "positives_found": len(hits),
        "coverage_at_k": len(hits) / len(affected) if affected else None,
        "empty_event": not affected,
        "first_affected_test_rank": first,
        "missed_positive_event": bool(affected and not hits),
        "population_weighted_coverage": captured_weight / total_weight,
    }

