"""Seed demo building hierarchy and admin user."""

from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np
from sqlalchemy.orm import Session

from app import models
from app.security import hash_password
from app.services.inference import APPLIANCE_LABELS


DEMO_APPLIANCES = [
    ("fridge", 0.15),
    ("kettle", 1.8),
    ("microwave", 1.2),
    ("dishwasher", 0.9),
    ("washing_machine", 0.5),
]


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
        name="Building A",
        address="Demo Campus No.1",
        floors_count=1,
        status="online",
    )
    db.add(building)
    db.flush()

    floor = models.Floor(id=1, building_id=1, floor_number=1, name="Floor 1")
    db.add(floor)
    db.flush()

    zone = models.Zone(id=1, floor_id=1, name="Office Zone A", type="office")
    db.add(zone)
    db.flush()

    meter = models.Meter(
        id=101,
        name="Building A - Floor 1 Main Meter",
        type="three_phase",
        building_id=1,
        floor_id=1,
        zone_id=1,
        sampling_rate_hz=1,
        protocol="http",
        status="online",
        last_seen=datetime.utcnow(),
        last_power_kw=0.0,
    )
    db.add(meter)
    db.flush()

    for i, (atype, rated) in enumerate(DEMO_APPLIANCES, start=201):
        db.add(
            models.Appliance(
                id=i,
                name=APPLIANCE_LABELS.get(atype, atype),
                type=atype,
                meter_id=101,
                zone_id=1,
                rated_power_kw=rated,
            )
        )

    # Seed ~30 minutes of synthetic measurements for immediate dashboard
    now = datetime.utcnow().replace(microsecond=0)
    n = 1800
    t0 = now - timedelta(seconds=n)
    rng = np.random.default_rng(0)
    fridge = np.where((np.arange(n) % 3600) < 1200, 120.0, 0.0)
    kettle = np.zeros(n)
    kettle[600:690] = 1800
    kettle[1200:1280] = 1800
    dish = np.zeros(n)
    dish[900:1500] = 900
    base = 80 + rng.normal(0, 3, n)
    power = base + fridge + kettle + dish
    for i in range(n):
        db.add(
            models.Measurement(
                meter_id=101,
                timestamp=t0 + timedelta(seconds=i),
                power_w=float(power[i]),
                voltage_a=220.0,
                current_a=float(power[i] / 220.0),
            )
        )
    meter.last_power_kw = float(power[-1] / 1000.0)
    meter.last_seen = now

    db.add(
        models.Alert(
            building_id=1,
            type="warning",
            title="系统已就绪",
            message="Demo 建筑已播种，可启动 replay 适配器推送实时数据。",
            status="open",
        )
    )
    db.commit()
