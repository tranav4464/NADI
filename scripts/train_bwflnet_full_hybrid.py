"""Train and evaluate a physics plus data BWFLnet state-estimation model.

The experiment uses only the publisher's 24-hour training folder for model
selection and fitting. The separate one-week folder is evaluated once at the
end. It predicts measured hydraulic states, not microorganisms.
"""
from __future__ import annotations

import json
import warnings
import zipfile
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import wntr
from sklearn.base import clone
from sklearn.cross_decomposition import PLSRegression
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import TimeSeriesSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "external" / "bwflnet"
OUT = ROOT / "results" / "bwflnet_full_hybrid"

ROUGHNESS_VARIANTS = {
    "dw_initial": ("D-W", "DW_initial [mm]"),
    "dw_nongrouped": ("D-W", "DW_nongrouped [mm]"),
    "dw_grouped": ("D-W", "DW_grouped [mm]"),
    "hw_initial": ("H-W", "HW_initial"),
    "hw_nongrouped": ("H-W", "HW_nongrouped"),
    "hw_grouped": ("H-W", "HW_grouped"),
}


def run_variant(name: str, formula: str, column: str, properties: pd.DataFrame):
    model = wntr.network.WaterNetworkModel(str(DATA / "BWFLnet.inp"))
    model.options.hydraulic.headloss = formula
    values = properties.set_index("link_name")[column]
    for pipe_name in model.pipe_name_list:
        if pipe_name in values.index and np.isfinite(values.loc[pipe_name]):
            value = float(values.loc[pipe_name])
            model.get_link(pipe_name).roughness = value / 1000.0 if formula == "D-W" else value
    result = wntr.sim.EpanetSimulator(model).run_sim()
    return model, result.node["pressure"], result.link["flowrate"] * 1000.0


def read_measurements(archive: zipfile.ZipFile, sensors: pd.DataFrame, phase: str):
    folder = "24hr_training_data" if phase == "train" else "week_validation_data"
    frames = []
    for _, row in sensors.iterrows():
        sid = str(row.Logger_ID)
        path = f"15min/{folder}/{sid}.csv"
        if path not in archive.namelist():
            continue
        frame = pd.read_csv(archive.open(path))
        value_col = "q_mean" if "Flow" in row.Data_Type else "p_mean"
        frame = frame[["timestamp", value_col]].rename(columns={value_col: sid})
        frame["timestamp"] = pd.to_datetime(frame.timestamp, format="%d-%b-%Y %H:%M:%S")
        frames.append(frame.set_index("timestamp"))
    return pd.concat(frames, axis=1).sort_index()


def clock_seconds(index: pd.DatetimeIndex) -> np.ndarray:
    return (index.hour * 3600 + index.minute * 60 + index.second).to_numpy()


def sample_physics(index, sensors, pressure, flow):
    seconds = clock_seconds(index)
    output = {}
    for _, row in sensors.iterrows():
        sid, element = str(row.Logger_ID), str(row["Node/Link"])
        table = flow if "Flow" in row.Data_Type else pressure
        if element in table.columns:
            output[sid] = pd.Series(seconds, index=index).map(table[element]).to_numpy()
    return pd.DataFrame(output, index=index)


def normalized_mae(observed, predicted, scale):
    return float(np.nanmean(np.abs(observed - predicted) / scale))


def test_metrics(observed, predicted):
    good = np.isfinite(observed) & np.isfinite(predicted)
    y, p = observed[good], predicted[good]
    error = y - p
    denom = np.sum((y - np.mean(y)) ** 2)
    return {
        "n": int(good.sum()),
        "mae": float(np.mean(np.abs(error))),
        "rmse": float(np.sqrt(np.mean(error**2))),
        "bias": float(np.mean(error)),
        "r2": float(1 - np.sum(error**2) / denom) if denom > 0 else None,
    }


def make_features(measured, physical, boundary, medians=None):
    index = measured.index
    x = pd.DataFrame(index=index)
    for col in boundary:
        x[f"boundary__{col}"] = measured[col]
    for col in physical.columns:
        x[f"physics__{col}"] = physical[col]
    phase = clock_seconds(index) / 86400.0
    for harmonic in range(1, 5):
        x[f"sin_{harmonic}"] = np.sin(2 * np.pi * harmonic * phase)
        x[f"cos_{harmonic}"] = np.cos(2 * np.pi * harmonic * phase)
    if medians is None:
        medians = x.median()
    return x.fillna(medians), medians


def select_estimator(x, residual, scale):
    candidates = {
        "ridge_0.1": make_pipeline(StandardScaler(), Ridge(alpha=0.1)),
        "ridge_1": make_pipeline(StandardScaler(), Ridge(alpha=1.0)),
        "ridge_10": make_pipeline(StandardScaler(), Ridge(alpha=10.0)),
        "ridge_100": make_pipeline(StandardScaler(), Ridge(alpha=100.0)),
        "pls_2": make_pipeline(StandardScaler(), PLSRegression(n_components=2, scale=False, max_iter=1000)),
        "pls_5": make_pipeline(StandardScaler(), PLSRegression(n_components=5, scale=False, max_iter=1000)),
        "pls_10": make_pipeline(StandardScaler(), PLSRegression(n_components=10, scale=False, max_iter=1000)),
        "extra_trees_2": ExtraTreesRegressor(n_estimators=400, min_samples_leaf=2, max_features=0.8, random_state=17, n_jobs=-1),
        "extra_trees_5": ExtraTreesRegressor(n_estimators=400, min_samples_leaf=5, max_features=0.8, random_state=17, n_jobs=-1),
        "random_forest_2": RandomForestRegressor(n_estimators=400, min_samples_leaf=2, max_features=0.8, random_state=17, n_jobs=-1),
    }
    folds = TimeSeriesSplit(n_splits=4)
    scores = {}
    for name, estimator in candidates.items():
        fold_scores = []
        for train_idx, valid_idx in folds.split(x):
            fitted = clone(estimator).fit(x.iloc[train_idx], residual.iloc[train_idx])
            pred = np.asarray(fitted.predict(x.iloc[valid_idx]))
            fold_scores.append(normalized_mae(residual.iloc[valid_idx].to_numpy(), pred, scale))
        scores[name] = float(np.mean(fold_scores))
    selected = min(scores, key=scores.get)
    chosen = candidates[selected]
    oof = np.full(residual.shape, np.nan, dtype=float)
    for train_idx, valid_idx in folds.split(x):
        fitted = clone(chosen).fit(x.iloc[train_idx], residual.iloc[train_idx])
        oof[valid_idx] = np.asarray(fitted.predict(x.iloc[valid_idx]))
    return selected, chosen.fit(x, residual), scores, oof


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    properties = pd.read_csv(DATA / "link_properties.csv")
    with zipfile.ZipFile(DATA / "data.zip") as archive:
        sensors = pd.read_csv(archive.open("sensor_info.csv"))
        train = read_measurements(archive, sensors, "train")
        test = read_measurements(archive, sensors, "test")

    variants = {}
    for name, (formula, column) in ROUGHNESS_VARIANTS.items():
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            network, pressure, flow = run_variant(name, formula, column, properties)
        variants[name] = {
            "train": sample_physics(train.index, sensors, pressure, flow),
            "test": sample_physics(test.index, sensors, pressure, flow),
        }

    common = [c for c in train if c in next(iter(variants.values()))["train"]]
    scale = train[common].std().replace(0, 1).fillna(1).to_numpy()
    variant_scores = {}
    for name, tables in variants.items():
        variant_scores[name] = normalized_mae(
            train[common].to_numpy(), tables["train"][common].to_numpy(), scale
        )
    selected_variant = min(variant_scores, key=variant_scores.get)
    physical_train = variants[selected_variant]["train"]
    physical_test = variants[selected_variant]["test"]

    pressure_ids = sensors.loc[sensors.Data_Type.str.contains("Pressure"), "Logger_ID"].tolist()
    flow_ids = sensors.loc[sensors.Data_Type.str.contains("Flow"), "Logger_ID"].tolist()
    boundary = [c for c in train.columns if c.startswith(tuple(f"Logger_0{i}" for i in range(1, 6)))]
    boundary += [c for c in train.columns if c == "Logger_33"]
    internal_pressure = [c for c in pressure_ids if c not in boundary and c in train and c in physical_train]

    x_train, medians = make_features(train, physical_train[internal_pressure], boundary)
    x_test, _ = make_features(test, physical_test[internal_pressure], boundary, medians)
    usable_train = train[internal_pressure].notna().all(axis=1)
    y_train = train.loc[usable_train, internal_pressure]
    residual_train = y_train - physical_train.loc[usable_train, internal_pressure]
    target_scale = y_train.std().replace(0, 1).fillna(1).to_numpy()
    selected_model, estimator, cv_scores, oof_residual = select_estimator(
        x_train.loc[usable_train], residual_train, target_scale
    )
    hybrid_test = physical_test[internal_pressure] + np.asarray(estimator.predict(x_test))
    hybrid_test = pd.DataFrame(hybrid_test, index=test.index, columns=internal_pressure)
    oof_error = residual_train.to_numpy() - oof_residual
    interval_half_width = np.nanquantile(np.abs(oof_error), 0.90, axis=0)
    interval_half_width = np.where(np.isfinite(interval_half_width), interval_half_width, 0.0)

    per_logger = []
    for sid in common:
        y_train_sid = train[sid].dropna()
        y_test_sid = test[sid].to_numpy()
        raw = physical_test[sid].to_numpy()
        aligned_train_physical = physical_train.loc[y_train_sid.index, sid]
        offset = float((y_train_sid - aligned_train_physical).mean())
        mean = float(y_train_sid.mean())
        methods = {
            "raw_physics": raw,
            "constant_offset": raw + offset,
            "training_mean": np.full(len(raw), mean),
        }
        if sid in internal_pressure:
            methods["hybrid_state_estimator"] = hybrid_test[sid].to_numpy()
        record = {
            "logger": sid,
            "type": "flow" if sid in flow_ids else "pressure",
            "element": sensors.set_index("Logger_ID").loc[sid, "Node/Link"],
            "metrics": {method: test_metrics(y_test_sid, pred) for method, pred in methods.items()},
        }
        per_logger.append(record)

    summary = {}
    for kind in ("pressure", "flow"):
        group = [r for r in per_logger if r["type"] == kind]
        methods = sorted({m for r in group for m in r["metrics"]})
        summary[kind] = {
            "logger_count": len(group),
            "median_logger_mae": {
                method: float(np.median([r["metrics"][method]["mae"] for r in group if method in r["metrics"]]))
                for method in methods
            },
            "unit": "m water" if kind == "pressure" else "L/s",
        }
    internal_records = [r for r in per_logger if r["logger"] in internal_pressure]
    internal_y = test[internal_pressure].to_numpy()
    internal_pred = hybrid_test.to_numpy()
    internal_good = np.isfinite(internal_y) & np.isfinite(internal_pred)
    interval_good = internal_good & (
        internal_y >= internal_pred - interval_half_width
    ) & (
        internal_y <= internal_pred + interval_half_width
    )
    summary["internal_pressure"] = {
        "logger_count": len(internal_records),
        "median_logger_mae": {
            method: float(np.median([r["metrics"][method]["mae"] for r in internal_records]))
            for method in ("raw_physics", "constant_offset", "training_mean", "hybrid_state_estimator")
        },
        "hybrid_beats_training_mean_loggers": int(sum(
            r["metrics"]["hybrid_state_estimator"]["mae"] < r["metrics"]["training_mean"]["mae"]
            for r in internal_records
        )),
        "aggregate_hybrid_metrics": test_metrics(internal_y.ravel(), internal_pred.ravel()),
        "nominal_interval": 0.90,
        "empirical_interval_coverage": float(interval_good.sum() / internal_good.sum()),
        "median_interval_half_width_m": float(np.median(interval_half_width)),
        "unit": "m water",
    }

    joblib.dump({
        "roughness_variant": selected_variant,
        "estimator_name": selected_model,
        "estimator": estimator,
        "feature_columns": list(x_train.columns),
        "feature_medians": medians,
        "target_loggers": internal_pressure,
        "boundary_loggers": boundary,
        "interval_half_width_m": dict(zip(internal_pressure, interval_half_width.tolist())),
    }, OUT / "bwflnet_hybrid_model.joblib")
    report = {
        "protocol": {
            "training": "Published 15-minute 24-hour training day, 2018-06-06",
            "testing": "Published separate 15-minute validation week, 2018-06-10 through 2018-06-16",
            "selection": "Roughness variant and estimator selected using training data only; estimator uses four expanding-window CV folds",
            "scope": "Hydraulic state estimation at monitored nodes; no microbial or contaminant-transport labels",
            "prior_test_disclosure": "A simple offset baseline was inspected on this validation week before this enhanced protocol; this is held-out evaluation but no longer a pristine untouched test.",
        },
        "network": {"nodes": network.num_nodes, "links": network.num_links},
        "selected_roughness_variant": selected_variant,
        "roughness_training_scores_normalized_mae": variant_scores,
        "selected_hybrid_estimator": selected_model,
        "hybrid_training_cv_normalized_mae": cv_scores,
        "training_rows": int(len(train)),
        "test_rows": int(len(test)),
        "summary": summary,
        "per_logger": per_logger,
    }
    (OUT / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    pd.DataFrame([
        {"logger": r["logger"], "type": r["type"], "element": r["element"], **{
            f"{method}_mae": values["mae"] for method, values in r["metrics"].items()
        }} for r in per_logger
    ]).to_csv(OUT / "per_logger_metrics.csv", index=False)
    prediction_rows = []
    for sid_idx, sid in enumerate(internal_pressure):
        frame = pd.DataFrame({
            "timestamp": test.index,
            "logger": sid,
            "observed_pressure_m": test[sid].to_numpy(),
            "physics_pressure_m": physical_test[sid].to_numpy(),
            "hybrid_pressure_m": hybrid_test[sid].to_numpy(),
            "interval_lower_m": hybrid_test[sid].to_numpy() - interval_half_width[sid_idx],
            "interval_upper_m": hybrid_test[sid].to_numpy() + interval_half_width[sid_idx],
        })
        prediction_rows.append(frame)
    pd.concat(prediction_rows, ignore_index=True).to_csv(OUT / "heldout_predictions.csv", index=False)
    print(json.dumps({
        "selected_roughness_variant": selected_variant,
        "selected_hybrid_estimator": selected_model,
        "summary": summary,
    }, indent=2))


if __name__ == "__main__":
    main()
