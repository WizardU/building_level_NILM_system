"""Train a single appliance Seq2Point model."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader
from tqdm import tqdm

from models.seq2point import WeightedHuberLoss, build_model
from preprocess.config import ON_THRESHOLDS, PROCESSED_DIR, ROOT, WINDOW_SIZE
from train.dataset import WindowDataset
from train.metrics import evaluate_all

CKPT_DIR = ROOT / "ml" / "checkpoints"


def resolve_file(manifest: dict, appliance: str, split: str) -> Path:
    rel = manifest["files"][appliance][split]
    # stored relative to NILM root
    p = ROOT / rel
    if not p.exists():
        p = PROCESSED_DIR / Path(rel).name
    return p


def train(
    appliance: str,
    model_name: str = "baseline",
    epochs: int = 5,
    batch_size: int = 64,
    lr: float = 1e-4,
    use_weighted_huber: bool = False,
) -> dict:
    man = json.loads((PROCESSED_DIR / "dataset_manifest.json").read_text(encoding="utf-8"))
    train_ds = WindowDataset(resolve_file(man, appliance, "train"))
    val_ds = WindowDataset(resolve_file(man, appliance, "val"))
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = build_model(model_name, WINDOW_SIZE).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = WeightedHuberLoss() if use_weighted_huber else torch.nn.MSELoss()

    stats = man["stats"][appliance]
    best_val = float("inf")
    history = []

    for epoch in range(1, epochs + 1):
        model.train()
        losses = []
        for x, y in tqdm(train_loader, desc=f"{appliance}/{model_name} ep{epoch}", leave=False):
            x, y = x.to(device), y.to(device)
            opt.zero_grad()
            pred = model(x)
            loss = criterion(pred, y)
            loss.backward()
            opt.step()
            losses.append(loss.item())
        model.eval()
        preds, trues = [], []
        with torch.no_grad():
            for x, y in val_loader:
                x = x.to(device)
                pred = model(x).cpu().numpy()
                preds.append(pred)
                trues.append(y.numpy())
        y_pred = np.concatenate(preds) * stats["y_std"] + stats["y_mean"]
        y_true = np.concatenate(trues) * stats["y_std"] + stats["y_mean"]
        metrics = evaluate_all(y_true, y_pred, ON_THRESHOLDS[appliance])
        metrics["train_loss"] = float(np.mean(losses))
        history.append(metrics)
        print(f"[{appliance}|{model_name}] epoch {epoch}: {metrics}")
        if metrics["mae"] < best_val:
            best_val = metrics["mae"]
            CKPT_DIR.mkdir(parents=True, exist_ok=True)
            path = CKPT_DIR / f"{appliance}_{model_name}.pt"
            torch.save(
                {
                    "model_name": model_name,
                    "appliance": appliance,
                    "state_dict": model.state_dict(),
                    "stats": stats,
                    "window_size": WINDOW_SIZE,
                    "metrics": metrics,
                },
                path,
            )
    return {"appliance": appliance, "model": model_name, "history": history, "best_mae": best_val}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--appliance", required=True)
    p.add_argument("--model", default="baseline")
    p.add_argument("--epochs", type=int, default=5)
    p.add_argument("--batch-size", type=int, default=64)
    p.add_argument("--weighted-huber", action="store_true")
    args = p.parse_args()
    train(args.appliance, args.model, args.epochs, args.batch_size, use_weighted_huber=args.weighted_huber)


if __name__ == "__main__":
    main()
