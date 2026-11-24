import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(r"C:\Users\Wizard\Desktop\ComputerScience\毕业设计\NILM")
data = np.load(ROOT / "data/processed/replay/ukdale_house1_day1.npz")
agg = data["aggregate"].astype(float)
apps = ["fridge", "kettle", "microwave", "dishwasher", "washing_machine"]


def best_window(hours=2.0):
    n = int(hours * 600)
    score = None
    best = 0
    for start in range(0, len(agg) - n, 60):
        value = (
            np.sum(data["kettle"][start : start + n] > 500)
            + np.sum(data["microwave"][start : start + n] > 200)
            + np.sum(data["dishwasher"][start : start + n] > 100)
        )
        if score is None or value > score:
            score = value
            best = start
    return best


start = best_window()
n = 1200
stamps = data["timestamps"].astype("int64")
print("timestamps dtype", data["timestamps"].dtype)
start_dt = datetime.fromtimestamp(int(stamps[start]) / 1e9, tz=timezone.utc)
end_dt = datetime.fromtimestamp(int(stamps[start + n - 1]) / 1e9, tz=timezone.utc)
print("window start index", start)
print("window time", start_dt, "->", end_dt)
mains = agg[start : start + n]
truth = {a: data[a][start : start + n].astype(float) for a in apps}
total_truth = sum(truth.values())
resid = mains - total_truth
print("mains mean/max", round(mains.mean(), 1), round(mains.max(), 1))
print("truth sum mean/max", round(total_truth.mean(), 1), round(total_truth.max(), 1))
print("residual mean/max", round(resid.mean(), 1), round(resid.max(), 1))
print("residual > 500W share", round(float(np.mean(resid > 500)), 3))
print("residual > 1500W share", round(float(np.mean(resid > 1500)), 3))
for a in apps:
    print(f"{a:16s} max={truth[a].max():7.1f} mean={truth[a].mean():6.1f} on_share={np.mean(truth[a]> (500 if a=='kettle' else 200 if a=='microwave' else 100 if a in ('dishwasher','washing_machine') else 50)):.3f}")

# residual profile in 10-minute bins
print("\n10-min bins: mains / five-truth / residual / biggest truth appliance")
for b in range(0, n, 300):
    m = mains[b : b + 300].mean()
    t = total_truth[b : b + 300].mean()
    r = resid[b : b + 300].mean()
    biggest = max(apps, key=lambda a: truth[a][b : b + 300].mean())
    print(f"{b//5:3d} min  {m:7.0f}  {t:7.0f}  {r:7.0f}  {biggest}")
