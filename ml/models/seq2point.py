"""Seq2Point 1D-CNN family: baseline, dilated, attention."""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


class Seq2Point(nn.Module):
    """Classic Kelly & Knottenbelt Seq2Point baseline."""

    def __init__(self, window_size: int = 599):
        super().__init__()
        self.window_size = window_size
        self.conv = nn.Sequential(
            nn.Conv1d(1, 30, kernel_size=5, padding=2),
            nn.ReLU(),
            nn.Conv1d(30, 30, kernel_size=5, padding=2),
            nn.ReLU(),
            nn.Conv1d(30, 40, kernel_size=5, padding=2),
            nn.ReLU(),
            nn.Conv1d(40, 50, kernel_size=5, padding=2),
            nn.ReLU(),
            nn.Conv1d(50, 50, kernel_size=5, padding=2),
            nn.ReLU(),
            nn.Dropout(0.2),
        )
        self.fc = nn.Sequential(
            nn.Flatten(),
            nn.Linear(50 * window_size, 1024),
            nn.ReLU(),
            nn.Linear(1024, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, W) or (B, 1, W)
        if x.dim() == 2:
            x = x.unsqueeze(1)
        h = self.conv(x)
        return self.fc(h).squeeze(-1)


class DilatedBlock(nn.Module):
    def __init__(self, channels: int, dilation: int):
        super().__init__()
        self.conv = nn.Conv1d(
            channels, channels, kernel_size=5, padding=2 * dilation, dilation=dilation
        )
        self.act = nn.ReLU()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.act(self.conv(x)) + x


class Seq2PointDilated(nn.Module):
    def __init__(self, window_size: int = 599):
        super().__init__()
        self.window_size = window_size
        self.stem = nn.Sequential(
            nn.Conv1d(1, 32, kernel_size=5, padding=2),
            nn.ReLU(),
        )
        self.blocks = nn.Sequential(
            DilatedBlock(32, 1),
            DilatedBlock(32, 2),
            DilatedBlock(32, 4),
            DilatedBlock(32, 8),
        )
        self.head = nn.Sequential(
            nn.Dropout(0.2),
            nn.Flatten(),
            nn.Linear(32 * window_size, 512),
            nn.ReLU(),
            nn.Linear(512, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if x.dim() == 2:
            x = x.unsqueeze(1)
        h = self.blocks(self.stem(x))
        return self.head(h).squeeze(-1)


class ChannelAttention(nn.Module):
    def __init__(self, channels: int, reduction: int = 8):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(channels, max(channels // reduction, 4)),
            nn.ReLU(),
            nn.Linear(max(channels // reduction, 4), channels),
            nn.Sigmoid(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, C, T)
        w = x.mean(dim=-1)
        w = self.fc(w).unsqueeze(-1)
        return x * w


class TemporalAttention(nn.Module):
    def __init__(self, channels: int):
        super().__init__()
        self.score = nn.Conv1d(channels, 1, kernel_size=1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        a = torch.softmax(self.score(x), dim=-1)
        return x * a * x.size(-1)


class Seq2PointAttention(nn.Module):
    def __init__(self, window_size: int = 599):
        super().__init__()
        self.window_size = window_size
        self.stem = nn.Sequential(
            nn.Conv1d(1, 32, kernel_size=5, padding=2),
            nn.ReLU(),
        )
        self.blocks = nn.Sequential(
            DilatedBlock(32, 1),
            DilatedBlock(32, 2),
            DilatedBlock(32, 4),
            DilatedBlock(32, 8),
        )
        self.ca = ChannelAttention(32)
        self.ta = TemporalAttention(32)
        self.head = nn.Sequential(
            nn.Dropout(0.2),
            nn.Flatten(),
            nn.Linear(32 * window_size, 512),
            nn.ReLU(),
            nn.Linear(512, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if x.dim() == 2:
            x = x.unsqueeze(1)
        h = self.blocks(self.stem(x))
        h = self.ca(h)
        h = self.ta(h)
        return self.head(h).squeeze(-1)


def build_model(name: str, window_size: int = 599) -> nn.Module:
    name = name.lower()
    if name in ("baseline", "seq2point"):
        return Seq2Point(window_size)
    if name in ("dilated", "seq2point_dilated"):
        return Seq2PointDilated(window_size)
    if name in ("attention", "proposed", "seq2point_attention"):
        return Seq2PointAttention(window_size)
    raise ValueError(f"Unknown model: {name}")


class WeightedHuberLoss(nn.Module):
    """Huber loss with higher weight when |target| exceeds on_threshold (normalized)."""

    def __init__(self, delta: float = 1.0, pos_weight: float = 3.0, on_threshold: float = 0.1):
        super().__init__()
        self.delta = delta
        self.pos_weight = pos_weight
        self.on_threshold = on_threshold

    def forward(self, pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        err = F.huber_loss(pred, target, delta=self.delta, reduction="none")
        w = torch.where(target.abs() > self.on_threshold, self.pos_weight, 1.0)
        return (err * w).mean()
