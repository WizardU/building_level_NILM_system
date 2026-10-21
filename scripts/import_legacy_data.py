"""Import Nilm.rar CSV demo data into the FastAPI backend database.

This lets you train models with ml/legacy_nilm, then view the disaggregation
results in the Vue web console.

Prerequisites:
  1. cd ml/legacy_nilm && python make_demo_data.py
  2. cd ml/legacy_nilm && python train.py --appliance kettle --model seq2point --epochs 6
     (and optionally microwave / washing_machine / fridge)
  3. Start backend so the demo building/meter/appliances are seeded.
  4. python scripts/import_legacy_data.py

Then open http://localhost:3000 and click "刷新分解".
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.db import SessionLocal  # noqa: E402
from app import models  # noqa: E402

LEGACY_DATA = ROOT / "ml" / "legacy_nilm" / "data" / "mains.csv"
METER_ID = 101
BATCH_SIZE = 500


def main() -> None:
    if not LEGACY_DATA.exists():
        raise SystemExit(
            f"Missing {LEGACY_DATA}. Run: cd ml/legacy_nilm && python make_demo_data.py"
        )

    df = pd.read_csv(LEGACY_DATA, parse_dates=["time"])
    print(f"Importing {len(df)} samples from {LEGACY_DATA}")

    db = SessionLocal()
    try:
        meter = db.get(models.Meter, METER_ID)
        if not meter:
            raise SystemExit(f"Meter {METER_ID} not found. Start backend first to seed demo data.")

        # Clear existing measurements for this meter to avoid duplicates
        db.query(models.Measurement).filter_by(meter_id=METER_ID).delete()
        db.commit()

        samples = []
        for _, row in df.iterrows():
            ts = row["time"].to_pydatetime()
            if pd.isna(ts):
                continue
            power_w = float(row["mains"])
            samples.append(
                models.Measurement(
                    meter_id=METER_ID,
                    timestamp=ts,
                    power_w=power_w,
                    voltage_a=220.0,
                    current_a=power_w / 220.0,
                )
            )
            if len(samples) >= BATCH_SIZE:
                db.bulk_save_objects(samples)
                db.commit()
                samples.clear()

        if samples:
            db.bulk_save_objects(samples)
            db.commit()

        meter.last_power_kw = float(df["mains"].iloc[-1] / 1000.0)
        meter.last_seen = df["time"].iloc[-1].to_pydatetime()
        db.commit()

        print(f"Imported {len(df)} measurements into meter {METER_ID}")
        print("Open http://localhost:3000 and click 刷新分解")
    finally:
        db.close()


if __name__ == "__main__":
    main()
