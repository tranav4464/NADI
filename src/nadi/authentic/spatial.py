from __future__ import annotations

import numpy as np
import pandas as pd


def assign_monitoring_zones(
    frame: pd.DataFrame,
    probabilities: np.ndarray,
    threshold: float,
    maximum_link_km: float = 25.0,
) -> pd.DataFrame:
    """Connect authentic high-risk monitoring sites by observed coordinates.

    The result is a monitoring zone, not a pipe route or causal transport path.
    """
    output = frame.copy().reset_index(drop=True)
    output["predicted_probability"] = np.asarray(probabilities, dtype=float)
    output["predicted_high_risk"] = output["predicted_probability"] >= float(threshold)
    output["monitoring_zone_id"] = "NOT_HIGH_RISK"
    for round_id, group in output[output["predicted_high_risk"]].groupby("round_id", sort=True):
        indices = group.index.tolist()
        adjacency = {index: set() for index in indices}
        for position, left in enumerate(indices):
            for right in indices[position + 1:]:
                dx = float(output.loc[left, "easting_km"] - output.loc[right, "easting_km"])
                dy = float(output.loc[left, "northing_km"] - output.loc[right, "northing_km"])
                if np.hypot(dx, dy) <= maximum_link_km:
                    adjacency[left].add(right)
                    adjacency[right].add(left)
        unvisited = set(indices)
        component = 0
        while unvisited:
            component += 1
            stack = [min(unvisited)]
            members = []
            while stack:
                node = stack.pop()
                if node not in unvisited:
                    continue
                unvisited.remove(node)
                members.append(node)
                stack.extend(adjacency[node].intersection(unvisited))
            output.loc[members, "monitoring_zone_id"] = f"{round_id}-Z{component:02d}"
    output["zone_claim"] = "MODEL_ESTIMATED_MONITORING_ZONE_NOT_PIPELINE_ROUTE"
    return output
