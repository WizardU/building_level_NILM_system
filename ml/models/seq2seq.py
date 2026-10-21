"""Seq2Seq LSTM baseline for NILM (reference implementation)."""

from __future__ import annotations

import torch
import torch.nn as nn


class Seq2SeqLSTM(nn.Module):
    """Seq2Seq bidirectional LSTM for energy disaggregation.

    Input:  aggregate window (B, W)
    Output: appliance power for the whole window (B, W)
            In practice the middle point is used like Seq2Point.
    """

    def __init__(self, window_size: int = 599, hidden: int = 128):
        super().__init__()
        self.window_size = window_size
        self.conv = nn.Sequential(
            nn.Conv1d(1, 16, kernel_size=3, padding=1),
            nn.ReLU(),
        )
        self.encoder = nn.LSTM(16, hidden, batch_first=True, bidirectional=True)
        self.decoder = nn.LSTM(hidden * 2, hidden, batch_first=True)
        self.fc = nn.Linear(hidden, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if x.dim() == 2:
            x = x.unsqueeze(1)
        # (B, 1, W) -> (B, 16, W) -> (B, W, 16)
        z = self.conv(x).transpose(1, 2)
        enc_out, _ = self.encoder(z)
        dec_out, _ = self.decoder(enc_out)
        # (B, W, hidden) -> (B, W, 1) -> (B, W)
        return self.fc(dec_out).squeeze(-1)
