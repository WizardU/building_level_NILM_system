"""Train a single appliance Seq2Point model."""

from __future__ import annotations

import argparse
import json
import random
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


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def resolve_file(manifest: dict, appliance: str, split: str) -> Path:
    rel = manifest["files"][appliance][split]
    # stored relative to NILM root
    p = ROOT / rel
    if not p.exists():
        p = PROCESSED_DIR / Path(rel).name
    return p


def _predict(model: torch.nn.Module, loader: DataLoader, device: torch.device, stats: dict):
    model.eval()
    preds, trues = [], []
    with torch.no_grad():
        for x, y in loader:
            preds.append(model(x.to(device)).cpu().numpy())
            trues.append(y.numpy())
    y_pred = np.concatenate(preds) * stats["y_std"] + stats["y_mean"]
    y_true = np.concatenate(trues) * stats["y_std"] + stats["y_mean"]
    return y_true, np.clip(y_pred, 0.0, None)


def train(
    appliance: str,
    model_name: str = "baseline",
    epochs: int = 5,
    batch_size: int = 128,
    lr: float = 1e-4,
    seed: int = 42,
    use_weighted_huber: bool = False,
    device_name: str | None = None,
    num_workers: int = 0,
) -> dict:
    seed_everything(seed)
    manifest = json.loads((PROCESSED_DIR / "dataset_manifest.json").read_text(encoding="utf-8"))
    if appliance not in manifest["files"]:
        raise SystemExit(f"{appliance} missing from dataset manifest")

    train_ds = WindowDataset(resolve_file(manifest, appliance, "train"))
    val_ds = WindowDataset(resolve_file(manifest, appliance, "val"))
    train_loader = DataLoader(
        train_ds, batch_size=batch_size, shuffle=True, num_workers=num_workers
    )
    val_loader = DataLoader(val_ds, batch_size=batch_size * 2, shuffle=False)

    if device_name:
        device = torch.device(device_name)
    else:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = build_model(model_name, WINDOW_SIZE).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = (
        WeightedHuberLoss(pos_weight=10.0) if use_weighted_huber else torch.nn.MSELoss()
    )

    stats = manifest["stats"][appliance]
    default_threshold = float(ON_THRESHOLDS[appliance])
    best_val = float("inf")
    history: list[dict] = []
    ckpt_path = CKPT_DIR / f"{appliance}_{model_name}.pt"
    CKPT_DIR.mkdir(parents=True, exist_ok=True)

    for epoch in range(1, epochs + 1):
        model.train()
        losses = []
        for x, y in tqdm(
            train_loader, desc=f"{appliance}/{model_name} ep{epoch}", leave=False
        ):
            x, y = x.to(device), y.to(device)
            opt.zero_grad()
            pred = model(x)
            loss = criterion(pred, y)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            opt.step()
            losses.append(loss.item())

        y_true, y_pred = _predict(model, val_loader, device, stats)
        metrics = evaluate_all(y_true, y_pred, default_threshold)
        metrics["train_loss"] = float(np.mean(losses)) if losses else float("nan")
        metrics["epoch"] = epoch
        history.append({k: float(v) for k, v in metrics.items()})
        print(
            f"[{appliance}|{model_name}] epoch {epoch}: "
            f"loss={metrics['train_loss']:.4f} mae={metrics['mae']:.2f} "
            f"sae={metrics['sae']:.3f} state_f1={metrics['state_f1']:.3f} "
            f"event_f1={metrics['event_f1']:.3f}"
        )

        if metrics["mae"] < best_val:
            best_val = float(metrics["mae"])
            torch.save(
                {
                    "model_name": model_name,
                    "appliance": appliance,
                    "state_dict": model.state_dict(),
                    "stats": stats,
                    "window_size": WINDOW_SIZE,
                    "sample_period_s": manifest.get("sample_period_s", 1),
                    "dataset": manifest.get("dataset", ""),
                    "metrics": {k: float(v) for k, v in metrics.items()},
                    "epoch": epoch,
                },
                ckpt_path,
            )

    # Threshold calibration on the validation split (fair: never uses test data).
    from eval.evaluate import calibrate_threshold

    checkpoint = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    model.load_state_dict(checkpoint["state_dict"])
    y_true, y_pred = _predict(model, val_loader, device, stats)
    threshold, calibrated_f1 = calibrate_threshold(y_true, y_pred, default_threshold)
    checkpoint["on_threshold"] = threshold
    checkpoint["val_event_f1"] = calibrated_f1
    torch.save(checkpoint, ckpt_path)
    print(
        f"[{appliance}|{model_name}] best val MAE={best_val:.2f}, "
        f"threshold={threshold:.1f} W (val event F1={calibrated_f1:.3f})"
    )

    return {
        "appliance": appliance,
        "model": model_name,
        "history": history,
        "best_mae": best_val,
        "on_threshold": threshold,
        "val_event_f1": calibrated_f1,
        "checkpoint": str(ckpt_path),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--appliance", required=True)
    parser.add_argument("--model", default="baseline")
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--device", default=None, help="cpu / cuda / cuda:0")
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--weighted-huber", action="store_true")
    args = parser.parse_args()
    train(
        args.appliance,
        args.model,
        args.epochs,
        args.batch_size,
        args.lr,
        args.seed,
        use_weighted_huber=args.weighted_huber,
        device_name=args.device,
        num_workers=args.num_workers,
    )


if __name__ == "__main__":
    main()
