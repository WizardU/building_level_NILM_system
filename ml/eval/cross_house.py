"""Cross-house evaluation: train on house 1, test on house 2 without retraining."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch

from models.seq2point import build_model
from preprocess.cleaning import sliding_windows
from preprocess.config import ROOT, WINDOW_SIZE
from preprocess.ukdale import load_ukdale_house
from train.metrics import evaluate_all

CKPT_DIR = ROOT / "ml" / "checkpoints"
OUT = CKPT_DIR / "cross_house_house2.json"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--house", type=int, default=2)
    parser.add_argument("--start", default="2013-06-01")
    parser.add_argument("--end", default="2013-09-01")
    parser.add_argument("--models", nargs="+", default=["attention", "baseline", "dilated"])
    parser.add_argument("--loss", default=None, help="mse / weighted_huber; default all")
    parser.add_argument("--stride", type=int, default=30)
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--device", default="cuda")
    args = parser.parse_args()

    manifest = json.loads(
        (ROOT / "data/processed/dataset_manifest.json").read_text(encoding="utf-8")
    )
    house1_stats = manifest["stats"]
    print(f"loading house {args.house} {args.start} .. {args.end}", flush=True)
    df = load_ukdale_house(
        ROOT / "data/raw/ukdale.h5",
        house=args.house,
        start=args.start,
        end=args.end,
        sample_period_s=6,
    )
    print("samples", len(df), "columns", list(df.columns), flush=True)

    device = torch.device(args.device if torch.cuda.is_available() else "cpu")
    rows = []
    for model_name in args.models:
        for pt in sorted(CKPT_DIR.glob(f"*_{model_name}*.pt")):
            ckpt = torch.load(pt, map_location="cpu", weights_only=False)
            run_name = ckpt.get("run_name", pt.stem)
            if args.loss and ckpt.get("loss", "weighted_huber") != args.loss:
                continue
            appliance = ckpt["appliance"]
            if appliance not in df.columns:
                print("skip missing appliance", appliance, flush=True)
                continue

            agg = df["aggregate"].to_numpy(dtype=np.float32)
            target = df[appliance].to_numpy(dtype=np.float32)
            x_raw, y_raw = sliding_windows(agg, target, WINDOW_SIZE, args.stride)
            if len(y_raw) == 0:
                continue
            stats = ckpt["stats"]
            x = (x_raw - house1_stats[appliance]["agg_mean"]) / house1_stats[appliance]["agg_std"]
            x = x.astype(np.float32)

            model = build_model(model_name, ckpt.get("window_size", WINDOW_SIZE))
            model.load_state_dict(ckpt["state_dict"])
            model.to(device).eval()
            preds = []
            with torch.no_grad():
                for start in range(0, len(x), args.batch_size):
                    batch = torch.from_numpy(x[start : start + args.batch_size]).to(device)
                    preds.append(model(batch).cpu().numpy())
            y_pred = np.concatenate(preds).reshape(-1) * stats["y_std"] + stats["y_mean"]
            y_pred = np.clip(y_pred, 0.0, None)
            metrics = evaluate_all(y_raw, y_pred, float(ckpt.get("on_threshold", 100.0)))
            rows.append(
                {
                    "appliance": appliance,
                    "model": model_name,
                    "run": run_name,
                    "loss": ckpt.get("loss", "weighted_huber"),
                    "split": f"house{args.house}",
                    "dataset": f"ukdale_house{args.house}",
                    "samples": int(len(y_raw)),
                    "mae": round(float(metrics["mae"]), 3),
                    "rmse": round(float(metrics["rmse"]), 3),
                    "sae": round(float(metrics["sae"]), 4),
                    "state_accuracy": round(float(metrics["state_accuracy"]), 4),
                    "state_f1": round(float(metrics["state_f1"]), 4),
                    "event_f1": round(float(metrics["event_f1"]), 4),
                    "on_threshold": round(float(ckpt.get("on_threshold", 100.0)), 2),
                }
            )
            print(appliance, model_name, rows[-1], flush=True)

    OUT.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print("wrote", OUT, "rows", len(rows))


if __name__ == "__main__":
    main()
