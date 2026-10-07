from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models
from app.db import get_db
from app.response import err, ok
from app.schemas import BuildingCreate, ZoneCreate
from app.security import get_current_user

router = APIRouter(tags=["Buildings"])


def _building_out(b: models.Building, db: Session) -> dict:
    meters = db.query(models.Meter).filter_by(building_id=b.id).all()
    total = sum(m.last_power_kw for m in meters)
    return {
        "id": b.id,
        "name": b.name,
        "address": b.address,
        "floors_count": b.floors_count,
        "meters_count": len(meters),
        "total_power_kw": round(total, 3),
        "status": b.status,
    }


@router.get("/buildings")
def list_buildings(
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    q = db.query(models.Building)
    total = q.count()
    items = q.offset((page - 1) * size).limit(size).all()
    return ok({"total": total, "items": [_building_out(b, db) for b in items]})


@router.post("/buildings")
def create_building(
    body: BuildingCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    b = models.Building(name=body.name, address=body.address, floors_count=body.floors_count)
    db.add(b)
    db.commit()
    db.refresh(b)
    return ok(_building_out(b, db), status_code=201)


@router.get("/buildings/{building_id}")
def get_building(
    building_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    b = db.get(models.Building, building_id)
    if not b:
        return err("Not found", 404, 404)
    return ok(_building_out(b, db))


@router.put("/buildings/{building_id}")
def update_building(
    building_id: int,
    body: BuildingCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    b = db.get(models.Building, building_id)
    if not b:
        return err("Not found", 404, 404)
    b.name = body.name
    b.address = body.address
    b.floors_count = body.floors_count
    db.commit()
    return ok(_building_out(b, db))


@router.delete("/buildings/{building_id}")
def delete_building(
    building_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    b = db.get(models.Building, building_id)
    if not b:
        return err("Not found", 404, 404)
    db.delete(b)
    db.commit()
    return ok({"deleted": building_id})


@router.get("/buildings/{building_id}/floors")
def list_floors(
    building_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    floors = db.query(models.Floor).filter_by(building_id=building_id).all()
    items = []
    for f in floors:
        zc = db.query(models.Zone).filter_by(floor_id=f.id).count()
        items.append(
            {
                "id": f.id,
                "building_id": f.building_id,
                "floor_number": f.floor_number,
                "name": f.name,
                "zones_count": zc,
            }
        )
    return ok({"total": len(items), "items": items})


@router.post("/buildings/{building_id}/floors")
def create_floor(
    building_id: int,
    body: dict,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    f = models.Floor(
        building_id=building_id,
        floor_number=body.get("floor_number", 1),
        name=body.get("name", "Floor"),
    )
    db.add(f)
    db.commit()
    db.refresh(f)
    return ok(
        {
            "id": f.id,
            "building_id": f.building_id,
            "floor_number": f.floor_number,
            "name": f.name,
            "zones_count": 0,
        },
        status_code=201,
    )


@router.get("/floors/{floor_id}/zones")
def list_zones(
    floor_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    zones = db.query(models.Zone).filter_by(floor_id=floor_id).all()
    return ok(
        {
            "total": len(zones),
            "items": [
                {"id": z.id, "floor_id": z.floor_id, "name": z.name, "type": z.type}
                for z in zones
            ],
        }
    )


@router.post("/floors/{floor_id}/zones")
def create_zone(
    floor_id: int,
    body: ZoneCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    z = models.Zone(floor_id=floor_id, name=body.name, type=body.type)
    db.add(z)
    db.commit()
    db.refresh(z)
    return ok({"id": z.id, "floor_id": z.floor_id, "name": z.name, "type": z.type}, status_code=201)
