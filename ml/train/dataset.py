from __future__ import annotations

from pathlib import Path

import h5py
import torch
from torch.utils.data import Dataset


class WindowDataset(Dataset):
    def __init__(self, path: Path):
        with h5py.File(path, "r") as f:
            self.x = f["x"][:].astype("float32")
            self.y = f["y"][:].astype("float32")

    def __len__(self) -> int:
        return len(self.y)

    def __getitem__(self, idx: int):
        return torch.from_numpy(self.x[idx]), torch.tensor(self.y[idx])
