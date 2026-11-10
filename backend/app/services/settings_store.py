"""Persistent runtime settings (alert threshold, tariff, timezone)."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app import models
from app.config import settings

DEFAULTS = {
    "power_limit_w": lambda: settings.power_limit_w,
    "tariff_cny_per_kwh": lambda: settings.tariff_cny_per_kwh,
    "display_timezone": lambda: settings.display_timezone,
    "alert_cooldown_minutes": lambda: settings.alert_cooldown_minutes,
}

FLOAT_KEYS = {"power_limit_w", "tariff_cny_per_kwh", "alert_cooldown_minutes"}


def get_all(db: Session) -> dict:
    stored = {row.key: row.value for row in db.query(models.Setting).all()}
    result = {}
    for key, factory in DEFAULTS.items():
        raw = stored.get(key)
        if raw is None:
            result[key] = factory()
            continue
        result[key] = float(raw) if key in FLOAT_KEYS else raw
    return result


def get_float(db: Session, key: str) -> float:
    return float(get_all(db)[key])


def set_many(db: Session, values: dict) -> dict:
    for key, value in values.items():
        if key not in DEFAULTS or value is None:
            continue
        row = db.get(models.Setting, key)
        text = str(value)
        if row:
            row.value = text
        else:
            db.add(models.Setting(key=key, value=text))
    db.commit()
    return get_all(db)
