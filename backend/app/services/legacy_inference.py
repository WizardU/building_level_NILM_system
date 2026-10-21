"""Adapter to run Nilm.rar PyTorch models inside the FastAPI demo.

Nilm.rar uses:
  - window size = 99
  - normalization = divide by MAX_POWER (3000.0)
  - models: Seq2PointCNN / Seq2SeqLSTM

This adapter converts between the demo's aggregate series (watts, any length)
and the legacy model's expected input, then returns appliance power series
in the same format as the ONNX inference engine.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

try:
    import torch
except ImportError:  # pragma: no cover - backend venv is not required to have torch
    torch = None  # type: ignore[assignment]

# Make ml/legacy_nilm importable from backend
LEGACY_ROOT = Path(__file__).resolve().parents[3] / "ml" / "legacy_nilm"
if str(LEGACY_ROOT) not in sys.path:
    sys.path.insert(0, str(LEGACY_ROOT))

if torch is None:
    disaggregate = None  # type: ignore[assignment]
    build_model = None  # type: ignore[assignment]
else:
    from disaggregate import disaggregate  # noqa: E402
    from models import build_model  # noqa: E402

MAX_POWER = 3000.0
WINDOW = 99
STRIDE = 4

# Map legacy appliance names to demo appliance names
APPLIANCE_MAP = {
    "kettle": "kettle",
    "microwave": "microwave",
    "washing_machine": "washing_machine",
    "fridge": "fridge",
}


class LegacyInferenceEngine:
    """Loads Nilm.rar .pt checkpoints and disaggregates aggregate power series."""

    def __init__(self, checkpoint_dir: str | Path | None = None):
        self.checkpoint_dir = Path(checkpoint_dir or LEGACY_ROOT / "outputs" / "checkpoints")
        self.models: dict[str, torch.nn.Module] = {}
        self.windows: dict[str, int] = {}
        self.thresholds: dict[str, float] = {}
        if torch is None:
            return
        self._load_all()

    def _load_all(self) -> None:
        if not self.checkpoint_dir.exists():
            return
        for app in APPLIANCE_MAP.keys():
            ckpt_path = self.checkpoint_dir / f"{app}_seq2point.pt"
            if not ckpt_path.exists():
                continue
            ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
            cfg = ckpt.get("config", {})
            model_name = cfg.get("model", "seq2point")
            window = int(cfg.get("window", WINDOW))
            model = build_model(model_name, window)
            model.load_state_dict(ckpt["state_dict"])
            model.eval()
            self.models[app] = model
            self.windows[app] = window
            self.thresholds[app] = float(cfg.get("on_threshold", 50.0))

    @property
    def appliances(self) -> list[str]:
        return sorted(self.models.keys())

    def predict_series(self, appliance: str, aggregate: np.ndarray) -> np.ndarray:
        """Run legacy disaggregation on a raw aggregate power series (watts)."""
        if appliance not in self.models:
            raise KeyError(f"No legacy model for {appliance}")
        model = self.models[appliance]
        cfg_window = self.windows.get(appliance, WINDOW)
        # disaggregate from legacy expects normalized-by-MAX_POWER inside
        return disaggregate(
            aggregate,
            model,
            window=cfg_window,
            max_power=MAX_POWER,
            stride=STRIDE,
            device="cpu",
        )

    def disaggregate_series(
        self,
        aggregate: np.ndarray,
        appliances: list[str] | None = None,
        stride: int = 1,  # noqa: ARG002
    ) -> dict[str, np.ndarray]:
        apps = appliances or self.appliances
        result = {}
        for app in apps:
            if app not in self.models:
                continue
            result[app] = self.predict_series(app, aggregate)
        return result
