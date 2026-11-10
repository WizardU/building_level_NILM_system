from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models
from app.config import settings
from app.db import get_db
from app.response import err, ok
from app.schemas import MeterCreate
from app.security import get_current_user
from app.utils.time import to_iso, utcnow

router = APIRouter(tags=["Meters"])


def _phase_split(meter: models.Meter) -> list[float]:
    total = meter.last_power_kw
    if meter.type == "three_phase":
        return [total / 3.0] * 3
    return [total, 0.0, 0.0]


def _meter_out(meter: models.Meter) -> dict:
    a, b, c = _phase_split(meter)

    def phase(power_kw: float) -> dict:
        current = power_kw * 1000.0 / 220.0
        return {
            "voltage": 220.0,
            "current": round(current, 3),
            "power_kw": round(power_kw, 4),
        }

    return {
        "id": meter.id,
        "name": meter.name,
        "type": meter.type,
        "location": {
            "building_id": meter.building_id,
            "floor_id": meter.floor_id,
            "zone_id": meter.zone_id,
        },
        "sampling_rate_hz": meter.sampling_rate_hz,
        "protocol": meter.protocol,
        "status": meter.status,
        "last_seen": to_iso(meter.last_seen),
        "current": {
            "phase_a": phase(a),
            "phase_b": phase(b),
            "phase_c": phase(c),
            "total_power_kw": round(meter.last_power_kw, 4),
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
    size = max(1, min(size, settings.max_page_size))
    query = db.query(models.Meter)
    if building_id is not None:
        query = query.filter_by(building_id=building_id)
    if floor_id is not None:
        query = query.filter_by(floor_id=floor_id)
    if zone_id is not None:
        query = query.filter_by(zone_id=zone_id)
    if status:
        query = query.filter_by(status=status)
    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()
    return ok({"total": total, "items": [_meter_out(m) for m in items]})


@router.post("/meters")
def create_meter(
    body: MeterCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    meter = models.Meter(
        id=body.id,
        name=body.name,
        type=body.type,
        building_id=body.location.building_id,
        floor_id=body.location.floor_id,
        zone_id=body.location.zone_id,
        sampling_rate_hz=body.sampling_rate_hz,
        protocol=body.protocol,
        status="online",
        last_seen=utcnow(),
    )
    db.add(meter)
    db.commit()
    db.refresh(meter)
    return ok(_meter_out(meter), status_code=201)


@router.get("/meters/{meter_id}")
def get_meter(
    meter_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    meter = db.get(models.Meter, meter_id)
    if not meter:
        return err("Not found", 404, 404)
    return ok(_meter_out(meter))


@router.get("/meters/{meter_id}/current")
def meter_current(
    meter_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    """Current reading. Kept as an alias because the mobile client uses it."""
    meter = db.get(models.Meter, meter_id)
    if not meter:
        return err("Not found", 404, 404)
    return ok(_meter_out(meter)["current"])


@router.put("/meters/{meter_id}")
def update_meter(
    meter_id: int,
    body: MeterCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    meter = db.get(models.Meter, meter_id)
    if not meter:
        return err("Not found", 404, 404)
    meter.name = body.name
    meter.type = body.type
    meter.building_id = body.location.building_id
    meter.floor_id = body.location.floor_id
    meter.zone_id = body.location.zone_id
    meter.sampling_rate_hz = body.sampling_rate_hz
    meter.protocol = body.protocol
    db.commit()
    return ok(_meter_out(meter))


@router.delete("/meters/{meter_id}")
def delete_meter(
    meter_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    meter = db.get(models.Meter, meter_id)
    if not meter:
        return err("Not found", 404, 404)
    db.delete(meter)
    db.commit()
    return ok({"deleted": meter_id})


@router.get("/meters/{meter_id}/status")
def meter_status(
    meter_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    meter = db.get(models.Meter, meter_id)
    if not meter:
        return err("Not found", 404, 404)
    return ok(
        {
            "id": meter.id,
            "status": meter.status,
            "last_seen": to_iso(meter.last_seen),
            "last_power_kw": round(meter.last_power_kw, 4),
        }
    )
