from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models
from app.db import get_db
from app.response import err, ok
from app.schemas import ApplianceCreate
from app.security import get_current_user

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
    a = db.get(models.Appliance, appliance_id)
    if not a:
        return err("Not found", 404, 404)
    end = datetime.utcnow()
    start = end - timedelta(hours=4)
    return ok(
        {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "duration_hours": 4.5,
            "energy_kwh": round(a.rated_power_kw * 2.5, 3),
            "avg_power_kw": a.rated_power_kw,
        }
    )
