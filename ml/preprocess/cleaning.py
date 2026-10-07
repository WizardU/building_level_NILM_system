"""Cleaning and alignment helpers for aggregate / appliance series."""

from __future__ import annotations

import numpy as np
import pandas as pd


def remove_outliers(
    series: pd.Series,
    max_power: float = 20000.0,
) -> pd.Series:
    s = series.copy()
    s[s < 0] = np.nan
    s[s > max_power] = np.nan
    return s


def fill_short_gaps(series: pd.Series, max_gap: int = 5) -> pd.Series:
    """Interpolate gaps shorter than max_gap samples; leave long gaps as NaN."""
    s = series.copy()
    is_na = s.isna()
    if not is_na.any():
        return s
    groups = (is_na != is_na.shift()).cumsum()
    for _, grp in s[is_na].groupby(groups[is_na]):
        if len(grp) <= max_gap:
            s.loc[grp.index] = np.nan  # mark for interpolate
    return s.interpolate(method="time", limit=max_gap).ffill().bfill()


def drop_long_nan_segments(df: pd.DataFrame, max_gap: int = 30) -> pd.DataFrame:
    """Drop rows that remain NaN after short-gap fill (long outages)."""
    return df.dropna()


def align_aggregate_and_appliances(
    aggregate: pd.Series,
    appliances: dict[str, pd.Series],
    freq: str = "1s",
) -> pd.DataFrame:
    """Resample to common timeline and join aggregate + appliance columns."""
    agg = remove_outliers(aggregate).resample(freq).mean()
    agg = fill_short_gaps(agg)
    frames = {"aggregate": agg}
    for name, ser in appliances.items():
        a = remove_outliers(ser).resample(freq).mean()
        a = fill_short_gaps(a)
        frames[name] = a
    df = pd.DataFrame(frames)
    return drop_long_nan_segments(df)


def sliding_windows(
    aggregate: np.ndarray,
    target: np.ndarray,
    window: int,
    stride: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Seq2Point windows: X shape (N, W), y mid-point target power."""
    half = window // 2
    xs, ys = [], []
    n = len(aggregate)
    for t in range(half, n - half, stride):
        xs.append(aggregate[t - half : t + half + 1])
        ys.append(target[t])
    if not xs:
        return np.zeros((0, window), dtype=np.float32), np.zeros((0,), dtype=np.float32)
    return np.asarray(xs, dtype=np.float32), np.asarray(ys, dtype=np.float32)
