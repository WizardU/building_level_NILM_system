import sys
from pathlib import Path

import numpy as np

ROOT = Path(r"C:\Users\Wizard\Desktop\ComputerScience\毕业设计\NILM")
sys.path.insert(0, str(ROOT / "ml"))
from inference.engine import InferenceEngine

data = np.load(ROOT / "data/processed/replay/ukdale_house1_day1.npz")
agg = data["aggregate"].astype(float)
apps = ["fridge", "kettle", "microwave", "dishwasher", "washing_machine"]

n = 1200
start = 5160
mains = agg[start : start + n]
truth = {a: data[a][start : start + n].astype(float) for a in apps}

engine = InferenceEngine(ROOT / "ml/checkpoints")
pred = engine.disaggregate_series(agg[start : start + n].astype(np.float32), stride=4)

for b in range(0, n, 300):
    sl = slice(b, b + 300)
    print(f"\nminutes {b*6//60:3d}-{(b+300)*6//60:3d}")
    print(f"  mains mean {mains[sl].mean():7.0f}")
    for a in apps:
        print(f"  {a:16s} truth mean {truth[a][sl].mean():7.0f} max {truth[a][sl].max():7.0f} | pred mean {pred[a][sl].mean():7.0f} max {pred[a][sl].max():7.0f}")
