# -*- coding: utf-8 -*-
"""disaggregate.py —— 推理(预测)阶段:把一条总功率曲线还原成电器功率曲线。

训练好的模型一次只看 99 个点、只报一个数;而真实使用时给的是一整条长曲线,
本文件负责"拼接":把几十万个窗口的预测,重新拼回一条和输入等长的曲线。

拼法(以 43 万点、stride=4 为例):
  1. 曲线两端各复制 49 个边缘值——否则开头的点凑不齐一个完整窗口
  2. 每隔 4 个点放一个窗口,共约 10.8 万个窗口
  3. 每个窗口喂给模型 → 得到"窗口中点"的预测值
  4. 于是每 4 个点有一个预测,中间的空隙用直线插值补齐
"""

import numpy as np
import torch


@torch.no_grad()  # 推理不需要梯度,加上这句更省内存、更快
def disaggregate(mains, model, window=99, max_power=3000.0, stride=4,
                 batch_size=512, device="cpu"):
    """输入总功率数组,输出等长的预测电器功率数组(单位:瓦)。

    stride 越小预测越密、越慢;越大越快、边缘越糙。4 是速度和质量的平衡点。
    """
    model.eval()  # 评估模式(关闭 Dropout)
    x = np.asarray(mains, dtype=np.float32)
    n = len(x)
    if n == 0:
        return np.zeros(0)
    half = window // 2  # 99 的一半 = 49

    # 第 1 步:两端各补 half 个点(复制边缘值),保证每个点都能当"窗口中点"
    padded = np.concatenate([np.full(half, x[0], np.float32), x,
                             np.full(half, x[-1], np.float32)])
    # 第 2 步:切窗口。第 i 个窗口覆盖 padded[i*stride : i*stride+99],
    # 它的中点正好对应原始曲线的第 i*stride 个点
    n_win = (n - 1) // stride + 1
    windows = np.lib.stride_tricks.sliding_window_view(padded, window)[::stride][:n_win]
    centers = np.arange(n_win) * stride  # 每个窗口的预测值应该写回到哪个位置

    # 第 3 步:分批送进模型(一批 512 个窗口,比一个一个算快得多)
    vals = np.empty(n_win, dtype=np.float64)
    for i in range(0, n_win, batch_size):
        xb = torch.from_numpy(np.ascontiguousarray(windows[i:i + batch_size]))
        xb = xb.to(device) / max_power  # 归一化,和训练时保持一致
        out = model(xb)
        if out.dim() == 2:  # seq2seq 输出整段窗口 (批, 99),取正中间那个点
            out = out[:, out.shape[1] // 2]
        vals[i:i + len(out)] = out.float().cpu().numpy()
    vals *= max_power  # 把 0~1 的预测值乘回真实瓦数

    # 第 4 步:如果相邻预测之间有空隙(stride>1),用直线插值补齐,得到逐点曲线
    if n_win == n:
        return vals
    return np.interp(np.arange(n), centers, vals)
