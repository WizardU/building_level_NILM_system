from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models
from app.db import get_db
from app.response import err, ok
from app.security import get_current_user

router = APIRouter(tags=["Events"])


def _event_out(e: models.Event) -> dict:
    return {
        "id": e.id,
        "meter_id": e.meter_id,
        "timestamp": e.timestamp.isoformat(),
        "type": e.type,
        "phase": e.phase,
        "delta_power_kw": e.delta_power_kw,
        "delta_reactive_kvar": e.delta_reactive_kvar,
        "appliance_guess": e.appliance_guess,
        "confidence": e.confidence,
    }


@router.get("/events")
def list_events(
    meter_id: int | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    type: str | None = None,
    page: int = 1,
    size: int = 50,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    q = db.query(models.Event)
    if meter_id is not None:
        q = q.filter_by(meter_id=meter_id)
    if start:
        q = q.filter(models.Event.timestamp >= start)
    if end:
        q = q.filter(models.Event.timestamp <= end)
    if type:
        q = q.filter_by(type=type)
    q = q.order_by(models.Event.timestamp.desc())
    total = q.count()
    items = q.offset((page - 1) * size).limit(size).all()
    return ok({"total": total, "items": [_event_out(e) for e in items]})


@router.get("/events/{event_id}")
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    e = db.get(models.Event, event_id)
    if not e:
        return err("Not found", 404, 404)
    return ok(_event_out(e))


@router.post("/events/upload")
def upload_events(
    body: dict,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    meter_id = body.get("meter_id")
    events = body.get("events") or []
    for ev in events:
        db.add(
            models.Event(
                meter_id=meter_id,
                timestamp=datetime.fromisoformat(ev["timestamp"].replace("Z", "")),
                type=ev.get("type", "state_change"),
                phase=ev.get("phase", "a"),
                delta_power_kw=ev.get("delta_power_kw", 0),
                delta_reactive_kvar=ev.get("delta_reactive_kvar", 0),
                appliance_guess=ev.get("appliance_guess", ""),
                confidence=ev.get("confidence", 0),
            )
        )
    db.commit()
    return ok({"uploaded": len(events)})
