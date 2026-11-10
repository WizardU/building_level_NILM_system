"""Cleaning, resampling and windowing helpers for aggregate / appliance series."""

from __future__ import annotations

import numpy as np
import pandas as pd


def remove_outliers(series: pd.Series, max_power: float = 20000.0) -> pd.Series:
    s = series.copy()
    s[s < 0] = np.nan
    s[s > max_power] = np.nan
    return s


def fill_short_gaps(series: pd.Series, max_gap: int = 5) -> pd.Series:
    """Interpolate short gaps; leave long gaps for the caller to handle."""
    return series.interpolate(method="time", limit=max_gap)


def drop_long_nan_segments(df: pd.DataFrame, max_gap: int = 30) -> pd.DataFrame:
    """Drop rows that remain NaN after short-gap fill (long outages)."""
    return df.dropna()


def align_aggregate_and_appliances(
    aggregate: pd.Series,
    appliances: dict[str, pd.Series],
    freq: str = "1s",
) -> pd.DataFrame:
    """Resample to a common timeline and join aggregate + appliance columns."""
    agg = remove_outliers(aggregate).resample(freq).mean()
    agg = fill_short_gaps(agg)
    frames = {"aggregate": agg}
    for name, ser in appliances.items():
        a = remove_outliers(ser).resample(freq).mean().ffill(limit=10)
        frames[name] = a
    df = pd.DataFrame(frames)
    return drop_long_nan_segments(df)


def clean_power(
    series: pd.Series,
    period_s: int = 1,
    max_power: float = 30000.0,
    max_gap: int = 60,
    is_aggregate: bool = False,
) -> pd.Series:
    """Resample to ``period_s`` and produce a gap-free power series in watts.

    - negative values are treated as missing (sensor glitches)
    - implausibly large values are treated as missing
    - gaps up to ``max_gap`` samples are interpolated (aggregate) or
      forward-filled (appliances, which are effectively "off" while missing)
    - remaining gaps become 0 so the time index stays regular
    """
    s = series.astype("float64")
    s[s < 0] = np.nan
    s[s > max_power] = np.nan
    s = s[~s.index.duplicated(keep="last")].sort_index()
    s = s.resample(f"{period_s}s").mean()
    if is_aggregate:
        s = s.interpolate(method="time", limit=max_gap)
    else:
        s = s.ffill(limit=max_gap)
    return s.fillna(0.0).clip(lower=0.0)


def sliding_windows(
    aggregate: np.ndarray,
    target: np.ndarray,
    window: int,
    stride: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Seq2Point windows: X shape (N, W), y = target at the window midpoint."""
    n = len(aggregate)
    if n < window or stride < 1:
        return np.zeros((0, window), dtype=np.float32), np.zeros((0,), dtype=np.float32)
    starts = np.arange(0, n - window + 1, stride, dtype=np.int64)
    # A view, then one copy for the selected windows (keeps peak memory bounded).
    x = np.lib.stride_tricks.sliding_window_view(aggregate, window)[starts]
    y = target[starts + window // 2]
    return np.ascontiguousarray(x, dtype=np.float32), np.asarray(y, dtype=np.float32)


def window_boundaries(n: int, window: int, stride: int) -> np.ndarray:
    """Midpoint sample indices for the windows produced by ``sliding_windows``."""
    if n < window or stride < 1:
        return np.zeros((0,), dtype=np.int64)
    starts = np.arange(0, n - window + 1, stride, dtype=np.int64)
    return starts + window // 2
