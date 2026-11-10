"""ONNX Runtime inference engine for N-to-1 Seq2Point models."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

try:
    import onnxruntime as ort
except ImportError:  # pragma: no cover
    ort = None

RANK = {"attention": 3, "proposed": 3, "dilated": 2, "baseline": 1, "seq2point": 1, "seq2seq": 1}


class InferenceEngine:
    """Loads one ONNX session per appliance and disaggregates power series."""

    def __init__(self, model_dir: str | Path, preferred: str = "attention", batch_size: int = 256):
        self.model_dir = Path(model_dir)
        self.preferred = preferred
        self.batch_size = batch_size
        self.sessions: dict[str, object] = {}
        self.meta: dict[str, dict] = {}
        self._load_all()

    def _load_all(self) -> None:
        if ort is None:
            return
        for meta_path in sorted(self.model_dir.glob("*.json")):
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            if not isinstance(meta, dict):
                continue  # ablation_metrics.json / training_runs.json are lists
            appliance = meta.get("appliance")
            if not appliance:
                continue
            onnx_path = self.model_dir / (meta.get("onnx") or meta_path.with_suffix(".onnx").name)
            if not onnx_path.exists():
                continue
            if appliance in self.meta:
                old = RANK.get(self.meta[appliance].get("model_name", ""), 0)
                new = RANK.get(meta.get("model_name", ""), 0)
                # Prefer the configured variant, then the highest ranked one.
                if meta.get("model_name") != self.preferred and new <= old:
                    continue
            options = ort.SessionOptions()
            options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            self.sessions[appliance] = ort.InferenceSession(
                str(onnx_path), sess_options=options, providers=["CPUExecutionProvider"]
            )
            meta["onnx_mtime"] = onnx_path.stat().st_mtime_ns
            self.meta[appliance] = meta

    @property
    def appliances(self) -> list[str]:
        return sorted(self.sessions.keys())

    @property
    def version(self) -> str:
        blob = "|".join(
            f"{a}:{self.meta[a].get('model_name')}:{self.meta[a].get('onnx_mtime')}"
            for a in self.appliances
        )
        return hashlib.sha1(blob.encode("utf-8")).hexdigest()[:12]

    @property
    def sample_period_s(self) -> int:
        periods = [int(m.get("sample_period_s", 1) or 1) for m in self.meta.values()]
        return max(periods) if periods else 1

    def threshold(self, appliance: str) -> float:
        value = self.meta.get(appliance, {}).get("on_threshold")
        return float(value) if value is not None else 50.0

    def predict_batch(self, appliance: str, windows: np.ndarray) -> np.ndarray:
        """windows: (N, W) raw aggregate watts -> (N,) appliance watts."""
        if appliance not in self.sessions:
            raise KeyError(appliance)
        meta = self.meta[appliance]
        stats = meta["stats"]
        expected = int(meta.get("window_size", 599))
        arr = np.asarray(windows, dtype=np.float32)
        if arr.ndim == 1:
            arr = arr[None, :]
        if arr.shape[1] != expected:
            raise ValueError(f"Expected window {expected}, got {arr.shape[1]}")

        normalized = (arr - stats["agg_mean"]) / stats["agg_std"]
        session = self.sessions[appliance]
        outputs = []
        for start in range(0, len(normalized), self.batch_size):
            chunk = normalized[start : start + self.batch_size]
            result = session.run(None, {"aggregate": chunk})[0]
            outputs.append(np.asarray(result).reshape(-1))
        y = np.concatenate(outputs) * stats["y_std"] + stats["y_mean"]
        return np.clip(y, 0.0, None).astype(np.float32)

    def predict_point(self, appliance: str, window: np.ndarray) -> float:
        return float(self.predict_batch(appliance, np.asarray(window).reshape(1, -1))[0])

    def disaggregate_series(
        self,
        aggregate: np.ndarray,
        appliances: list[str] | None = None,
        stride: int = 1,
    ) -> dict[str, np.ndarray]:
        apps = appliances or self.appliances
        agg = np.asarray(aggregate, dtype=np.float32)
        result: dict[str, np.ndarray] = {}
        for app in apps:
            if app not in self.sessions:
                continue
            window = int(self.meta[app].get("window_size", 599))
            half = window // 2
            stride = max(int(stride), 1)
            if len(agg) < window:
                # Too short to slide: pad by edge replication.
                padded = np.pad(agg, (half, half), mode="edge")
                starts = np.array([0], dtype=np.int64)
                windows = padded[None, :window]
            else:
                starts = np.arange(half, len(agg) - half, stride, dtype=np.int64)
                windows = np.lib.stride_tricks.sliding_window_view(agg, window)[
                    starts - half
                ]
            values = self.predict_batch(app, windows)
            out = np.zeros(len(agg), dtype=np.float32)
            out[starts] = values
            if len(starts) == 0:
                result[app] = out
                continue
            # Hold the first/last prediction constant outside the valid region.
            if starts[0] > 0:
                out[: starts[0]] = values[0]
            if starts[-1] + 1 < len(out):
                out[starts[-1] + 1 :] = values[-1]
            # Fill gaps between stride steps by linear interpolation.
            if stride > 1 and len(starts) > 1:
                idx = np.arange(len(out))
                out = np.interp(idx, starts, values).astype(np.float32)
            result[app] = out
        return result
