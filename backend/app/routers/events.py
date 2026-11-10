from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models
from app.config import settings
from app.db import get_db
from app.response import err, ok
from app.security import get_current_user
from app.utils.time import parse_utc, to_iso

router = APIRouter(tags=["Events"])


def _event_out(event: models.Event) -> dict:
    return {
        "id": event.id,
        "meter_id": event.meter_id,
        "timestamp": to_iso(event.timestamp),
        "type": event.type,
        "phase": event.phase,
        "delta_power_kw": event.delta_power_kw,
        "delta_reactive_kvar": event.delta_reactive_kvar,
        "appliance_guess": event.appliance_guess,
        "confidence": event.confidence,
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
    size = max(1, min(size, settings.max_page_size))
    query = db.query(models.Event)
    if meter_id is not None:
        query = query.filter_by(meter_id=meter_id)
    if start:
        query = query.filter(models.Event.timestamp >= parse_utc(start))
    if end:
        query = query.filter(models.Event.timestamp <= parse_utc(end))
    if type:
        query = query.filter_by(type=type)
    query = query.order_by(models.Event.timestamp.desc())
    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()
    return ok({"total": total, "items": [_event_out(e) for e in items]})


@router.get("/events/{event_id}")
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    event = db.get(models.Event, event_id)
    if not event:
        return err("Not found", 404, 404)
    return ok(_event_out(event))


@router.post("/events/upload")
def upload_events(
    body: dict,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    meter_id = body.get("meter_id")
    events = body.get("events") or []
    if len(events) > 1000:
        return err("too many events (max 1000)", 413, 413)
    for event in events:
        timestamp = event.get("timestamp")
        db.add(
            models.Event(
                meter_id=meter_id,
                timestamp=parse_utc(timestamp) if timestamp else None,
                type=event.get("type", "state_change"),
                phase=event.get("phase", "a"),
                delta_power_kw=event.get("delta_power_kw", 0),
                delta_reactive_kvar=event.get("delta_reactive_kvar", 0),
                appliance_guess=event.get("appliance_guess", ""),
                confidence=event.get("confidence", 0),
            )
        )
    db.commit()
    return ok({"uploaded": len(events)})
