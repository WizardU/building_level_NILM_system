"""Train the MSE half of the loss ablation.

The weighted-Huber half already exists as the main ``baseline`` checkpoint
(same architecture, 8 epochs, seed 42). We therefore train only the MSE variant
under a distinct run name, then rebuild the metrics table with ``train_all
--skip-train``.
"""

from __future__ import annotations

import argparse
import json

from preprocess.config import APPLIANCES, ROOT
from train.train_one import train

CKPT_DIR = ROOT / "ml" / "checkpoints"
OUT = CKPT_DIR / "loss_ablation_runs.json"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=8)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--appliances", nargs="+", default=APPLIANCES)
    args = parser.parse_args()

    runs = []
    for appliance in args.appliances:
        run_name = f"{appliance}_baseline_mse"
        print(f"=== {run_name} ===", flush=True)
        result = train(
            appliance,
            model_name="baseline",
            epochs=args.epochs,
            seed=42,
            use_weighted_huber=False,
            device_name=args.device,
            run_name=run_name,
            loss_name="mse",
        )
        runs.append(result)

    CKPT_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(runs, indent=2), encoding="utf-8")
    print(f"wrote {OUT}", flush=True)


if __name__ == "__main__":
    main()
