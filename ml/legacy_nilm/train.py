# -*- coding: utf-8 -*-
"""train.py —— 训练脚本:教神经网络从总功率曲线里"认出"某个电器。

【训练在干什么?】
1. 把 data/ 里的曲线切成几十万个 (输入窗口, 标准答案) 样本
2. 网络对每个窗口给出预测 → 和标准答案比差距(loss) → 朝差距变小的方向微调参数
3. 把全部样本过一遍叫 1 个 epoch;通常过几轮,loss 就降下去了

【怎么运行?】在 PyCharm 终端执行(参数可换):
    python train.py --appliance kettle --model seq2point --epochs 6
    可选电器: kettle / microwave / washing_machine / fridge
    可选模型: seq2point(CNN,快)/ seq2seq(LSTM,慢)
训练完的模型保存在 outputs/checkpoints/ 下,界面 app.py 会自动加载它。
"""

import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from data_utils import NILMDataset, create_windows, create_windows_seq, load_demo
from disaggregate import disaggregate
from evaluate import evaluate
from models import build_model

# 归一化"满量程":所有功率先除以 3000,压到 0~1 之间。
# 神经网络吃 0~1 的小数字比吃 0~3000 的大数字稳定得多(推理时再乘回来)
MAX_POWER = 3000.0
CKPT_DIR = Path(__file__).resolve().parent / "outputs" / "checkpoints"  # 模型保存目录


def split(n, ratios=(0.8, 0.1)):
    """把 43 万个采样点按时间顺序切成三段:前 80% 训练 / 中 10% 验证 / 后 10% 测试。

    为什么按时间切而不是随机抽?真实场景是"用过去预测未来",
    时间上分开才不会作弊(测试段必须是模型从没见过的数据)。
    """
    i1, i2 = int(n * ratios[0]), int(n * (ratios[0] + ratios[1]))
    return slice(0, i1), slice(i1, i2), slice(i2, n)


def main():
    # ---------- 1. 读取命令行参数 ----------
    p = argparse.ArgumentParser()
    p.add_argument("--appliance", default="kettle", help="target appliance name")
    p.add_argument("--model", default="seq2point", choices=["seq2point", "seq2seq"])
    p.add_argument("--window", type=int, default=99, help="input window length")
    p.add_argument("--stride", type=int, default=4, help="window step when slicing")
    p.add_argument("--epochs", type=int, default=6, help="how many passes over the data")
    p.add_argument("--batch-size", type=int, default=256, help="samples per update")
    p.add_argument("--lr", type=float, default=1e-3, help="learning rate")
    args = p.parse_args()

    torch.manual_seed(42)  # 固定随机种子,保证每次训练结果可复现
    device = "cuda" if torch.cuda.is_available() else "cpu"  # 有独显用 GPU,没有用 CPU
    print(f"[env] device={device}")

    # ---------- 2. 读数据 ----------
    # 从 meta.json 里拿这个电器的"开机阈值"(算 F1 指标时用),拿不到就默认 50 瓦
    threshold = 50.0
    meta_path = Path(__file__).resolve().parent / "data" / "meta.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if args.appliance in meta["appliances"]:
            threshold = float(meta["appliances"][args.appliance]["on_threshold"])

    df = load_demo(args.appliance)  # 三列表格:time / mains / 该电器功率
    mains = df["mains"].to_numpy(np.float32)      # 总功率(模型输入)
    target = df[args.appliance].to_numpy(np.float32)  # 电器真实功率(标准答案)
    tr, va, te = split(len(df))  # 三段时间切片

    # 把每段曲线切滑窗(输入和答案都除以 3000 归一化);
    # seq2seq 还额外需要"整段窗口的答案",seq2point 只用中点
    def make_arrays(seg):
        x_win, y_pt = create_windows(mains[seg] / MAX_POWER, target[seg] / MAX_POWER,
                                     args.window, args.stride)
        y_sq = (create_windows_seq(target[seg] / MAX_POWER, args.window, args.stride)
                if args.model == "seq2seq" else None)
        return x_win, y_pt, y_sq

    x_tr, y_tr, ys_tr = make_arrays(tr)
    x_va, y_va, ys_va = make_arrays(va)
    x_te, _, _ = make_arrays(te)
    print(f"[data] appliance={args.appliance} model={args.model} window={args.window} "
          f"train/val/test windows = {len(x_tr)}/{len(x_va)}/{len(x_te)}")

    # DataLoader:自动把样本打乱(shuffle)并按批打包;验证集不用打乱
    train_loader = DataLoader(NILMDataset(x_tr, y_tr, ys_tr),
                              batch_size=args.batch_size, shuffle=True, drop_last=True)
    val_loader = DataLoader(NILMDataset(x_va, y_va, ys_va), batch_size=1024)

    # ---------- 3. 建模型、优化器、损失函数 ----------
    model = build_model(args.model, args.window).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)  # Adam:自动调步长的梯度下降
    crit = nn.MSELoss()  # 损失函数 = 预测与答案的均方差,差距越小越好

    best_val, best_state = float("inf"), None  # 记录历史最好的验证成绩和对应参数
    for epoch in range(1, args.epochs + 1):
        t0 = time.time()

        # --- 训练半场:逐批喂样本 → 算损失 → 反向传播 → 更新参数 ---
        model.train()  # 切到训练模式(Dropout 生效)
        tr_loss = 0.0
        for batch in train_loader:
            batch = [b.to(device) for b in batch]          # 数据搬到 GPU/CPU
            x, y = batch[0], batch[-1]  # seq2point 时 batch=[输入,答案];
            opt.zero_grad()                                # 清掉上一步的梯度
            loss = crit(model(x), y)                       # 前向:预测并算差距
            loss.backward()                                # 反向:算每个参数该怎么改
            opt.step()                                     # 真的去改参数
            tr_loss += loss.item() * len(x)
        tr_loss /= max(len(x_tr) - len(x_tr) % args.batch_size, 1)

        # --- 验证半场:只考不学,看模型在"没学过的验证段"上的成绩 ---
        model.eval()  # 切到评估模式(Dropout 关闭)
        va_loss = 0.0
        with torch.no_grad():  # 验证不需要算梯度,省内存提速
            for batch in val_loader:
                batch = [b.to(device) for b in batch]
                x, y = batch[0], batch[-1]
                va_loss += crit(model(x), y).item() * len(x)
        va_loss /= len(x_va)

        # 只保存验证成绩最好的那一轮的参数(防止保存到"越学越差"的状态)
        mark = ""
        if va_loss < best_val:
            best_val = va_loss
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
            mark = "  <- best"
        print(f"[epoch {epoch:02d}] train_mse={tr_loss:.6f} val_mse={va_loss:.6f} "
              f"({time.time() - t0:.1f}s){mark}")

    # ---------- 4. 保存模型 ----------
    CKPT_DIR.mkdir(parents=True, exist_ok=True)
    ckpt_path = CKPT_DIR / f"{args.appliance}_{args.model}.pt"
    # 检查点里除了权重,还带上推理需要的全部配置(窗口长度、归一化量、阈值等),
    # 这样 app.py 加载时不用重新问参数
    torch.save({"state_dict": best_state,
                "config": {"appliance": args.appliance, "model": args.model,
                           "window": args.window, "max_power": MAX_POWER,
                           "on_threshold": threshold}}, ckpt_path)
    print(f"[save] {ckpt_path}")

    # ---------- 5. 最终考试:在完全没见过的后 10% 数据上打分 ----------
    model.load_state_dict(best_state)
    model.to(device)
    y_pred = disaggregate(mains[te], model, args.window, MAX_POWER, stride=4, device=device)
    metrics = evaluate(target[te], y_pred, threshold)
    print("[test]", json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
