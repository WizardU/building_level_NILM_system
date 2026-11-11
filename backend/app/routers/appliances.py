from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models
from app.db import get_db
from app.response import err, ok
from app.schemas import ApplianceCreate
from app.security import get_current_user
from app.services.inference import disagg_service
from app.utils.time import parse_utc, to_iso

router = APIRouter(tags=["Appliances"])


@router.get("/appliances")
def list_appliances(
    meter_id: int | None = None,
    type: str | None = None,
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    q = db.query(models.Appliance)
    if meter_id is not None:
        q = q.filter_by(meter_id=meter_id)
    if type:
        q = q.filter_by(type=type)
    total = q.count()
    items = q.offset((page - 1) * size).limit(size).all()
    return ok(
        {
            "total": total,
            "items": [
                {
                    "id": a.id,
                    "name": a.name,
                    "type": a.type,
                    "meter_id": a.meter_id,
                    "zone_id": a.zone_id,
                    "rated_power_kw": a.rated_power_kw,
                }
                for a in items
            ],
        }
    )


@router.post("/appliances")
def create_appliance(
    body: ApplianceCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    a = models.Appliance(
        name=body.name,
        type=body.type,
        meter_id=body.meter_id,
        zone_id=body.zone_id,
        rated_power_kw=body.rated_power_kw,
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return ok(
        {
            "id": a.id,
            "name": a.name,
            "type": a.type,
            "meter_id": a.meter_id,
            "zone_id": a.zone_id,
            "rated_power_kw": a.rated_power_kw,
        },
        status_code=201,
    )


@router.get("/appliances/{appliance_id}")
def get_appliance(
    appliance_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    a = db.get(models.Appliance, appliance_id)
    if not a:
        return err("Not found", 404, 404)
    return ok(
        {
            "id": a.id,
            "name": a.name,
            "type": a.type,
            "meter_id": a.meter_id,
            "zone_id": a.zone_id,
            "rated_power_kw": a.rated_power_kw,
        }
    )


@router.put("/appliances/{appliance_id}")
def update_appliance(
    appliance_id: int,
    body: ApplianceCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    a = db.get(models.Appliance, appliance_id)
    if not a:
        return err("Not found", 404, 404)
    a.name = body.name
    a.type = body.type
    a.meter_id = body.meter_id
    a.zone_id = body.zone_id
    a.rated_power_kw = body.rated_power_kw
    db.commit()
    return ok(
        {
            "id": a.id,
            "name": a.name,
            "type": a.type,
            "meter_id": a.meter_id,
            "zone_id": a.zone_id,
            "rated_power_kw": a.rated_power_kw,
        }
    )


@router.delete("/appliances/{appliance_id}")
def delete_appliance(
    appliance_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    a = db.get(models.Appliance, appliance_id)
    if not a:
        return err("Not found", 404, 404)
    db.delete(a)
    db.commit()
    return ok({"deleted": appliance_id})


@router.get("/appliances/{appliance_id}/usage")
def usage(
    appliance_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    """Usage for the latest cached disaggregation window (no fabricated values)."""
    appliance = db.get(models.Appliance, appliance_id)
    if not appliance:
        return err("Not found", 404, 404)
    latest = disagg_service.latest_cached(db, appliance.meter_id)
    match = None
    if latest:
        match = next(
            (item for item in latest.get("appliances", []) if item.get("type") == appliance.type),
            None,
        )
    if not match or not latest.get("start") or not latest.get("end"):
        return ok(
            {
                "appliance_id": appliance.id,
                "type": appliance.type,
                "available": False,
                "start": None,
                "end": None,
                "duration_hours": 0.0,
                "energy_kwh": 0.0,
                "avg_power_kw": 0.0,
            }
        )
    start = parse_utc(latest["start"])
    end = parse_utc(latest["end"])
    duration = max((end - start).total_seconds() / 3600.0, 1e-6)
    energy = float(match.get("energy_kwh", 0.0))
    return ok(
        {
            "appliance_id": appliance.id,
            "type": appliance.type,
            "available": True,
            "start": to_iso(start),
            "end": to_iso(end),
            "duration_hours": round(duration, 3),
            "energy_kwh": round(energy, 4),
            "avg_power_kw": round(energy / duration, 4),
            "model_version": latest.get("model_version"),
        }
    )
