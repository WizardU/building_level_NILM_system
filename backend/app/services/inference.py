"""Load ONNX models and run disaggregation; heuristic fallback if no models."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
from sqlalchemy.orm import Session

from app import models
from app.config import ROOT, settings

# Allow importing ml.inference when running from repo
ML_ROOT = ROOT / "ml"
if str(ML_ROOT) not in sys.path:
    sys.path.insert(0, str(ML_ROOT))

APPLIANCE_LABELS = {
    "fridge": "智能冰箱",
    "kettle": "电热水壶",
    "microwave": "微波炉",
    "dishwasher": "洗碗机",
    "washing_machine": "滚筒洗衣机",
}


from app.services.legacy_inference import LegacyInferenceEngine


class DisaggregationService:
    def __init__(self) -> None:
        self.engine = None
        self.legacy_engine = None
        self._try_load()

    def _try_load(self) -> None:
        # 1) prefer ONNX models from the main pipeline
        model_dir = Path(settings.model_dir)
        if model_dir.exists():
            try:
                from inference.engine import InferenceEngine

                eng = InferenceEngine(model_dir)
                if eng.appliances:
                    self.engine = eng
                    return
            except Exception:
                self.engine = None

        # 2) fallback to Nilm.rar PyTorch checkpoints
        try:
            legacy = LegacyInferenceEngine()
            if legacy.appliances:
                self.legacy_engine = legacy
        except Exception:
            self.legacy_engine = None

    def reload(self) -> None:
        self._try_load()

    def run(
        self,
        db: Session,
        meter_id: int,
        start: datetime,
        end: datetime,
        stride: int = 30,
    ) -> dict:
        q = (
            db.query(models.Measurement)
            .filter(
                models.Measurement.meter_id == meter_id,
                models.Measurement.timestamp >= start,
                models.Measurement.timestamp <= end,
            )
            .order_by(models.Measurement.timestamp.asc())
        )
        rows = q.all()
        apps_db = db.query(models.Appliance).filter(models.Appliance.meter_id == meter_id).all()
        type_to_app = {a.type: a for a in apps_db}

        if not rows:
            # synthetic short series for empty DB demo
            return self._empty_result(meter_id, start, end, apps_db)

        times = [r.timestamp for r in rows]
        agg = np.array([r.power_w for r in rows], dtype=np.float32)

        if self.engine and self.engine.appliances:
            series_map = self.engine.disaggregate_series(agg, stride=max(stride, 1))
            confidence = 0.94
        elif self.legacy_engine and self.legacy_engine.appliances:
            series_map = self.legacy_engine.disaggregate_series(agg)
            confidence = 0.88
        else:
            series_map = self._heuristic(agg)
            confidence = 0.75

        appliances_out = []
        total_energy = float(np.sum(agg) / 3600.0 / 1000.0)  # W·s → kWh approx at 1Hz
        for atype, series in series_map.items():
            app = type_to_app.get(atype)
            if app is None:
                continue
            # downsample series for API (max ~200 points)
            step = max(len(series) // 200, 1)
            pts = [
                {"timestamp": times[i].isoformat(), "power_kw": float(series[i] / 1000.0)}
                for i in range(0, len(series), step)
            ]
            energy = float(np.sum(series) / 3600.0 / 1000.0)
            runtime = float(np.mean(series > 50) * (len(series) / 3600.0))
            last_p = float(series[-1]) if len(series) else 0.0
            appliances_out.append(
                {
                    "appliance_id": app.id,
                    "type": atype,
                    "name": app.name,
                    "energy_kwh": round(energy, 4),
                    "percentage": 0.0,
                    "runtime_hours": round(runtime, 3),
                    "series": pts,
                    "power_w": round(last_p, 1),
                    "state": last_p > 50,
                    "confidence": confidence,
                }
            )

        energy_sum = sum(a["energy_kwh"] for a in appliances_out) or 1e-8
        for a in appliances_out:
            a["percentage"] = round(100.0 * a["energy_kwh"] / energy_sum, 1)

        step = max(len(agg) // 200, 1)
        mains_series = [
            {"timestamp": times[i].isoformat(), "power_kw": float(agg[i] / 1000.0)}
            for i in range(0, len(agg), step)
        ]
        period = start.date().isoformat()
        result = {
            "meter_id": meter_id,
            "period": period,
            "total_energy_kwh": round(total_energy, 4),
            "appliances": appliances_out,
            "mains_series": mains_series,
        }

        cache = (
            db.query(models.DisaggregationCache)
            .filter_by(meter_id=meter_id, period=period)
            .first()
        )
        payload = json.dumps(result)
        if cache:
            cache.payload_json = payload
        else:
            db.add(
                models.DisaggregationCache(
                    meter_id=meter_id, period=period, payload_json=payload
                )
            )
        db.commit()
        return result

    def _heuristic(self, agg: np.ndarray) -> dict[str, np.ndarray]:
        """Simple power-band heuristic when ONNX models are missing."""
        n = len(agg)
        fridge = np.where(agg > 100, 120.0, 0.0).astype(np.float32)
        kettle = np.where(agg > 1600, 1800.0, 0.0).astype(np.float32)
        dishwasher = np.where((agg > 800) & (agg < 1600), 900.0, 0.0).astype(np.float32)
        microwave = np.where((agg > 1100) & (agg < 1400), 1200.0, 0.0).astype(np.float32)
        washer = np.where((agg > 400) & (agg < 700), 500.0, 0.0).astype(np.float32)
        # dampen overlapping
        residual = np.clip(agg - fridge - kettle * 0.5, 0, None)
        return {
            "fridge": fridge,
            "kettle": kettle,
            "dishwasher": dishwasher * (residual > 0),
            "microwave": microwave,
            "washing_machine": washer,
        }

    def _empty_result(self, meter_id, start, end, apps_db) -> dict:
        return {
            "meter_id": meter_id,
            "period": start.date().isoformat(),
            "total_energy_kwh": 0.0,
            "appliances": [
                {
                    "appliance_id": a.id,
                    "type": a.type,
                    "name": a.name,
                    "energy_kwh": 0.0,
                    "percentage": 0.0,
                    "runtime_hours": 0.0,
                    "series": [],
                    "power_w": 0.0,
                    "state": False,
                    "confidence": 0.0,
                }
                for a in apps_db
            ],
            "mains_series": [],
        }


disagg_service = DisaggregationService()
