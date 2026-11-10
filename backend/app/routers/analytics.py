import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models
from app.config import settings
from app.db import get_db
from app.response import err, ok
from app.security import get_current_user
from app.services import metrics as metrics_service
from app.services import settings_store
from app.services.energy import energy_kwh
from app.services.inference import disagg_service
from app.utils.time import to_iso, utcnow

router = APIRouter(tags=["Analytics"])


def _tz() -> ZoneInfo:
    try:
        return ZoneInfo(settings.display_timezone)
    except Exception:  # noqa: BLE001 - bad config should not break analytics
        return ZoneInfo("UTC")


def _local_day_start() -> datetime:
    local_now = utcnow().replace(tzinfo=timezone.utc).astimezone(_tz())
    local_midnight = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
    return local_midnight.astimezone(timezone.utc).replace(tzinfo=None)


@router.get("/analytics/overview")
def overview(
    building_id: int = 1,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    meters = db.query(models.Meter).filter_by(building_id=building_id).all()
    total_power = sum(m.last_power_kw for m in meters)
    appliances = (
        db.query(models.Appliance)
        .join(models.Meter)
        .filter(models.Meter.building_id == building_id)
        .all()
    )
    day_start = _local_day_start()
    now = utcnow()
    today_energy = sum(energy_kwh(db, m.id, day_start, now) for m in meters)
    month_energy = sum(
        energy_kwh(db, m.id, now - timedelta(days=30), now) for m in meters
    )

    floors = db.query(models.Floor).filter_by(building_id=building_id).all()
    floor_stats = []
    for floor in floors:
        floor_meters = [m for m in meters if m.floor_id == floor.id]
        floor_energy = sum(
            energy_kwh(db, m.id, now - timedelta(hours=8), now) for m in floor_meters
        )
        floor_stats.append(
            {
                "floor_id": floor.id,
                "name": floor.name,
                "power_kw": round(sum(m.last_power_kw for m in floor_meters), 3),
                "energy_kwh": round(floor_energy, 3),
            }
        )

    latest = disagg_service.latest_cached(db, meters[0].id) if meters else None
    top = []
    if latest:
        top = sorted(
            (
                {
                    "appliance_id": a.get("appliance_id"),
                    "name": a.get("name"),
                    "type": a.get("type"),
                    "power_kw": round((a.get("power_w") or 0) / 1000.0, 3),
                    "energy_kwh": a.get("energy_kwh", 0),
                }
                for a in latest.get("appliances", [])
            ),
            key=lambda item: item["energy_kwh"],
            reverse=True,
        )[:5]

    return ok(
        {
            "building_id": building_id,
            "timestamp": to_iso(now),
            "total_power_kw": round(total_power, 3),
            "today_energy_kwh": round(today_energy, 3),
            "month_energy_kwh": round(month_energy, 3),
            "active_appliances": len(appliances),
            "floors": floor_stats,
            "top_appliances": top,
            "tariff_cny_per_kwh": settings_store.get_float(db, "tariff_cny_per_kwh"),
        }
    )


@router.get("/analytics/energy")
def energy(
    building_id: int = 1,
    meter_id: int = 101,
    start: datetime | None = None,
    end: datetime | None = None,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    latest = disagg_service.latest_cached(db, meter_id)
    tariff = settings_store.get_float(db, "tariff_cny_per_kwh")
    if start and end:
        from app.utils.time import parse_utc

        window_start, window_end = parse_utc(start), parse_utc(end)
        breakdown = []
        if latest and latest.get("start") == to_iso(window_start):
            breakdown = latest.get("appliances", [])
        total_kwh = energy_kwh(db, meter_id, window_start, window_end)
        estimated = not breakdown
    elif latest and latest.get("start") and latest.get("end"):
        from app.utils.time import parse_utc

        window_start = parse_utc(latest["start"])
        window_end = parse_utc(latest["end"])
        breakdown = latest.get("appliances", [])
        total_kwh = energy_kwh(db, meter_id, window_start, window_end)
        estimated = False
    else:
        window_end = utcnow()
        window_start = window_end - timedelta(hours=2)
        breakdown = []
        total_kwh = energy_kwh(db, meter_id, window_start, window_end)
        estimated = True

    rows = [
        {
            "key": a["type"],
            "name": a["name"],
            "kWh": round(float(a.get("energy_kwh", 0.0)), 3),
            "cost": round(float(a.get("energy_kwh", 0.0)) * tariff, 2),
            "ratio": a.get("percentage", 0.0),
        }
        for a in breakdown
    ]
    breakdown_total = sum(row["kWh"] for row in rows)
    unmetered = max(total_kwh - breakdown_total, 0.0)

    return ok(
        {
            "totalCost": round(total_kwh * tariff, 2),
            "totalKWh": round(total_kwh, 3),
            "breakdown": rows,
            "unmeteredKWh": round(unmetered, 3),
            "window": {"start": to_iso(window_start), "end": to_iso(window_end)},
            "tariff": tariff,
            "estimated": estimated,
        }
    )


@router.get("/analytics/alerts")
def alerts(
    building_id: int = 1,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    rows = (
        db.query(models.Alert)
        .filter_by(building_id=building_id)
        .order_by(models.Alert.created_at.desc())
        .limit(50)
        .all()
    )
    local_tz = _tz()
    items = [
        {
            "id": alert.id,
            "key": (alert.dedupe_key or alert.type).split(":")[0],
            "type": alert.type if alert.type in ("danger", "warning", "info") else "warning",
            "title": alert.title,
            "message": alert.message,
            "title_en": alert.title_en or "",
            "message_en": alert.message_en or "",
            "time": alert.created_at.replace(tzinfo=timezone.utc)
            .astimezone(local_tz)
            .strftime("%H:%M:%S"),
            "created_at": to_iso(alert.created_at),
            "status": "已处理" if alert.resolved else "未处理",
            "resolved": alert.resolved,
        }
        for alert in rows
    ]
    return ok({"total": len(items), "items": items})


@router.post("/analytics/alerts/{alert_id}/resolve")
def resolve_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    alert = db.get(models.Alert, alert_id)
    if not alert:
        return err("Not found", 404, 404)
    alert.resolved = True
    alert.status = "resolved"
    db.commit()
    return ok({"id": alert.id, "resolved": True})


@router.get("/analytics/settings")
def get_settings(db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    return ok(settings_store.get_all(db))


@router.put("/analytics/settings")
def update_settings(
    body: dict,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    allowed = {
        "power_limit_w": (500.0, 30000.0),
        "tariff_cny_per_kwh": (0.0, 10.0),
        "alert_cooldown_minutes": (0.0, 1440.0),
    }
    values: dict = {}
    for key, (low, high) in allowed.items():
        if key not in body:
            continue
        try:
            number = float(body[key])
        except (TypeError, ValueError):
            return err(f"{key} must be a number", 400, 400)
        if not low <= number <= high:
            return err(f"{key} must be between {low} and {high}", 400, 400)
        values[key] = number
    return ok(settings_store.set_many(db, values))


@router.get("/analytics/metrics")
def metrics(_: models.User = Depends(get_current_user)):
    summary = metrics_service.as_summary()
    summary["engine"] = disagg_service.status()
    return ok(summary)


@router.get("/analytics/reports")
def reports(_: models.User = Depends(get_current_user)):
    """Radar data built from real ablation rows, with bounded dimensions."""
    summary = metrics_service.as_summary()
    rows = summary["rows"]
    proposal = "attention" if "attention" in summary["models"] else (
        summary["models"][-1] if summary["models"] else ""
    )
    baseline = "baseline" if "baseline" in summary["models"] else proposal

    def score(model: str) -> list[float]:
        avg = metrics_service.average(model)
        if not avg:
            return [0.0] * 5
        return [
            round(avg.get("state_f1", 0.0) * 100, 1),
            round(avg.get("event_f1", 0.0) * 100, 1),
            round(avg.get("state_precision", 0.0) * 100, 1),
            round(avg.get("state_recall", 0.0) * 100, 1),
            round(max(0.0, 1.0 - min(avg.get("sae", 0.0), 1.0)) * 100, 1),
        ]

    return ok(
        {
            "indicators": [
                {"name": "State F1", "max": 100},
                {"name": "Event F1", "max": 100},
                {"name": "Precision", "max": 100},
                {"name": "Recall", "max": 100},
                {"name": "SAE Score", "max": 100},
            ],
            "series": [
                {"key": "baseline", "name": "Baseline", "value": score(baseline)},
                {"key": "proposed", "name": "Proposed", "value": score(proposal)},
            ],
            "models": {"baseline": baseline, "proposed": proposal},
            "per_appliance": rows,
            "samples": summary["samples"],
            "model_version": disagg_service.version,
            "ablation_csv": str(Path(settings.model_dir) / "ablation_metrics.csv"),
        }
    )


@router.get("/analytics/evaluation")
def evaluation(user: models.User = Depends(get_current_user)):
    return reports(user)
