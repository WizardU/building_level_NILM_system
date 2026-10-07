"""ONNX Runtime inference engine for N-to-1 Seq2Point models."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

try:
    import onnxruntime as ort
except ImportError:  # pragma: no cover
    ort = None


class InferenceEngine:
    def __init__(self, model_dir: str | Path, preferred: str = "attention"):
        self.model_dir = Path(model_dir)
        self.preferred = preferred
        self.sessions: dict[str, object] = {}
        self.meta: dict[str, dict] = {}
        self._load_all()

    def _load_all(self) -> None:
        if ort is None:
            return
        for meta_path in self.model_dir.glob("*.json"):
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            app = meta["appliance"]
            onnx_name = meta.get("onnx") or meta_path.with_suffix(".onnx").name
            onnx_path = self.model_dir / onnx_name
            if not onnx_path.exists():
                continue
            # Prefer attention / proposed over baseline when multiple exist
            if app in self.meta:
                rank = {"attention": 3, "proposed": 3, "dilated": 2, "baseline": 1, "seq2point": 1}
                old = rank.get(self.meta[app].get("model_name", ""), 0)
                new = rank.get(meta.get("model_name", ""), 0)
                if new < old:
                    continue
            self.sessions[app] = ort.InferenceSession(
                str(onnx_path), providers=["CPUExecutionProvider"]
            )
            self.meta[app] = meta

    @property
    def appliances(self) -> list[str]:
        return sorted(self.sessions.keys())

    def predict_point(self, appliance: str, window: np.ndarray) -> float:
        """window: shape (W,) aggregate watts (raw)."""
        if appliance not in self.sessions:
            raise KeyError(appliance)
        stats = self.meta[appliance]["stats"]
        w = self.meta[appliance].get("window_size", 599)
        x = np.asarray(window, dtype=np.float32).reshape(-1)
        if len(x) != w:
            raise ValueError(f"Expected window {w}, got {len(x)}")
        xn = (x - stats["agg_mean"]) / stats["agg_std"]
        out = self.sessions[appliance].run(None, {"aggregate": xn.reshape(1, -1)})[0]
        y = float(out.reshape(-1)[0]) * stats["y_std"] + stats["y_mean"]
        return max(y, 0.0)

    def disaggregate_series(
        self,
        aggregate: np.ndarray,
        appliances: list[str] | None = None,
        stride: int = 1,
    ) -> dict[str, np.ndarray]:
        apps = appliances or self.appliances
        agg = np.asarray(aggregate, dtype=np.float32)
        result = {}
        for app in apps:
            if app not in self.sessions:
                continue
            w = int(self.meta[app].get("window_size", 599))
            half = w // 2
            out = np.zeros(len(agg), dtype=np.float32)
            counts = np.zeros(len(agg), dtype=np.float32)
            for t in range(half, len(agg) - half, stride):
                p = self.predict_point(app, agg[t - half : t + half + 1])
                out[t] = p
                counts[t] = 1
            # fill edges by nearest
            if counts.any():
                idx = np.where(counts > 0)[0]
                for i in range(len(agg)):
                    if counts[i] == 0:
                        j = idx[np.argmin(np.abs(idx - i))]
                        out[i] = out[j]
            result[app] = out
        return result
