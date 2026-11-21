from nadi.hazards.intrusion import estimate_intrusion_hazard


def test_intrusion_hazard_is_monotone_for_pressure_and_sewage_proximity():
    near = estimate_intrusion_hazard({"min_pressure": 0.2, "sewage_distance_m": 5, "pipe_defect": 1, "intermittent_restart": 1})
    far = estimate_intrusion_hazard({"min_pressure": 0.8, "sewage_distance_m": 100, "pipe_defect": 1, "intermittent_restart": 1})
    assert near.score > far.score


def test_intrusion_hazard_widens_and_abstains_with_insufficient_context():
    result = estimate_intrusion_hazard({"min_pressure": 0.3})
    assert result.abstain
    assert result.upper >= result.lower


def test_location_adaptive_z_inputs_replace_raw_thresholds_monotonically():
    low = estimate_intrusion_hazard({"pressure_low_z": -3, "chlorine_drop_z": 2, "turbidity_spike_z": 2})
    normal = estimate_intrusion_hazard({"pressure_low_z": 0, "chlorine_drop_z": 0, "turbidity_spike_z": 0})
    assert low.score > normal.score
