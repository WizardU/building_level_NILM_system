"""UK-DALE loader: read the official NILMTK HDF5 directly (no NILMTK needed).

The UKERC EDC release stores one HDF5 file with ``building{N}/elec/meter{M}``
groups. Each group holds a ``time`` dataset (UNIX epoch, usually nanoseconds)
and a ``power`` dataset (watts). Channel numbers are documented in the UK-DALE
ReadMe and mirrored in :mod:`preprocess.config` (``UKDALE_CHANNELS``).

Usage::

    python -m preprocess.ukdale --h5 data/raw/ukdale.h5 --house 1
    python -m preprocess.ukdale --h5 data/raw/ukdale.h5 --house 2 \
        --start 2013-03-01 --end 2013-09-01 --sample-period 1
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import h5py
import numpy as np
import pandas as pd

try:  # UK-DALE's HDF5 uses the Blosc filter, which needs hdf5plugin.
    import hdf5plugin  # noqa: F401
except ImportError:  # pragma: no cover - optional dependency
    hdf5plugin = None

from .cleaning import clean_power, sliding_windows
from .config import (
    APPLIANCES,
    ON_THRESHOLDS,
    PROCESSED_DIR,
    ROOT,
    SAMPLE_PERIOD_S,
    STRIDE_EVAL,
    STRIDE_TRAIN,
    UKDALE_CHANNELS,
    UKDALE_DEFAULT_RANGE,
    WINDOW_SIZE,
)


def _time_unit(values: np.ndarray) -> str:
    if values.size == 0:
        return "s"
    peak = float(np.nanmax(values))
    if peak > 1e17:
        return "ns"
    if peak > 1e14:
        return "us"
    if peak > 1e11:
        return "ms"
    return "s"


def _power_key(group: h5py.Group) -> str:
    for key in ("power", "active", "apparent"):
        if key in group:
            return key
    raise KeyError(f"no power dataset in {group.name}: {list(group.keys())}")


def _read_channel(
    h5: h5py.File,
    house: int,
    meter: int,
    start: pd.Timestamp | None = None,
    end: pd.Timestamp | None = None,
) -> pd.Series:
    path = f"building{house}/elec/meter{meter}"
    if path not in h5:
        raise KeyError(f"{path} not found in {h5.filename}")
    group = h5[path]

    if "table" in group:
        # NILMTK / PyTables layout: compound dataset with an int64 ``index``
        # (pandas datetime64[ns]) and one or more float value blocks.
        table = group["table"]
        raw_time = table["index"][:]
        unit = _time_unit(raw_time)
        time_index = pd.to_datetime(raw_time.astype("int64"), unit=unit, utc=True)
        i0, i1 = 0, len(time_index)
        if start is not None:
            i0 = int(time_index.searchsorted(start))
        if end is not None:
            i1 = int(time_index.searchsorted(end))
        if i1 <= i0:
            raise ValueError(f"{path}: empty range {start} .. {end}")
        block = table["values_block_0"][i0:i1]
        power = block[:, 0] if getattr(block, "ndim", 1) > 1 else block
    else:
        raw_time = group["time"][:]
        unit = _time_unit(raw_time)
        time_index = pd.to_datetime(raw_time.astype("int64"), unit=unit, utc=True)
        i0, i1 = 0, len(time_index)
        if start is not None:
            i0 = int(time_index.searchsorted(start))
        if end is not None:
            i1 = int(time_index.searchsorted(end))
        if i1 <= i0:
            raise ValueError(f"{path}: empty range {start} .. {end}")
        power = group[_power_key(group)][i0:i1]

    series = pd.Series(np.asarray(power, dtype="float64"), index=time_index[i0:i1])
    return series[~series.index.duplicated(keep="last")].sort_index()


def load_ukdale_house(
    h5_path: str | Path,
    house: int = 1,
    start: str | pd.Timestamp | None = None,
    end: str | pd.Timestamp | None = None,
    sample_period_s: int = SAMPLE_PERIOD_S,
    appliances: list[str] | None = None,
) -> pd.DataFrame:
    """Return a gap-free ``aggregate + appliances`` frame on a regular grid."""
    if house not in UKDALE_CHANNELS:
        raise SystemExit(f"House {house} has no channel mapping; add it to UKDALE_CHANNELS")
    channels = UKDALE_CHANNELS[house]
    start_ts = pd.Timestamp(start, tz="UTC") if start else None
    end_ts = pd.Timestamp(end, tz="UTC") if end else None
    wanted = appliances or APPLIANCES

    with h5py.File(h5_path, "r") as h5:
        aggregate = _read_channel(h5, house, channels["aggregate"], start_ts, end_ts)
        aggregate = clean_power(
            aggregate, period_s=sample_period_s, is_aggregate=True
        )
        frame = {"aggregate": aggregate}
        for appliance in wanted:
            if appliance not in channels:
                continue
            series = _read_channel(h5, house, channels[appliance], start_ts, end_ts)
            series = clean_power(series, period_s=sample_period_s, is_aggregate=False)
            frame[appliance] = series

    df = pd.DataFrame(frame).sort_index()
    # Reindex onto the mains grid then forward-fill appliance gaps; anything left
    # is genuinely missing and treated as "off" (0 W).
    df = df.reindex(aggregate.index).ffill(limit=sample_period_s * 60).fillna(0.0)
    return df


def write_windows(
    df: pd.DataFrame,
    house: int,
    out_dir: Path = PROCESSED_DIR,
    stride_train: int = STRIDE_TRAIN,
    stride_eval: int = STRIDE_EVAL,
    sample_period_s: int = SAMPLE_PERIOD_S,
    split_ratios: tuple[float, float, float] = (0.7, 0.15, 0.15),
    dataset_name: str | None = None,
) -> dict:
    """Split by time, build Seq2Point windows and write HDF5 + manifest."""
    out_dir.mkdir(parents=True, exist_ok=True)
    n = len(df)
    if n < WINDOW_SIZE * 3:
        raise SystemExit(f"Not enough samples: {n}")
    i1 = int(n * split_ratios[0])
    i2 = int(n * (split_ratios[0] + split_ratios[1]))
    splits = {
        "train": (0, i1, stride_train),
        "val": (i1, i2, stride_eval),
        "test": (i2, n, stride_eval),
    }
    train = df.iloc[:i1]
    agg_mean = float(train["aggregate"].mean())
    agg_std = float(train["aggregate"].std() + 1e-6)

    present = [a for a in APPLIANCES if a in df.columns]
    manifest = {
        "dataset": dataset_name or f"ukdale_house{house}",
        "source": "UK-DALE (April 2017), CC BY 4.0",
        "house": house,
        "window_size": WINDOW_SIZE,
        "sample_period_s": sample_period_s,
        "appliances": present,
        "split_ratios": list(split_ratios),
        "time_range": {
            "start": df.index[0].isoformat(),
            "end": df.index[-1].isoformat(),
            "samples": int(n),
        },
        "stats": {},
        "files": {},
        "window_counts": {},
        "positive_ratios": {},
    }

    for appliance in present:
        target = df[appliance].to_numpy(dtype=np.float32)
        y_mean = float(train[appliance].mean())
        y_std = float(train[appliance].std() + 1e-6)
        manifest["stats"][appliance] = {
            "agg_mean": agg_mean,
            "agg_std": agg_std,
            "y_mean": y_mean,
            "y_std": y_std,
        }
        for split, (a, b, stride) in splits.items():
            x, y = sliding_windows(
                df["aggregate"].to_numpy(dtype=np.float32)[a:b],
                target[a:b],
                WINDOW_SIZE,
                stride,
            )
            if len(x) == 0:
                continue
            xn = ((x - agg_mean) / agg_std).astype(np.float16)
            yn = ((y - y_mean) / y_std).astype(np.float32)
            path = out_dir / f"{manifest['dataset']}_{appliance}_{split}.h5"
            with h5py.File(path, "w") as f:
                f.create_dataset("x", data=xn, compression="gzip", compression_opts=4)
                f.create_dataset("y", data=yn, compression="gzip", compression_opts=4)
            manifest["files"].setdefault(appliance, {})[split] = str(
                path.relative_to(ROOT)
            ).replace("\\", "/")
            manifest["window_counts"].setdefault(appliance, {})[split] = int(len(x))
            threshold = ON_THRESHOLDS.get(appliance, 50.0)
            manifest["positive_ratios"].setdefault(appliance, {})[split] = float(
                np.mean(y > threshold) if len(y) else 0.0
            )

    # One real day of test data for the replay adapter / live demo.
    replay_dir = out_dir / "replay"
    replay_dir.mkdir(exist_ok=True)
    day_len = int(86400 / sample_period_s)
    day = df.iloc[-day_len:] if n >= day_len else df
    replay_path = replay_dir / f"{manifest['dataset']}_day1.npz"
    np.savez_compressed(
        replay_path,
        aggregate=day["aggregate"].to_numpy(dtype=np.float32),
        **{a: day[a].to_numpy(dtype=np.float32) for a in present},
        timestamps=day.index.astype("int64").to_numpy(),
    )
    manifest["replay"] = str(replay_path.relative_to(ROOT)).replace("\\", "/")
    manifest["created_at"] = datetime.now(timezone.utc).isoformat()

    manifest_path = out_dir / "dataset_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Build UK-DALE windows from the official HDF5")
    parser.add_argument("--h5", "--path", dest="h5", type=Path, required=True)
    parser.add_argument("--house", "--building", dest="house", type=int, default=1)
    parser.add_argument("--start", default=None, help="YYYY-MM-DD (UTC)")
    parser.add_argument("--end", default=None, help="YYYY-MM-DD (UTC)")
    parser.add_argument("--sample-period", type=int, default=SAMPLE_PERIOD_S, help="seconds per sample")
    parser.add_argument("--stride-train", type=int, default=STRIDE_TRAIN)
    parser.add_argument("--stride-eval", type=int, default=STRIDE_EVAL)
    parser.add_argument("--out", type=Path, default=PROCESSED_DIR)
    parser.add_argument("--name", default=None, help="dataset name prefix")
    args = parser.parse_args()

    start, end = args.start, args.end
    if start is None or end is None:
        default_start, default_end = UKDALE_DEFAULT_RANGE.get(args.house, (None, None))
        start = start or default_start
        end = end or default_end

    print(f"Loading UK-DALE house {args.house}  {start} .. {end}  period={args.sample_period}s")
    df = load_ukdale_house(
        args.h5,
        house=args.house,
        start=start,
        end=end,
        sample_period_s=args.sample_period,
    )
    print(f"  samples: {len(df):,}  columns: {list(df.columns)}")
    print(df.describe().T[["mean", "std", "max"]].round(2).to_string())

    manifest = write_windows(
        df,
        house=args.house,
        out_dir=args.out,
        stride_train=args.stride_train,
        stride_eval=args.stride_eval,
        sample_period_s=args.sample_period,
        dataset_name=args.name,
    )
    print(json.dumps({k: manifest[k] for k in ("dataset", "window_counts", "time_range")}, indent=2))
    print(f"manifest -> {args.out / 'dataset_manifest.json'}")


if __name__ == "__main__":
    main()
