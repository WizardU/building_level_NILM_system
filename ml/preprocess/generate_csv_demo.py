"""Generate synthetic CSV demo data compatible with the legacy NILM pipeline.

This is adapted from the Nilm.rar reference implementation. It produces:
  - data/csv_demo/mains.csv
  - data/csv_demo/appliances/<appliance>.csv
  - data/csv_demo/meta.json

Sampling interval is 6 seconds (UK-DALE low-frequency style) and window length
is 99 points, matching the original reference code.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from .config import APPLIANCES, ON_THRESHOLDS

SEED = 42
SAMPLE_SEC = 6
DAYS = 30
START = "2025-09-01"
DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "csv_demo"

# Nominal operating power for each appliance (annotation only)
NOMINAL_POWER = {
    "fridge": 140,
    "kettle": 1800,
    "microwave": 1100,
    "dishwasher": 900,
    "washing_machine": 500,
}

T = DAYS * 86400 // SAMPLE_SEC
rng = np.random.default_rng(SEED)


def _place(power: np.ndarray, start_sec: int, dur_sec: int, watts: float) -> None:
    i0 = start_sec // SAMPLE_SEC
    i1 = min(i0 + max(dur_sec // SAMPLE_SEC, 1), T)
    if i0 < T:
        power[i0:i1] = watts


def add_kettle(power: np.ndarray) -> None:
    for day in range(DAYS):
        for _ in range(rng.integers(2, 6)):
            hour = int(rng.choice([7, 8, 12, 13, 17, 18, 19, 20, 21]))
            start = day * 86400 + hour * 3600 + int(rng.integers(0, 3600))
            _place(power, start, int(rng.integers(90, 300)), 1800.0)


def add_microwave(power: np.ndarray) -> None:
    for day in range(DAYS):
        for _ in range(rng.integers(1, 4)):
            hour = int(rng.choice([7, 11, 12, 17, 18, 19, 20]))
            start = day * 86400 + hour * 3600 + int(rng.integers(0, 3600))
            _place(power, start, int(rng.integers(40, 180)), 1100.0)


def add_dishwasher(power: np.ndarray) -> None:
    phases = [(120, 100.0), (720, 800.0), (120, 200.0), (360, 500.0), (240, 900.0)]
    for day in range(DAYS):
        if rng.random() < 0.5:
            continue
        cursor = day * 86400 + int(rng.integers(10, 20)) * 3600 + int(rng.integers(0, 3600))
        for dur, watts in phases:
            _place(power, cursor, dur, watts)
            cursor += dur


def add_washing_machine(power: np.ndarray) -> None:
    phases = [(120, 100.0), (720, 800.0), (120, 200.0), (360, 500.0), (240, 900.0)]
    for day in range(DAYS):
        runs = int(rng.integers(1, 3)) if rng.random() < 0.8 else 0
        for _ in range(runs):
            cursor = day * 86400 + int(rng.integers(8, 20)) * 3600 + int(rng.integers(0, 3600))
            for dur, watts in phases:
                _place(power, cursor, dur, watts)
                cursor += dur


def add_fridge(power: np.ndarray) -> None:
    cursor = 0
    while cursor < T:
        on = int(rng.integers(600, 1081)) // SAMPLE_SEC
        off = int(rng.integers(1500, 2701)) // SAMPLE_SEC
        power[cursor:min(cursor + on, T)] = 140.0
        cursor += on + off


def main() -> None:
    builders = {
        "kettle": add_kettle,
        "microwave": add_microwave,
        "dishwasher": add_dishwasher,
        "washing_machine": add_washing_machine,
        "fridge": add_fridge,
    }
    appliance_powers = {}
    for name in APPLIANCES:
        p = np.zeros(T)
        builders[name](p)
        appliance_powers[name] = p

    base = np.clip(90 + np.cumsum(rng.normal(0, 1.5, T)), 50, 160)
    mains = base + sum(appliance_powers.values()) + rng.normal(0, 4, T)
    mains = np.clip(mains, 0, None)

    idx = pd.date_range(START, periods=T, freq=f"{SAMPLE_SEC}s")
    (DATA_DIR / "appliances").mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"time": idx, "mains": mains.round(1)}).to_csv(DATA_DIR / "mains.csv", index=False)
    for name, p in appliance_powers.items():
        pd.DataFrame({"time": idx, "power": p}).to_csv(DATA_DIR / "appliances" / f"{name}.csv", index=False)

    meta = {
        "sample_sec": SAMPLE_SEC,
        "days": DAYS,
        "start": START,
        "appliances": {
            name: {"on_threshold": ON_THRESHOLDS[name], "nominal_power": NOMINAL_POWER[name]}
            for name in APPLIANCES
        },
    }
    (DATA_DIR / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    print(f"Generated CSV demo data -> {DATA_DIR}")
    print(f"mains.csv: {T} rows, mean {mains.mean():.0f} W")
    for name, p in appliance_powers.items():
        energy = p.sum() * SAMPLE_SEC / 3.6e6
        print(f"  {name:16s} on-ratio {(p > 0).mean():.2f}  energy {energy:.1f} kWh")


if __name__ == "__main__":
    main()
