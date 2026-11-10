"""Energy integration helpers over the measurement table."""

from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models
from app.utils.time import utcnow

EPOCH = datetime(1970, 1, 1)


def _seconds(times: list[datetime]) -> np.ndarray:
    return np.array([(t - EPOCH).total_seconds() for t in times], dtype="float64")


def energy_kwh(
    db: Session,
    meter_id: int,
    start: datetime,
    end: datetime,
    max_gap_s: float = 60.0,
) -> float:
    """Integrate measured power over time using the real sampling intervals."""
    rows = (
        db.query(models.Measurement.timestamp, models.Measurement.power_w)
        .filter(
            models.Measurement.meter_id == meter_id,
            models.Measurement.timestamp >= start,
            models.Measurement.timestamp <= end,
        )
        .order_by(models.Measurement.timestamp.asc())
        .all()
    )
    if len(rows) < 2:
        return 0.0
    seconds = _seconds([r[0] for r in rows])
    power = np.array([r[1] for r in rows], dtype="float64")
    dt = np.clip(np.diff(seconds), 0.0, max_gap_s)
    return float(np.sum(power[:-1] * dt) / 3.6e6)


def energy_since(db: Session, meter_id: int, hours: float) -> float:
    end = utcnow()
    return energy_kwh(db, meter_id, end - timedelta(hours=hours), end)


def coverage(db: Session, meter_id: int, start: datetime, end: datetime) -> dict:
    """Basic data-quality stats for a window (used by the dashboard)."""
    total = (
        db.query(func.count(models.Measurement.id))
        .filter(
            models.Measurement.meter_id == meter_id,
            models.Measurement.timestamp >= start,
            models.Measurement.timestamp <= end,
        )
        .scalar()
        or 0
    )
    expected = max(int((end - start).total_seconds()), 1)
    return {
        "samples": int(total),
        "expected_1hz": expected,
        "coverage": round(min(total / expected, 1.0), 4),
    }
