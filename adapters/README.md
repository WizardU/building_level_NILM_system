# Adapters

## Replay (supported)

`adapters/replay/` streams the real UK-DALE day produced by
`ml/preprocess/ukdale.py` into the backend:

```bash
python -m adapters.replay.cli --meter-id 101 --speed 20
```

It is the only adapter used by the demo and by `scripts/demo_web.ps1` /
`demo_mobile.ps1`. The NPZ path defaults to
`data/processed/replay/ukdale_house1_day1.npz`, falling back to the synthetic
file only if the real one is missing.

## MQTT / Modbus (experimental, no hardware validation)

`adapters/modbus_mqtt/sources.py` contains two optional sources:

| Source | Env | Dependency |
|--------|-----|------------|
| `MqttSource` | `MQTT_HOST`, `MQTT_PORT`, `MQTT_TOPIC` | `paho-mqtt` |
| `ModbusTcpSource` | `MODBUS_HOST`, `MODBUS_PORT`, `MODBUS_UNIT`, `MODBUS_ADDRESS`, `MODBUS_SCALE` | `pymodbus` |

They implement the `MeterSource` interface (`read()` → `MeterSample`) but have
**not** been tested against physical meters. No reconnect/backpressure logic is
included yet; treat them as integration stubs. Choose one with
`METER_SOURCE=mqtt|modbus|replay`.

## Adding a source

1. Subclass `adapters.base.MeterSource` and implement `read()`.
2. Return `MeterSample(timestamp, power_w, voltage)`.
3. Register it in `adapters.modbus_mqtt.sources.create_source`.
4. Push batches to `POST /api/v1/measurements/upload` (or reuse the replay CLI
   pattern).
