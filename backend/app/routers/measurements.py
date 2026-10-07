from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models
from app.config import settings
from app.db import get_db
from app.response import err, ok
from app.schemas import MeasurementUpload
from app.security import get_current_user

router = APIRouter(tags=["Measurements"])


@router.get("/measurements/realtime")
def realtime(
    meter_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    m = db.get(models.Meter, meter_id)
    if not m:
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
                "timestamp": datetime.utcnow().isoformat(),
                "total_power_kw": m.last_power_kw,
                "samples": [],
            }
        )
    return ok(
        {
            "meter_id": meter_id,
            "timestamp": last.timestamp.isoformat(),
            "total_power_kw": last.power_w / 1000.0,
            "phase_a": {
                "voltage": last.voltage_a,
                "current": last.current_a,
                "power_kw": last.power_w / 1000.0,
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
    q = (
        db.query(models.Measurement)
        .filter(
            models.Measurement.meter_id == meter_id,
            models.Measurement.timestamp >= start,
            models.Measurement.timestamp <= end,
        )
        .order_by(models.Measurement.timestamp.asc())
    )
    total = q.count()
    rows = q.offset((page - 1) * size).limit(size).all()
    items = [
        {
            "timestamp": r.timestamp.isoformat(),
            "phase_a": {
                "voltage": r.voltage_a,
                "current": r.current_a,
                "power_kw": r.power_w / 1000.0,
            },
            "phase_b": {"voltage": 220.0, "current": 0.0, "power_kw": 0.0},
            "phase_c": {"voltage": 220.0, "current": 0.0, "power_kw": 0.0},
        }
        for r in rows
    ]
    return ok({"total": total, "items": items})


@router.post("/measurements/upload")
def upload(
    body: MeasurementUpload,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    m = db.get(models.Meter, body.meter_id)
    if not m:
        return err("Meter not found", 404, 404)
    last_power = m.last_power_kw
    for s in body.samples:
        if s.power_w is not None:
            pw = s.power_w
        else:
            pw = (
                s.phase_a.power_kw + s.phase_b.power_kw + s.phase_c.power_kw
            ) * 1000.0
            if pw == 0 and s.phase_a.current:
                pw = s.phase_a.voltage * s.phase_a.current
        db.add(
            models.Measurement(
                meter_id=body.meter_id,
                timestamp=s.timestamp,
                power_w=float(pw),
                voltage_a=s.phase_a.voltage,
                current_a=s.phase_a.current or (pw / 220.0 if pw else 0),
            )
        )
        # simple edge event detection
        delta_kw = pw / 1000.0 - last_power
        if abs(delta_kw) > 0.3:
            db.add(
                models.Event(
                    meter_id=body.meter_id,
                    timestamp=s.timestamp,
                    type="on" if delta_kw > 0 else "off",
                    phase="a",
                    delta_power_kw=round(delta_kw, 3),
                    appliance_guess="",
                    confidence=0.5,
                )
            )
            if pw > settings.power_limit_w:
                db.add(
                    models.Alert(
                        building_id=m.building_id,
                        type="danger",
                        title="总功率过载预警",
                        message=f"实时总功率达到 {pw:.0f}W，超过安全阈值 ({settings.power_limit_w:.0f}W)",
                        status="open",
                    )
                )
        last_power = pw / 1000.0
        m.last_power_kw = last_power
        m.last_seen = s.timestamp
        m.status = "online"
    db.commit()
    return ok({"uploaded": len(body.samples)})
