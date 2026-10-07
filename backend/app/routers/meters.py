from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models
from app.db import get_db
from app.response import err, ok
from app.schemas import MeterCreate
from app.security import get_current_user

router = APIRouter(tags=["Meters"])


def _meter_out(m: models.Meter) -> dict:
    p = m.last_power_kw
    phase = {"voltage": 220.0, "current": round(p * 1000 / 220 / 3, 3), "power_kw": round(p / 3, 3)}
    return {
        "id": m.id,
        "name": m.name,
        "type": m.type,
        "location": {
            "building_id": m.building_id,
            "floor_id": m.floor_id,
            "zone_id": m.zone_id,
        },
        "sampling_rate_hz": m.sampling_rate_hz,
        "protocol": m.protocol,
        "status": m.status,
        "last_seen": m.last_seen.isoformat() if m.last_seen else None,
        "current": {
            "phase_a": phase,
            "phase_b": phase,
            "phase_c": phase,
            "total_power_kw": p,
        },
    }


@router.get("/meters")
def list_meters(
    building_id: int | None = None,
    floor_id: int | None = None,
    zone_id: int | None = None,
    status: str | None = None,
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    q = db.query(models.Meter)
    if building_id is not None:
        q = q.filter_by(building_id=building_id)
    if floor_id is not None:
        q = q.filter_by(floor_id=floor_id)
    if zone_id is not None:
        q = q.filter_by(zone_id=zone_id)
    if status:
        q = q.filter_by(status=status)
    total = q.count()
    items = q.offset((page - 1) * size).limit(size).all()
    return ok({"total": total, "items": [_meter_out(m) for m in items]})


@router.post("/meters")
def create_meter(
    body: MeterCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    m = models.Meter(
        id=body.id,
        name=body.name,
        type=body.type,
        building_id=body.location.building_id,
        floor_id=body.location.floor_id,
        zone_id=body.location.zone_id,
        sampling_rate_hz=body.sampling_rate_hz,
        protocol=body.protocol,
        status="online",
        last_seen=datetime.utcnow(),
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return ok(_meter_out(m), status_code=201)


@router.get("/meters/{meter_id}")
def get_meter(
    meter_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    m = db.get(models.Meter, meter_id)
    if not m:
        return err("Not found", 404, 404)
    return ok(_meter_out(m))


@router.put("/meters/{meter_id}")
def update_meter(
    meter_id: int,
    body: MeterCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    m = db.get(models.Meter, meter_id)
    if not m:
        return err("Not found", 404, 404)
    m.name = body.name
    m.type = body.type
    m.building_id = body.location.building_id
    m.floor_id = body.location.floor_id
    m.zone_id = body.location.zone_id
    m.sampling_rate_hz = body.sampling_rate_hz
    m.protocol = body.protocol
    db.commit()
    return ok(_meter_out(m))


@router.delete("/meters/{meter_id}")
def delete_meter(
    meter_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    m = db.get(models.Meter, meter_id)
    if not m:
        return err("Not found", 404, 404)
    db.delete(m)
    db.commit()
    return ok({"deleted": meter_id})


@router.get("/meters/{meter_id}/status")
def meter_status(
    meter_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    m = db.get(models.Meter, meter_id)
    if not m:
        return err("Not found", 404, 404)
    return ok({"id": m.id, "status": m.status, "last_seen": m.last_seen.isoformat() if m.last_seen else None})
