"""UK-DALE / REDD loader via NILMTK when available; falls back with clear error."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import h5py
import numpy as np
import pandas as pd

from .cleaning import align_aggregate_and_appliances, sliding_windows
from .config import APPLIANCES, PROCESSED_DIR, STRIDE_EVAL, STRIDE_TRAIN, WINDOW_SIZE

# Common UK-DALE appliance label aliases
ALIASES = {
    "fridge": ["fridge", "fridge freezer", "freezer"],
    "kettle": ["kettle"],
    "microwave": ["microwave"],
    "dishwasher": ["dishwasher", "dish washer"],
    "washing_machine": ["washing machine", "washer dryer", "washing_machine"],
}


def _find_channel(elec, aliases: list[str]):
    for meter in elec.meters:
        label = str(meter.appliance_label() if hasattr(meter, "appliance_label") else "").lower()
        name = " ".join(str(a.label).lower() for a in getattr(meter, "appliances", []) or [])
        text = f"{label} {name}"
        for a in aliases:
            if a in text:
                return meter
    return None


def load_ukdale_house(data_path: Path, building: int = 1) -> pd.DataFrame:
    try:
        from nilmtk import DataSet
    except ImportError as e:
        raise ImportError(
            "nilmtk is required for UK-DALE. Install nilmtk or use: "
            "python -m preprocess.generate_synthetic"
        ) from e

    ds = DataSet(str(data_path))
    elec = ds.buildings[building].elec
    mains = next(elec.mains().load(sample_period=1))
    if isinstance(mains, pd.DataFrame):
        agg = mains.iloc[:, 0]
    else:
        agg = mains
    apps = {}
    for key, aliases in ALIASES.items():
        if key not in APPLIANCES:
            continue
        meter = _find_channel(elec, aliases)
        if meter is None:
            continue
        ser = next(meter.load(sample_period=1))
        apps[key] = ser.iloc[:, 0] if isinstance(ser, pd.DataFrame) else ser
    if not apps:
        raise RuntimeError(f"No target appliances found in UK-DALE building {building}")
    return align_aggregate_and_appliances(agg, apps)


def write_from_dataframe(df: pd.DataFrame, house: str, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    agg = df["aggregate"].to_numpy(dtype=np.float32)
    n = len(agg)
    i1, i2 = int(n * 0.7), int(n * 0.85)
    splits = {
        "train": (0, i1, STRIDE_TRAIN),
        "val": (i1, i2, STRIDE_EVAL),
        "test": (i2, n, STRIDE_EVAL),
    }
    present = [a for a in APPLIANCES if a in df.columns]
    manifest = {"house": house, "window_size": WINDOW_SIZE, "appliances": present, "stats": {}, "files": {}}
    for app in present:
        target = df[app].to_numpy(dtype=np.float32)
        mean, std = float(agg[:i1].mean()), float(agg[:i1].std() + 1e-6)
        y_mean, y_std = float(target[:i1].mean()), float(target[:i1].std() + 1e-6)
        manifest["stats"][app] = {
            "agg_mean": mean,
            "agg_std": std,
            "y_mean": y_mean,
            "y_std": y_std,
        }
        for split, (a, b, stride) in splits.items():
            x, y = sliding_windows(agg[a:b], target[a:b], WINDOW_SIZE, stride)
            x = (x - mean) / std
            y = (y - y_mean) / y_std
            path = out_dir / f"{house}_{app}_{split}.h5"
            with h5py.File(path, "w") as f:
                f.create_dataset("x", data=x, compression="gzip")
                f.create_dataset("y", data=y, compression="gzip")
            manifest["files"].setdefault(app, {})[split] = str(path.relative_to(out_dir.parent.parent))
    man_path = out_dir / "dataset_manifest.json"
    man_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=Path, required=True, help="UK-DALE HDF5 path")
    parser.add_argument("--building", type=int, default=1)
    args = parser.parse_args()
    df = load_ukdale_house(args.path, args.building)
    man = write_from_dataframe(df, f"ukdale_house{args.building}", PROCESSED_DIR)
    print(json.dumps(man, indent=2))


if __name__ == "__main__":
    main()
