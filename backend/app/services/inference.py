"""Load ONNX models and run disaggregation; heuristic fallback if no models."""

from __future__ import annotations

import json
import logging
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
from sqlalchemy.orm import Session

from app import models
from app.config import ROOT, settings

logger = logging.getLogger(__name__)

# Allow importing ml.inference when running from the repo (and /ml in Docker).
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

EPOCH = datetime(1970, 1, 1)


def _seconds(times: list[datetime]) -> np.ndarray:
    return np.array([(t - EPOCH).total_seconds() for t in times], dtype="float64")


def integrate_kwh(power_w: np.ndarray, times: list[datetime]) -> float:
    """Trapezoidal-ish energy using the real sampling interval (kWh)."""
    if len(power_w) < 2 or len(times) < 2:
        return 0.0
    seconds = _seconds(times)
    dt = np.diff(seconds)
    dt = np.clip(dt, 0.0, 60.0)
    return float(np.sum(np.asarray(power_w[:-1], dtype="float64") * dt) / 3.6e6)


class DisaggregationService:
    def __init__(self) -> None:
        self.engine = None
        self.legacy_engine = None
        self.backend = "heuristic"
        self.version = "heuristic"
        self._try_load()

    def _try_load(self) -> None:
        self.engine = None
        self.legacy_engine = None
        self.backend = "heuristic"
        self.version = "heuristic"

        # 1) ONNX models from the main pipeline
        model_dir = Path(settings.model_dir)
        if model_dir.exists():
            try:
                from inference.engine import InferenceEngine

                engine = InferenceEngine(model_dir, preferred=settings.model_preferred)
                if engine.appliances:
                    self.engine = engine
                    self.backend = "onnx"
                    self.version = engine.version
                    return
            except Exception as exc:  # noqa: BLE001 - fall back, but never hide it
                logger.warning("ONNX engine unavailable: %s", exc)

        # 2) legacy PyTorch checkpoints from the bundled reference project
        try:
            from app.services.legacy_inference import LegacyInferenceEngine

            legacy = LegacyInferenceEngine()
            if legacy.appliances:
                self.legacy_engine = legacy
                self.backend = "torch-legacy"
                self.version = "legacy"
        except Exception as exc:  # noqa: BLE001
            logger.info("legacy engine unavailable: %s", exc)

    def reload(self) -> None:
        self._try_load()

    def status(self) -> dict:
        engine = self.engine
        first_meta = engine.meta.get(engine.appliances[0], {}) if engine and engine.appliances else {}
        return {
            "backend": self.backend,
            "model_version": self.version,
            "model_dir": str(Path(settings.model_dir)),
            "appliances": engine.appliances if engine else [],
            "sample_period_s": engine.sample_period_s if engine else 1,
            "window_size": int(first_meta.get("window_size", 599)),
            "dataset": first_meta.get("dataset", ""),
            "model_name": first_meta.get("model_name", ""),
        }

    def threshold(self, appliance: str) -> float:
        if self.engine:
            return self.engine.threshold(appliance)
        return 50.0

    def cache_key(self, meter_id: int, start: datetime, end: datetime) -> str:
        return (
            f"{meter_id}|{start:%Y%m%dT%H%M%S}|{end:%Y%m%dT%H%M%S}|{self.version}"
        )

    def get_cached(self, db: Session, meter_id: int, start: datetime, end: datetime) -> dict | None:
        key = self.cache_key(meter_id, start, end)
        row = (
            db.query(models.DisaggregationCache)
            .filter_by(meter_id=meter_id, period=key)
            .first()
        )
        return json.loads(row.payload_json) if row else None

    def latest_cached(self, db: Session, meter_id: int) -> dict | None:
        row = (
            db.query(models.DisaggregationCache)
            .filter_by(meter_id=meter_id)
            .order_by(models.DisaggregationCache.created_at.desc())
            .first()
        )
        return json.loads(row.payload_json) if row else None

    def run(
        self,
        db: Session,
        meter_id: int,
        start: datetime,
        end: datetime,
        stride: int = 30,
    ) -> dict:
        rows = (
            db.query(models.Measurement)
            .filter(
                models.Measurement.meter_id == meter_id,
                models.Measurement.timestamp >= start,
                models.Measurement.timestamp <= end,
            )
            .order_by(models.Measurement.timestamp.asc())
            .all()
        )
        apps_db = db.query(models.Appliance).filter(models.Appliance.meter_id == meter_id).all()
        type_to_app = {a.type: a for a in apps_db}

        if not rows:
            return self._empty_result(meter_id, start, end, apps_db)

        times = [r.timestamp for r in rows]
        agg = np.array([r.power_w for r in rows], dtype=np.float32)

        inference_started = time.perf_counter()
        if self.engine and self.engine.appliances:
            series_map = self.engine.disaggregate_series(agg, stride=max(stride, 1))
            confidence = 0.9
        elif self.legacy_engine and self.legacy_engine.appliances:
            series_map = self.legacy_engine.disaggregate_series(agg)
            confidence = 0.8
        else:
            series_map = self._heuristic(agg)
            confidence = 0.5
        inference_ms = round((time.perf_counter() - inference_started) * 1000.0, 2)

        total_energy = integrate_kwh(agg, times)
        appliances_out = []
        for atype, series in series_map.items():
            app = type_to_app.get(atype)
            if app is None:
                continue
            threshold = self.threshold(atype)
            energy = integrate_kwh(series, times)
            runtime = float(np.mean(series > threshold) * (len(series) / 3600.0))
            last_p = float(series[-1]) if len(series) else 0.0
            step = max(len(series) // 240, 1)
            points = [
                {"timestamp": times[i].isoformat() + "Z", "power_kw": float(series[i] / 1000.0)}
                for i in range(0, len(series), step)
            ]
            model_conf = confidence
            if self.engine:
                metrics = self.engine.meta.get(atype, {}).get("metrics", {})
                model_conf = float(metrics.get("event_f1", metrics.get("state_f1", confidence)))
            appliances_out.append(
                {
                    "appliance_id": app.id,
                    "type": atype,
                    "name": app.name,
                    "energy_kwh": round(energy, 4),
                    "percentage": 0.0,
                    "runtime_hours": round(runtime, 3),
                    "series": points,
                    "power_w": round(last_p, 1),
                    "state": bool(last_p > threshold),
                    "confidence": round(model_conf, 3),
                    "threshold_w": round(threshold, 1),
                }
            )

        energy_sum = sum(a["energy_kwh"] for a in appliances_out) or 1e-8
        for appliance in appliances_out:
            appliance["percentage"] = round(100.0 * appliance["energy_kwh"] / energy_sum, 1)

        step = max(len(agg) // 240, 1)
        mains_series = [
            {"timestamp": times[i].isoformat() + "Z", "power_kw": float(agg[i] / 1000.0)}
            for i in range(0, len(agg), step)
        ]
        result = {
            "meter_id": meter_id,
            "period": start.date().isoformat(),
            "start": start.isoformat() + "Z",
            "end": end.isoformat() + "Z",
            "model_version": self.version,
            "backend": self.backend,
            "sample_period_s": (
                self.engine.sample_period_s if self.engine else 1
            ),
            "inference_ms": inference_ms,
            "total_energy_kwh": round(total_energy, 4),
            "appliances": appliances_out,
            "mains_series": mains_series,
        }

        key = self.cache_key(meter_id, start, end)
        payload = json.dumps(result)
        cache = (
            db.query(models.DisaggregationCache)
            .filter_by(meter_id=meter_id, period=key)
            .first()
        )
        if cache:
            cache.payload_json = payload
            cache.created_at = datetime.utcnow()
        else:
            db.add(
                models.DisaggregationCache(meter_id=meter_id, period=key, payload_json=payload)
            )
        db.commit()
        return result

    def _heuristic(self, agg: np.ndarray) -> dict[str, np.ndarray]:
        """Simple power-band heuristic when ONNX models are missing."""
        fridge = np.where(agg > 100, 120.0, 0.0).astype(np.float32)
        kettle = np.where(agg > 1600, 1800.0, 0.0).astype(np.float32)
        dishwasher = np.where((agg > 800) & (agg < 1600), 900.0, 0.0).astype(np.float32)
        microwave = np.where((agg > 1100) & (agg < 1400), 1200.0, 0.0).astype(np.float32)
        washer = np.where((agg > 400) & (agg < 700), 500.0, 0.0).astype(np.float32)
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
            "start": start.isoformat() + "Z",
            "end": end.isoformat() + "Z",
            "model_version": self.version,
            "backend": self.backend,
            "sample_period_s": 1,
            "inference_ms": 0.0,
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
                    "threshold_w": 0.0,
                }
                for a in apps_db
            ],
            "mains_series": [],
        }


disagg_service = DisaggregationService()
