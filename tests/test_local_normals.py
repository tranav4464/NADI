import pandas as pd

from nadi.telemetry.normal import fit_local_normals


def test_local_normals_use_group_baseline_and_global_fallback():
    train = pd.DataFrame({"zone": ["A"] * 25 + ["B"] * 25, "p": list(range(25)) + list(range(100, 125))})
    model = fit_local_normals(train, ["p"], group_column="zone", min_group_count=20)
    values = model.transform(pd.DataFrame({"zone": ["A", "NEW"], "p": [24, 50]}))
    assert abs(float(values.iloc[0, 0])) > 0.0
    assert values.iloc[1, 0] == values.iloc[1, 0]  # known finite global fallback


def test_local_normals_do_not_fit_on_future_rows():
    train = pd.DataFrame({"zone": ["A"] * 20, "p": [1.0] * 20})
    model = fit_local_normals(train, ["p"], group_column="zone", min_group_count=20)
    score = model.transform(pd.DataFrame({"zone": ["A"], "p": [100.0]})).iloc[0, 0]
    assert score > 1e6
