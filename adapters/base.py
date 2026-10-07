"""Pluggable meter data sources."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass
class MeterSample:
    timestamp: datetime
    power_w: float
    voltage: float = 220.0
    current: float = 0.0

    def to_api(self) -> dict:
        kw = self.power_w / 1000.0
        cur = self.current or (self.power_w / self.voltage if self.voltage else 0)
        phase = {"voltage": self.voltage, "current": cur, "power_kw": kw}
        return {
            "timestamp": self.timestamp.isoformat(),
            "phase_a": phase,
            "phase_b": {"voltage": self.voltage, "current": 0.0, "power_kw": 0.0},
            "phase_c": {"voltage": self.voltage, "current": 0.0, "power_kw": 0.0},
            "power_w": self.power_w,
        }


class MeterSource(ABC):
    @abstractmethod
    def read(self) -> MeterSample | None:
        """Return next sample or None when exhausted."""

    def close(self) -> None:
        return None
