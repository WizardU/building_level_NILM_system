from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from adapters.base import MeterSample, MeterSource


class ReplaySource(MeterSource):
    """Replay aggregate power from NPZ produced by preprocess."""

    def __init__(self, npz_path: Path, loop: bool = True):
        data = np.load(npz_path)
        self.aggregate = data["aggregate"].astype(np.float32)
        self.idx = 0
        self.loop = loop

    def read(self) -> MeterSample | None:
        if self.idx >= len(self.aggregate):
            if not self.loop:
                return None
            self.idx = 0
        pw = float(self.aggregate[self.idx])
        self.idx += 1
        return MeterSample(timestamp=datetime.now(timezone.utc), power_w=pw)
