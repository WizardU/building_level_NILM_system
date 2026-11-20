import json
import sys
from pathlib import Path

import h5py
import numpy as np

ROOT = Path(r"C:\Users\Wizard\Desktop\ComputerScience\毕业设计\NILM")
sys.path.insert(0, str(ROOT / "ml"))
from preprocess.ukdale import load_ukdale_house

THRESH = {
    "fridge": 50.0,
    "kettle": 500.0,
    "microwave": 200.0,
    "dishwasher": 100.0,
    "washing_machine": 100.0,
}
APPS = list(THRESH)
man = json.loads((ROOT / "data/processed/dataset_manifest.json").read_text(encoding="utf-8"))

print("loading six months of UK-DALE house 1 ...", flush=True)
df = load_ukdale_house(ROOT / "data/raw/ukdale.h5", house=1, start="2014-01-01", end="2014-07-01", sample_period_s=6)
print("samples", len(df))
for app in APPS:
    s = df[app].to_numpy()
    on = s > THRESH[app]
    events = int(np.sum(np.diff(on.astype(np.int8)) == 1))
    print(
        f"{app:16s} on_hours={on.sum()*6/3600:8.1f} on_pct={on.mean()*100:6.2f}% "
        f"events={events:5d} max={s.max():7.0f} mean={s.mean():7.1f}"
    )

print("\nwindow counts and positive windows:")
for app in APPS:
    stats = man["stats"][app]
    thr_norm = (THRESH[app] - stats["y_mean"]) / stats["y_std"]
    parts = []
    for split in ("train", "val", "test"):
        path = ROOT / man["files"][app][split]
        with h5py.File(path, "r") as f:
            y = f["y"][:].astype("float32")
        pos = int(np.sum(y > thr_norm))
        parts.append(f"{split}={len(y)}/{pos} pos")
    print(f"{app:16s} " + " | ".join(parts))
