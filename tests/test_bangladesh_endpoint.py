from nadi.microbial_risk.bangladesh import binary_ecoli


def test_raw_source_and_household_endpoints_use_valid_mics_codes():
    assert binary_ecoli(0) == 0
    assert binary_ecoli(1) == 1
    assert binary_ecoli(100) == 1
    assert binary_ecoli(101) == 1  # Censored as >100, still positive.
    assert binary_ecoli(991) is None
    assert binary_ecoli(992) is None
    assert binary_ecoli(None) is None
