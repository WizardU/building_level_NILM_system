from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

WINDOW_SIZE = 599
SAMPLE_RATE_HZ = 1
# UK-DALE's NILMTK HDF5 stores every channel at 6 s resolution.
SAMPLE_PERIOD_S = 6
STRIDE_TRAIN = 30
STRIDE_EVAL = 30

# Target appliances (Type I–II coverage for thesis experiments)
APPLIANCES = [
    "fridge",
    "kettle",
    "microwave",
    "dishwasher",
    "washing_machine",
]

# On-threshold (watts) for Acc/F1. Values follow common NILM practice and the
# UK-DALE metadata (on_power_threshold) where available.
ON_THRESHOLDS = {
    "fridge": 50.0,
    "kettle": 500.0,
    "microwave": 200.0,
    "dishwasher": 100.0,
    "washing_machine": 100.0,
}

# Official UK-DALE channel numbers (1-based) from the UKERC EDC ReadMe (2017).
# See data/raw/... or the ReadMe linked in DATASET.md.
UKDALE_CHANNELS = {
    1: {
        "aggregate": 1,
        "washing_machine": 5,
        "dishwasher": 6,
        "kettle": 10,
        "fridge": 12,
        "microwave": 13,
    },
    2: {
        "aggregate": 1,
        "kettle": 8,
        "washing_machine": 12,
        "dishwasher": 13,
        "fridge": 14,
        "microwave": 15,
    },
    5: {
        "aggregate": 1,
        "kettle": 18,
        "fridge": 19,
        "dishwasher": 22,
        "microwave": 23,
        "washing_machine": 24,
    },
}

# Default date window per house: enough data for a midterm demo, small enough to
# preprocess on a laptop. Override on the CLI for full-year training.
UKDALE_DEFAULT_RANGE = {
    1: ("2014-01-01", "2014-07-01"),
    2: ("2013-03-01", "2013-09-01"),
    5: ("2014-07-01", "2014-11-01"),
}

# Synthetic generator defaults (watts)
SYNTH_PROFILES = {
    "fridge": {"on_power": 120.0, "cycle_on": 20 * 60, "cycle_off": 40 * 60},
    "kettle": {"on_power": 1800.0, "burst_len": 90, "bursts_per_day": 6},
    "microwave": {"on_power": 1200.0, "burst_len": 60, "bursts_per_day": 4},
    "dishwasher": {"on_power": 900.0, "burst_len": 45 * 60, "bursts_per_day": 1},
    "washing_machine": {"on_power": 500.0, "burst_len": 60 * 60, "bursts_per_day": 1},
}
