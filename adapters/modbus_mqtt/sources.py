"""Optional real-meter adapters (stubs + config-driven)."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone

from adapters.base import MeterSample, MeterSource


class MqttSource(MeterSource):
    """
    Subscribe to MQTT topic; payload JSON: {"power_w": float, "voltage": float}.
    Requires `paho-mqtt` when enabled.
    """

    def __init__(
        self,
        host: str | None = None,
        topic: str | None = None,
        port: int = 1883,
    ):
        self.host = host or os.getenv("MQTT_HOST", "127.0.0.1")
        self.topic = topic or os.getenv("MQTT_TOPIC", "nilm/meter/101")
        self.port = int(os.getenv("MQTT_PORT", port))
        self._queue: list[MeterSample] = []
        self._client = None
        self._connect()

    def _connect(self) -> None:
        try:
            import paho.mqtt.client as mqtt
        except ImportError as e:
            raise ImportError("Install paho-mqtt to use MqttSource") from e

        def on_message(_c, _u, msg):
            try:
                data = json.loads(msg.payload.decode("utf-8"))
                pw = float(data.get("power_w", data.get("power", 0)))
                volt = float(data.get("voltage", 220.0))
                self._queue.append(
                    MeterSample(timestamp=datetime.now(timezone.utc), power_w=pw, voltage=volt)
                )
            except Exception:
                pass

        self._client = mqtt.Client()
        self._client.on_message = on_message
        self._client.connect(self.host, self.port, 60)
        self._client.subscribe(self.topic)
        self._client.loop_start()

    def read(self) -> MeterSample | None:
        if not self._queue:
            return None
        return self._queue.pop(0)

    def close(self) -> None:
        if self._client:
            self._client.loop_stop()
            self._client.disconnect()


class ModbusTcpSource(MeterSource):
    """
    Read holding registers from a Modbus TCP power meter.
    Default mapping: register 0 = power watts (uint16), scale from env.
    Requires `pymodbus` when enabled.
    """

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        unit: int = 1,
        address: int = 0,
        scale: float = 1.0,
    ):
        self.host = host or os.getenv("MODBUS_HOST", "127.0.0.1")
        self.port = int(port or os.getenv("MODBUS_PORT", "502"))
        self.unit = int(os.getenv("MODBUS_UNIT", unit))
        self.address = int(os.getenv("MODBUS_ADDRESS", address))
        self.scale = float(os.getenv("MODBUS_SCALE", scale))
        self._client = None

    def _ensure(self):
        if self._client is not None:
            return
        try:
            from pymodbus.client import ModbusTcpClient
        except ImportError as e:
            raise ImportError("Install pymodbus to use ModbusTcpSource") from e
        self._client = ModbusTcpClient(self.host, port=self.port)
        if not self._client.connect():
            raise ConnectionError(f"Modbus connect failed: {self.host}:{self.port}")

    def read(self) -> MeterSample | None:
        self._ensure()
        rr = self._client.read_holding_registers(self.address, 1, slave=self.unit)
        if rr.isError():
            return None
        pw = float(rr.registers[0]) * self.scale
        return MeterSample(timestamp=datetime.now(timezone.utc), power_w=pw)

    def close(self) -> None:
        if self._client:
            self._client.close()


def create_source(kind: str | None = None) -> MeterSource:
    kind = (kind or os.getenv("METER_SOURCE", "replay")).lower()
    if kind == "mqtt":
        return MqttSource()
    if kind == "modbus":
        return ModbusTcpSource()
    from pathlib import Path

    from adapters.replay.source import ReplaySource

    root = Path(__file__).resolve().parents[2]
    npz = Path(os.getenv("REPLAY_NPZ", root / "data/processed/replay/synth_house1_day1.npz"))
    return ReplaySource(npz)
