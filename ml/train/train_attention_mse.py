"""Train attention with MSE to complete the 2x2 architecture x loss design."""

from __future__ import annotations

import argparse
import json

from preprocess.config import APPLIANCES, ROOT
from train.train_one import train

CKPT_DIR = ROOT / "ml" / "checkpoints"
OUT = CKPT_DIR / "attention_mse_runs.json"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=8)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--appliances", nargs="+", default=APPLIANCES)
    args = parser.parse_args()

    runs = []
    for appliance in args.appliances:
        run_name = f"{appliance}_attention_mse"
        print(f"=== {run_name} ===", flush=True)
        runs.append(
            train(
                appliance,
                model_name="attention",
                epochs=args.epochs,
                seed=42,
                use_weighted_huber=False,
                device_name=args.device,
                run_name=run_name,
                loss_name="mse",
            )
        )
    OUT.write_text(json.dumps(runs, indent=2), encoding="utf-8")
    print("wrote", OUT, flush=True)


if __name__ == "__main__":
    main()
