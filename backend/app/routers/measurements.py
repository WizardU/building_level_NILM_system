from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models
from app.config import settings
from app.db import get_db
from app.response import err, ok
from app.schemas import MeasurementUpload
from app.security import get_current_user
from app.services import settings_store
from app.utils.time import parse_utc, to_iso, utcnow

router = APIRouter(tags=["Measurements"])


@router.get("/measurements/realtime")
def realtime(
    meter_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    meter = db.get(models.Meter, meter_id)
    if not meter:
        return err("Meter not found", 404, 404)
    last = (
        db.query(models.Measurement)
        .filter_by(meter_id=meter_id)
        .order_by(models.Measurement.timestamp.desc())
        .first()
    )
    if not last:
        return ok(
            {
                "meter_id": meter_id,
                "timestamp": to_iso(utcnow()),
                "total_power_kw": meter.last_power_kw,
                "samples": [],
            }
        )
    return ok(
        {
            "meter_id": meter_id,
            "timestamp": to_iso(last.timestamp),
            "total_power_kw": round(last.power_w / 1000.0, 4),
            "phase_a": {
                "voltage": last.voltage_a,
                "current": round(last.current_a, 3),
                "power_kw": round(last.power_w / 1000.0, 4),
            },
        }
    )


@router.get("/measurements/history")
def history(
    meter_id: int,
    start: datetime,
    end: datetime,
    page: int = 1,
    size: int = 1000,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    start_utc, end_utc = parse_utc(start), parse_utc(end)
    if end_utc <= start_utc:
        return err("end must be after start", 400, 400)
    if (end_utc - start_utc) > timedelta(days=settings.max_range_days):
        return err(f"range exceeds {settings.max_range_days} days", 400, 400)
    size = max(1, min(size, settings.max_page_size * 10))

    query = db.query(models.Measurement).filter(
        models.Measurement.meter_id == meter_id,
        models.Measurement.timestamp >= start_utc,
        models.Measurement.timestamp <= end_utc,
    )
    total = query.count()
    rows = (
        query.order_by(models.Measurement.timestamp.asc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )
    items = [
        {
            "timestamp": to_iso(row.timestamp),
            "phase_a": {
                "voltage": row.voltage_a,
                "current": row.current_a,
                "power_kw": round(row.power_w / 1000.0, 4),
            },
            "phase_b": {"voltage": 220.0, "current": 0.0, "power_kw": 0.0},
            "phase_c": {"voltage": 220.0, "current": 0.0, "power_kw": 0.0},
        }
        for row in rows
    ]
    return ok({"total": total, "items": items})


def _alert_within_cooldown(db: Session, building_id: int, dedupe_key: str, minutes: float) -> bool:
    since = utcnow() - timedelta(minutes=minutes)
    exists = (
        db.query(models.Alert.id)
        .filter(
            models.Alert.building_id == building_id,
            models.Alert.dedupe_key == dedupe_key,
            models.Alert.created_at >= since,
        )
        .first()
    )
    return exists is not None


@router.post("/measurements/upload")
def upload(
    body: MeasurementUpload,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    meter = db.get(models.Meter, body.meter_id)
    if not meter:
        return err("Meter not found", 404, 404)
    if not body.samples:
        return ok({"uploaded": 0, "duplicates": 0})
    if len(body.samples) > 10000:
        return err("too many samples in one request (max 10000)", 413, 413)

    samples = []
    for sample in body.samples:
        if sample.power_w is not None:
            power_w = float(sample.power_w)
        else:
            power_w = (
                sample.phase_a.power_kw
                + sample.phase_b.power_kw
                + sample.phase_c.power_kw
            ) * 1000.0
            if power_w == 0 and sample.phase_a.current:
                power_w = sample.phase_a.voltage * sample.phase_a.current
        samples.append((parse_utc(sample.timestamp), power_w, sample))

    first_ts = min(s[0] for s in samples)
    last_ts = max(s[0] for s in samples)
    existing = {
        row[0]
        for row in db.query(models.Measurement.timestamp)
        .filter(
            models.Measurement.meter_id == body.meter_id,
            models.Measurement.timestamp >= first_ts,
            models.Measurement.timestamp <= last_ts,
        )
        .all()
    }

    last_power = meter.last_power_kw
    inserted = 0
    duplicates = 0
    last_event_ts = None
    alert_sent = False
    power_limit = settings_store.get_float(db, "power_limit_w")
    cooldown = settings_store.get_float(db, "alert_cooldown_minutes")
    for timestamp, power_w, sample in sorted(samples, key=lambda item: item[0]):
        if timestamp in existing:
            duplicates += 1
            continue
        existing.add(timestamp)
        inserted += 1
        db.add(
            models.Measurement(
                meter_id=body.meter_id,
                timestamp=timestamp,
                power_w=power_w,
                voltage_a=sample.phase_a.voltage,
                current_a=sample.phase_a.current or (power_w / 220.0 if power_w else 0.0),
            )
        )
        # Edge detection with a 30 s debounce so one switch event logs once.
        delta_kw = power_w / 1000.0 - last_power
        if abs(delta_kw) > 0.3 and (
            last_event_ts is None or (timestamp - last_event_ts).total_seconds() >= 30
        ):
            db.add(
                models.Event(
                    meter_id=body.meter_id,
                    timestamp=timestamp,
                    type="on" if delta_kw > 0 else "off",
                    phase="a",
                    delta_power_kw=round(delta_kw, 3),
                    appliance_guess="",
                    confidence=0.5,
                )
            )
            last_event_ts = timestamp
        last_power = power_w / 1000.0
        meter.last_power_kw = last_power
        meter.last_seen = timestamp
        meter.status = "online"

        if power_w > power_limit and not alert_sent:
            key = f"overload:{body.meter_id}"
            if not _alert_within_cooldown(db, meter.building_id, key, cooldown):
                db.add(
                    models.Alert(
                        building_id=meter.building_id,
                        type="danger",
                        title="总功率过载预警",
                        message=(
                            f"实时总功率达到 {power_w:.0f}W，"
                            f"超过安全阈值 ({power_limit:.0f}W)"
                        ),
                        title_en="Mains Overload",
                        message_en=(
                            f"Live power reached {power_w:.0f} W, "
                            f"above the {power_limit:.0f} W limit"
                        ),
                        status="open",
                        dedupe_key=key,
                    )
                )
            alert_sent = True
    db.commit()
    return ok({"uploaded": inserted, "duplicates": duplicates})
