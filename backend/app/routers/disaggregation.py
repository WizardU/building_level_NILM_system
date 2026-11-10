import json
import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app import models
from app.config import settings
from app.db import SessionLocal, get_db
from app.response import err, ok
from app.schemas import DisaggregationRun
from app.security import get_current_user
from app.services import metrics as metrics_service
from app.services.inference import disagg_service
from app.utils.time import parse_utc, to_iso, utcnow

router = APIRouter(tags=["Disaggregation"])


def _run_task(task_id: str, meter_id: int, start: datetime, end: datetime) -> None:
    db = SessionLocal()
    try:
        task = db.get(models.TaskStatus, task_id)
        if task:
            task.status = "running"
            task.progress = 10
            db.commit()
        result = disagg_service.run(db, meter_id, start, end, stride=30)
        task = db.get(models.TaskStatus, task_id)
        if task:
            task.status = "completed"
            task.progress = 100
            task.result_json = json.dumps(
                {
                    "model_version": result.get("model_version"),
                    "backend": result.get("backend"),
                    "appliances": len(result.get("appliances", [])),
                }
            )
            db.commit()
    except Exception as exc:  # noqa: BLE001 - task failure must be reported
        task = db.get(models.TaskStatus, task_id)
        if task:
            task.status = "failed"
            task.message = str(exc)[:250]
            db.commit()
    finally:
        db.close()


def _validate(start_utc: datetime, end_utc: datetime):
    if end_utc <= start_utc:
        return "end must be after start"
    if (end_utc - start_utc) > timedelta(days=settings.max_range_days):
        return f"range exceeds {settings.max_range_days} days"
    return None


@router.get("/disaggregation/models")
def models_status(_: models.User = Depends(get_current_user)):
    status = disagg_service.status()
    status["metrics"] = metrics_service.as_summary()
    return ok(status)


@router.get("/disaggregation/result")
def get_result(
    meter_id: int,
    start: datetime,
    end: datetime,
    appliance_types: str | None = None,
    refresh: bool = False,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    start_utc, end_utc = parse_utc(start), parse_utc(end)
    error = _validate(start_utc, end_utc)
    if error:
        return err(error, 400, 400)

    data = None if refresh else disagg_service.get_cached(db, meter_id, start_utc, end_utc)
    if data is None:
        data = disagg_service.run(db, meter_id, start_utc, end_utc, stride=30)
    if appliance_types:
        allowed = {t.strip() for t in appliance_types.split(",") if t.strip()}
        data = dict(data)
        data["appliances"] = [a for a in data.get("appliances", []) if a["type"] in allowed]
    return ok(data)


@router.post("/disaggregation/run")
def run_disaggregation(
    body: DisaggregationRun,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    start_utc, end_utc = parse_utc(body.start), parse_utc(body.end)
    error = _validate(start_utc, end_utc)
    if error:
        return err(error, 400, 400)
    if not db.get(models.Meter, body.meter_id):
        return err("Meter not found", 404, 404)
    task_id = f"task-{uuid.uuid4().hex[:12]}"
    db.add(models.TaskStatus(id=task_id, status="pending", progress=0))
    db.commit()
    background.add_task(_run_task, task_id, body.meter_id, start_utc, end_utc)
    return ok({"task_id": task_id}, status_code=202)


@router.get("/disaggregation/status/{task_id}")
def task_status(
    task_id: str,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    task = db.get(models.TaskStatus, task_id)
    if not task:
        return err("Not found", 404, 404)
    return ok(
        {
            "task_id": task.id,
            "status": task.status,
            "progress": task.progress,
            "message": task.message,
            "result": json.loads(task.result_json) if task.result_json else None,
        }
    )


@router.get("/disaggregation/overview")
def overview(
    meter_id: int = 101,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    """Dashboard KPIs: live mains power plus the latest cached inference."""
    meter = db.get(models.Meter, meter_id)
    appliances_db = db.query(models.Appliance).filter_by(meter_id=meter_id).all()
    latest = disagg_service.latest_cached(db, meter_id)

    active = 0
    if latest:
        active = sum(1 for a in latest.get("appliances", []) if a.get("state"))

    attention = metrics_service.average("attention")
    from app.services import settings_store

    summary = {
        "mainsPower": round((meter.last_power_kw if meter else 0.0) * 1000.0, 1),
        "activeDevices": active,
        "totalDevices": len(appliances_db),
        "f1Score": attention.get("state_f1", 0.0),
        "eventF1": attention.get("event_f1", 0.0),
        "maeScore": attention.get("mae", 0.0),
        "saeScore": attention.get("sae", 0.0),
        "latency": (latest or {}).get("inference_ms"),
        "backend": disagg_service.backend,
        "modelVersion": disagg_service.version,
        "powerLimit": settings_store.get_float(db, "power_limit_w"),
        "meter_id": meter_id,
        "lastInference": (latest or {}).get("start"),
        "timestamp": to_iso(utcnow()),
    }
    return ok(summary)
