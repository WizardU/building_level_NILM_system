"""Export PyTorch checkpoints to ONNX and verify numerical parity."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch

from models.seq2point import build_model
from preprocess.config import ROOT, WINDOW_SIZE

CKPT_DIR = ROOT / "ml" / "checkpoints"


def export_one(pt_path: Path, rtol: float = 1e-3, atol: float = 1e-4) -> Path:
    ckpt = torch.load(pt_path, map_location="cpu", weights_only=False)
    model = build_model(ckpt["model_name"], ckpt.get("window_size", WINDOW_SIZE))
    model.load_state_dict(ckpt["state_dict"])
    model.eval()

    onnx_path = pt_path.with_suffix(".onnx")
    dummy = torch.randn(1, WINDOW_SIZE)
    try:
        torch.onnx.export(
            model,
            dummy,
            str(onnx_path),
            input_names=["aggregate"],
            output_names=["power"],
            dynamic_axes={"aggregate": {0: "batch"}, "power": {0: "batch"}},
            opset_version=17,
            dynamo=False,
        )
    except TypeError:
        torch.onnx.export(
            model,
            dummy,
            str(onnx_path),
            input_names=["aggregate"],
            output_names=["power"],
            dynamic_axes={"aggregate": {0: "batch"}, "power": {0: "batch"}},
            opset_version=17,
        )

    # Parity check
    import onnxruntime as ort

    sess = ort.InferenceSession(str(onnx_path), providers=["CPUExecutionProvider"])
    x = np.random.randn(4, WINDOW_SIZE).astype(np.float32)
    with torch.no_grad():
        pt_out = model(torch.from_numpy(x)).numpy()
    ort_out = sess.run(None, {"aggregate": x})[0].reshape(-1)
    if not np.allclose(pt_out, ort_out, rtol=rtol, atol=atol):
        max_err = float(np.max(np.abs(pt_out - ort_out)))
        raise RuntimeError(f"ONNX mismatch for {pt_path.name}: max_err={max_err}")

    meta = {
        "appliance": ckpt["appliance"],
        "model_name": ckpt["model_name"],
        "stats": ckpt["stats"],
        "window_size": ckpt.get("window_size", WINDOW_SIZE),
        "metrics": ckpt.get("metrics", {}),
        "onnx": onnx_path.name,
    }
    meta_path = pt_path.with_suffix(".json")
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"Exported {onnx_path} (parity OK)")
    return onnx_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pattern", default="*_attention.pt")
    parser.add_argument("--all", action="store_true", help="Export all .pt checkpoints")
    args = parser.parse_args()
    CKPT_DIR.mkdir(parents=True, exist_ok=True)
    if args.all:
        paths = sorted(CKPT_DIR.glob("*.pt"))
    else:
        paths = sorted(CKPT_DIR.glob(args.pattern))
        if not paths:
            paths = sorted(CKPT_DIR.glob("*.pt"))
    if not paths:
        raise SystemExit(f"No checkpoints in {CKPT_DIR}")
    for p in paths:
        export_one(p)


if __name__ == "__main__":
    main()
