from nadi.microbial_risk.lira import ecoli_presence


def test_lira_ecoli_censoring_and_presence_are_not_confused() -> None:
    assert ecoli_presence("<1") == 0
    assert ecoli_presence("1") == 1
    assert ecoli_presence("0") == 0
    assert ecoli_presence("CFU/100ml") is None
    assert ecoli_presence("") is None
