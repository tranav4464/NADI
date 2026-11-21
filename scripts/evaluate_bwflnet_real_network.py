"""Evaluate the published BWFLnet hydraulic model against held-out field loggers.

No microbiological or contaminant labels are present in this dataset.
"""
from __future__ import annotations

import json
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import wntr


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "external" / "bwflnet"
OUTPUT = ROOT / "results" / "bwflnet_real_network_validation.json"


def metrics(y: np.ndarray, p: np.ndarray) -> dict:
    good = np.isfinite(y) & np.isfinite(p)
    e = y[good] - p[good]
    return {
        "n": int(good.sum()),
        "mae": float(np.mean(np.abs(e))),
        "rmse": float(np.sqrt(np.mean(e * e))),
        "bias_observed_minus_predicted": float(np.mean(e)),
    }


def main() -> None:
    network = wntr.network.WaterNetworkModel(str(SOURCE / "BWFLnet.inp"))
    results = wntr.sim.EpanetSimulator(network).run_sim()
    pressure = results.node["pressure"]
    flow = results.link["flowrate"] * 1000.0  # m3/s to L/s
    with zipfile.ZipFile(SOURCE / "data.zip") as archive:
        sensors = pd.read_csv(archive.open("sensor_info.csv"))
        rows = []
        for _, sensor in sensors.iterrows():
            sid = str(sensor["Logger_ID"])
            kind = "flow" if "Flow" in sensor["Data_Type"] else "pressure"
            element = sensor["Node/Link"]
            simulated = flow if kind == "flow" else pressure
            if element not in simulated.columns:
                continue
            parts = {}
            for phase, folder in (("train", "24hr_training_data"), ("test", "week_validation_data")):
                name = f"15min/{folder}/{sid}.csv"
                if name not in archive.namelist():
                    break
                frame = pd.read_csv(archive.open(name))
                column = "q_mean" if kind == "flow" else "p_mean"
                frame["timestamp"] = pd.to_datetime(frame["timestamp"], format="%d-%b-%Y %H:%M:%S")
                frame["clock_seconds"] = (
                    frame["timestamp"].dt.hour * 3600 + frame["timestamp"].dt.minute * 60
                )
                curve = simulated[element]
                frame["physical"] = frame["clock_seconds"].map(curve)
                parts[phase] = frame[[column, "physical"]].rename(columns={column: "observed"})
            if len(parts) != 2:
                continue
            train, test = parts["train"], parts["test"]
            train_valid = train.dropna()
            test_valid = test.dropna()
            if len(train_valid) < 20 or len(test_valid) < 20:
                continue
            offset = float((train_valid.observed - train_valid.physical).mean())
            constant = float(train_valid.observed.mean())
            y = test_valid.observed.to_numpy()
            p = test_valid.physical.to_numpy()
            rows.append({
                "logger": sid, "type": kind, "element": element,
                "training_records": len(train_valid), "test_records": len(test_valid),
                "train_offset": offset,
                "uncalibrated": metrics(y, p),
                "calibrated_offset": metrics(y, p + offset),
                "training_mean_baseline": metrics(y, np.full_like(y, constant)),
            })
    summary = {}
    for kind in ("pressure", "flow"):
        group = [r for r in rows if r["type"] == kind]
        summary[kind] = {
            "logger_count": len(group),
            "median_logger_mae": {
                method: float(np.median([r[method]["mae"] for r in group])) if group else None
                for method in ("uncalibrated", "calibrated_offset", "training_mean_baseline")
            },
            "unit": "m water" if kind == "pressure" else "L/s",
        }
    report = {
        "source": "Waldron, Pecci, Stoianov, BWFLnet + data, doi:10.17632/srt4vr5k38.3",
        "data_origin": "real field hydraulic measurements; published network model",
        "train": "15min/24hr_training_data (June 6, 2018)",
        "test": "15min/week_validation_data (June 10-16, 2018)",
        "simulation_use": "EPANET produces hydraulic predictions from published network; measured logger values are held-out truth",
        "biological_claim": "None; no E. coli data are paired with this network",
        "network_nodes": network.num_nodes,
        "network_links": network.num_links,
        "summary": summary,
        "loggers": rows,
    }
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
