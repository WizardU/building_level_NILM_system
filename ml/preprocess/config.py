from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

WINDOW_SIZE = 599
SAMPLE_RATE_HZ = 1
STRIDE_TRAIN = 16
STRIDE_EVAL = 599

# Target appliances (Type I–II coverage for thesis experiments)
APPLIANCES = [
    "fridge",
    "kettle",
    "microwave",
    "dishwasher",
    "washing_machine",
]

# On-threshold (watts) for Acc/F1
ON_THRESHOLDS = {
    "fridge": 50.0,
    "kettle": 500.0,
    "microwave": 200.0,
    "dishwasher": 100.0,
    "washing_machine": 100.0,
}

# Synthetic generator defaults (watts)
SYNTH_PROFILES = {
    "fridge": {"on_power": 120.0, "cycle_on": 20 * 60, "cycle_off": 40 * 60},
    "kettle": {"on_power": 1800.0, "burst_len": 90, "bursts_per_day": 6},
    "microwave": {"on_power": 1200.0, "burst_len": 60, "bursts_per_day": 4},
    "dishwasher": {"on_power": 900.0, "burst_len": 45 * 60, "bursts_per_day": 1},
    "washing_machine": {"on_power": 500.0, "burst_len": 60 * 60, "bursts_per_day": 1},
}
