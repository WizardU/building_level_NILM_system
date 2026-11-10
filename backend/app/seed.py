"""Seed demo building hierarchy, admin user and an initial real-data window."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
from sqlalchemy.orm import Session

from app import models
from app.config import ROOT, settings
from app.security import hash_password
from app.services.inference import APPLIANCE_LABELS

logger = logging.getLogger(__name__)

DEMO_APPLIANCES = [
    ("fridge", 0.15),
    ("kettle", 1.8),
    ("microwave", 1.2),
    ("dishwasher", 0.9),
    ("washing_machine", 0.5),
]

# The replayed day is 86,400 s at 6 s resolution -> 14,400 samples.
SEED_MAX_SAMPLES = 14400


def _replay_npz() -> Path | None:
    manifest_path = Path(settings.data_dir) / "processed" / "dataset_manifest.json"
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            # Only preload a real dataset; synthetic demo data is seeded separately.
            if str(manifest.get("dataset", "")).startswith("ukdale"):
                replay = manifest.get("replay")
                if replay:
                    path = ROOT / replay
                    if path.exists():
                        return path
        except (json.JSONDecodeError, OSError):
            pass
    return None


def _timestamps(data, count: int) -> list[datetime]:
    """Rebase the dataset's timestamps so the window ends at 'now'.

    UK-DALE timestamps are from 2014; the dashboard queries the last hours, so
    the seeded window must be shifted onto the current clock while keeping the
    original 6 s spacing.
    """
    now = datetime.now(timezone.utc).replace(tzinfo=None, microsecond=0)
    if "timestamps" in data:
        ns = data["timestamps"][-count:].astype("int64")
        if len(ns):
            end = datetime.fromtimestamp(int(ns[-1]) / 1e9, tz=timezone.utc).replace(
                tzinfo=None
            )
            shift = now - end
            return [
                datetime.fromtimestamp(int(value) / 1e9, tz=timezone.utc).replace(
                    tzinfo=None
                )
                + shift
                for value in ns
            ]
    return [now - timedelta(seconds=count - 1 - i) for i in range(count)]


def _seed_real_replay(db: Session, meter: models.Meter) -> int:
    npz = _replay_npz()
    if npz is None:
        return 0
    data = np.load(npz)
    aggregate = np.asarray(data["aggregate"], dtype=np.float32)
    count = min(len(aggregate), SEED_MAX_SAMPLES)
    if count <= 0:
        return 0
    aggregate = aggregate[-count:]
    stamps = _timestamps(data, len(data["aggregate"]))[-count:]
    rows = [
        {
            "meter_id": meter.id,
            "timestamp": stamps[i],
            "power_w": float(aggregate[i]),
            "voltage_a": 230.0,
            "current_a": float(aggregate[i] / 230.0),
        }
        for i in range(count)
    ]
    for start in range(0, len(rows), 5000):
        db.bulk_insert_mappings(models.Measurement, rows[start : start + 5000])
    meter.last_power_kw = float(aggregate[-1] / 1000.0)
    meter.last_seen = stamps[-1]
    logger.info("seeded %s real samples from %s", count, npz.name)
    return count


def _seed_synthetic(db: Session, meter: models.Meter) -> int:
    now = datetime.now(timezone.utc).replace(tzinfo=None, microsecond=0)
    count = 1800
    t0 = now - timedelta(seconds=count)
    rng = np.random.default_rng(0)
    fridge = np.where((np.arange(count) % 3600) < 1200, 120.0, 0.0)
    kettle = np.zeros(count)
    kettle[600:690] = 1800
    kettle[1200:1280] = 1800
    dish = np.zeros(count)
    dish[900:1500] = 900
    power = 80 + rng.normal(0, 3, count) + fridge + kettle + dish
    rows = [
        {
            "meter_id": meter.id,
            "timestamp": t0 + timedelta(seconds=i),
            "power_w": float(power[i]),
            "voltage_a": 230.0,
            "current_a": float(power[i] / 230.0),
        }
        for i in range(count)
    ]
    for start in range(0, len(rows), 5000):
        db.bulk_insert_mappings(models.Measurement, rows[start : start + 5000])
    meter.last_power_kw = float(power[-1] / 1000.0)
    meter.last_seen = now
    return count


def seed_demo(db: Session) -> None:
    if db.query(models.User).filter_by(username="admin").first():
        return

    admin = models.User(
        username="admin",
        password_hash=hash_password("admin123"),
        role="system_admin",
    )
    db.add(admin)

    building = models.Building(
        id=1,
        name="Building A · UK-DALE House 1",
        address="Demo Campus No.1",
        floors_count=1,
        status="online",
    )
    db.add(building)
    db.flush()

    floor = models.Floor(id=1, building_id=1, floor_number=1, name="Floor 1")
    db.add(floor)
    db.flush()

    zone = models.Zone(id=1, floor_id=1, name="Kitchen", type="kitchen")
    db.add(zone)
    db.flush()

    meter = models.Meter(
        id=101,
        name="UK-DALE House 1 · Mains",
        type="single_phase",
        building_id=1,
        floor_id=1,
        zone_id=1,
        sampling_rate_hz=1,
        protocol="replay",
        status="online",
        last_seen=datetime.now(timezone.utc).replace(tzinfo=None),
        last_power_kw=0.0,
    )
    db.add(meter)
    db.flush()

    for appliance_id, (appliance_type, rated) in enumerate(DEMO_APPLIANCES, start=201):
        db.add(
            models.Appliance(
                id=appliance_id,
                name=APPLIANCE_LABELS.get(appliance_type, appliance_type),
                type=appliance_type,
                meter_id=meter.id,
                zone_id=zone.id,
                rated_power_kw=rated,
            )
        )

    seeded = _seed_real_replay(db, meter)
    if seeded == 0:
        seeded = _seed_synthetic(db, meter)

    db.add(
        models.Alert(
            building_id=1,
            type="info",
            title="系统已就绪",
            message=f"已预载 {seeded} 条真实 UK-DALE 样本，可启动 replay 适配器继续推送。",
            title_en="System Ready",
            message_en=(
                f"Preloaded {seeded} real UK-DALE samples. "
                "Start the replay adapter to continue streaming."
            ),
            status="open",
            dedupe_key="system_ready",
        )
    )
    db.commit()
