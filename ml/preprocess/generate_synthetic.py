"""Generate synthetic building power traces when UK-DALE is unavailable."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import h5py
import numpy as np

from .cleaning import sliding_windows
from .config import (
    APPLIANCES,
    PROCESSED_DIR,
    STRIDE_EVAL,
    STRIDE_TRAIN,
    SYNTH_PROFILES,
    WINDOW_SIZE,
)


def _fridge(n: int, rng: np.random.Generator, p: dict) -> np.ndarray:
    out = np.zeros(n, dtype=np.float32)
    t = 0
    while t < n:
        on = p["cycle_on"]
        off = p["cycle_off"]
        out[t : min(t + on, n)] = p["on_power"] + rng.normal(0, 5, min(on, n - t))
        t += on + off
    return np.clip(out, 0, None)


def _bursts(n: int, rng: np.random.Generator, p: dict, days: int) -> np.ndarray:
    out = np.zeros(n, dtype=np.float32)
    day_len = 86400
    for d in range(days):
        for _ in range(p["bursts_per_day"]):
            start = d * day_len + int(rng.integers(0, day_len - p["burst_len"]))
            end = min(start + p["burst_len"], n)
            out[start:end] = p["on_power"] + rng.normal(0, 20, end - start)
    return np.clip(out, 0, None)


def generate_house(days: int = 7, seed: int = 42) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    n = days * 86400
    apps = {}
    for name in APPLIANCES:
        p = SYNTH_PROFILES[name]
        if name == "fridge":
            apps[name] = _fridge(n, rng, p)
        else:
            apps[name] = _bursts(n, rng, p, days)
    base = 80.0 + rng.normal(0, 5, n).astype(np.float32)
    aggregate = base + sum(apps.values())
    apps["aggregate"] = np.clip(aggregate, 0, None)
    return apps


def write_windows(
    series: dict[str, np.ndarray],
    out_dir: Path,
    house: str = "synth_house1",
) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    agg = series["aggregate"]
    n = len(agg)
    # 70/15/15 split by time
    i1, i2 = int(n * 0.7), int(n * 0.85)
    splits = {
        "train": (0, i1, STRIDE_TRAIN),
        "val": (i1, i2, STRIDE_EVAL),
        "test": (i2, n, STRIDE_EVAL),
    }
    manifest = {
        "house": house,
        "window_size": WINDOW_SIZE,
        "appliances": APPLIANCES,
        "stats": {},
        "files": {},
    }
    for app in APPLIANCES:
        mean = float(agg[:i1].mean())
        std = float(agg[:i1].std() + 1e-6)
        y_mean = float(series[app][:i1].mean())
        y_std = float(series[app][:i1].std() + 1e-6)
        manifest["stats"][app] = {
            "agg_mean": mean,
            "agg_std": std,
            "y_mean": y_mean,
            "y_std": y_std,
        }
        for split, (a, b, stride) in splits.items():
            x, y = sliding_windows(agg[a:b], series[app][a:b], WINDOW_SIZE, stride)
            x = (x - mean) / std
            y = (y - y_mean) / y_std
            path = out_dir / f"{house}_{app}_{split}.h5"
            with h5py.File(path, "w") as f:
                f.create_dataset("x", data=x, compression="gzip")
                f.create_dataset("y", data=y, compression="gzip")
            manifest["files"].setdefault(app, {})[split] = str(path.relative_to(out_dir.parent.parent))
    # Also dump raw 1Hz CSV sample for replay (first day)
    replay_dir = out_dir / "replay"
    replay_dir.mkdir(exist_ok=True)
    day = min(86400, n)
    replay_path = replay_dir / f"{house}_day1.npz"
    np.savez_compressed(
        replay_path,
        aggregate=agg[:day],
        **{k: series[k][:day] for k in APPLIANCES},
    )
    manifest["replay"] = str(replay_path.relative_to(out_dir.parent.parent))
    man_path = out_dir / "dataset_manifest.json"
    man_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic NILM windows")
    parser.add_argument("--days", type=int, default=3)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    series = generate_house(days=args.days, seed=args.seed)
    man = write_windows(series, PROCESSED_DIR)
    print(f"Wrote manifest → {PROCESSED_DIR / 'dataset_manifest.json'}")
    print(f"Appliances: {man['appliances']}")


if __name__ == "__main__":
    main()
