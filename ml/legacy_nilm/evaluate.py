# -*- coding: utf-8 -*-
"""evaluate.py —— 打分工具:训练完后,用这些指标衡量模型猜得准不准。

四个指标(都越小/越大越好,看注释):
  MAE           平均绝对误差(瓦)
  SAE           总电能误差(百分比)
  state P/R/F1  按"开/关状态"逐点打分
  event P/R/F1  按"开启事件"打分(更贴近实际使用)
"""

import numpy as np


def mae(y_true, y_pred):
    """MAE(平均绝对误差):每个时刻 |预测-真实| 的平均值,单位瓦。

    例:MAE = 3 W 表示预测曲线平均只偏差 3 瓦,越小越好。
    """
    return float(np.mean(np.abs(np.asarray(y_true) - np.asarray(y_pred))))


def sae(y_true, y_pred):
    """SAE(总电能误差):整段时间总用电量的相对误差。

    例:真实共用了 10 度电,预测出 9.7 度,SAE = 0.03(3%)。
    它衡量"能量守恒"程度——曲线形状再准,总量差太多也不行。
    """
    total = float(np.sum(y_true))
    return abs(float(np.sum(y_pred)) - total) / max(abs(total), 1e-9)


def _on_off(signal, threshold):
    """把功率曲线变成开/关两种状态:高于阈值算"开"(True),否则"关"。"""
    return np.asarray(signal) >= threshold


def state_prf(y_true, y_pred, threshold):
    """按开关状态逐点计算 精确率/召回率/F1(0~1,越接近 1 越好)。

    precision 精确率 = 网络喊"开着"的时刻里,真开着的比例 → 衡量"误报多不多"
    recall    召回率 = 真开着的时刻里,被网络抓到的比例   → 衡量"漏报多不多"
    f1        两者的调和平均,综合分
    """
    a, b = _on_off(y_true, threshold), _on_off(y_pred, threshold)
    tp = float(np.sum(a & b))          # 预测开、实际也开(答对)
    p = tp / max(float(np.sum(b)), 1e-9)
    r = tp / max(float(np.sum(a)), 1e-9)
    f1 = 2 * p * r / max(p + r, 1e-9)
    return {"precision": p, "recall": r, "f1": f1}


def _rising_edges(on):
    """找出所有"从关变开"的瞬间(上升沿)的下标,一次开机算一个事件。"""
    return np.flatnonzero(np.diff(on.astype(np.int8)) == 1) + 1


def event_prf(y_true, y_pred, threshold, tol=50):
    """按"开启事件"计算 精确率/召回率/F1(比逐点打分更贴近实际应用)。

    例:水壶一天烧 3 次水 = 3 个事件。网络预测出的每次开机,
    只要附近 ±tol 个采样点内(默认 50 点 ≈ 5 分钟)确实有真实开机就算命中。
    事件级打分对"时间偏移"更宽容,但对"漏检"更严格。
    """
    true_ev = _rising_edges(_on_off(y_true, threshold))
    pred_ev = _rising_edges(_on_off(y_pred, threshold))
    matched, used = 0, set()  # used:每个真实事件最多被命中一次
    for e in pred_ev:
        if len(true_ev):
            j = int(np.argmin(np.abs(true_ev - e)))  # 找离得最近的真实事件
            if abs(int(true_ev[j]) - e) <= tol and j not in used:
                matched += 1
                used.add(j)
    p = matched / len(pred_ev) if len(pred_ev) else 0.0
    r = matched / len(true_ev) if len(true_ev) else 0.0
    f1 = 2 * p * r / max(p + r, 1e-9)
    return {"precision": p, "recall": r, "f1": f1}


def evaluate(y_true, y_pred, threshold, event_tol=50):
    """一次算齐全部指标,返回一个字典(界面和训练脚本都调这个)。"""
    out = {"mae_w": mae(y_true, y_pred), "sae": sae(y_true, y_pred)}
    out.update({f"state_{k}": v for k, v in state_prf(y_true, y_pred, threshold).items()})
    out.update({f"event_{k}": v for k, v in event_prf(y_true, y_pred, threshold, event_tol).items()})
    return out
