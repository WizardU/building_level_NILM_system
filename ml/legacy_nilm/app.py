# -*- coding: utf-8 -*-
"""app.py —— 数据展示界面(Streamlit 网页应用)。

【Streamlit 是什么?】
一个"用纯 Python 就能写网页"的库,做数据演示特别方便:
代码从上往下执行一遍,页面就画出来了;用户在页面上动一下控件
(换电器、拉时间条),整页代码会自动重新执行一遍,页面随之刷新。

【怎么运行?】在 PyCharm 底部 Terminal(终端)里执行:
    .venv\\Scripts\\python.exe -m streamlit run app.py
然后浏览器会自动打开 http://localhost:8501

【界面上有什么?】
左侧:选目标电器、选分解模型(seq2point/seq2seq)、拖动查看时间段
右侧:四个指标卡(MAE/SAE/两个F1)+ 功率曲线对比图 + 每日电能柱状图
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import torch

from data_utils import load_demo
from disaggregate import disaggregate
from evaluate import evaluate
from models import build_model

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"                            # 数据目录
CKPT_DIR = ROOT / "outputs" / "checkpoints"         # 训练好的模型目录

# 电器英文名 → 界面上显示的中文名
APPLIANCE_CN = {
    "kettle": "电水壶 Kettle",
    "microwave": "微波炉 Microwave",
    "washing_machine": "洗衣机 Washing Machine",
    "fridge": "冰箱 Fridge",
}
MODEL_CN = {"seq2point": "Seq2Point (CNN)", "seq2seq": "Seq2Seq (LSTM)"}


@st.cache_data
def load_data(appliance):
    """读数据 + 缓存。

    @st.cache_data 是 Streamlit 的缓存标记:同一个电器第二次调用时
    不重新读 CSV,直接用上次的结果——用户每动一下控件整页都会重跑,
    没有这个缓存的话每次都要读几十万行,页面会很卡。
    """
    return load_demo(appliance)


@st.cache_resource
def load_model(appliance, model_type):
    """加载训练好的模型(同样带缓存,模型只从硬盘读一次)。

    检查点 .pt 文件里存了两样东西:
      state_dict  网络的权重参数
      config      推理需要的配置(窗口长度、归一化量、开机阈值)
    """
    ckpt = torch.load(CKPT_DIR / f"{appliance}_{model_type}.pt", map_location="cpu")
    model = build_model(ckpt["config"]["model"], ckpt["config"]["window"])
    model.load_state_dict(ckpt["state_dict"])  # 把权重装进网络
    model.eval()  # 评估模式(关闭 Dropout)
    return model, ckpt["config"]


def list_appliances():
    """扫一眼 data/appliances/ 文件夹,有哪些电器就列出哪些选项。"""
    if not (DATA_DIR / "mains.csv").exists():
        return []
    return sorted(p.stem for p in (DATA_DIR / "appliances").glob("*.csv"))


def downsample(df, max_points=30000):
    """曲线点数太多时抽稀(每隔几个点取一个),画图才不会卡。"""
    if len(df) <= max_points:
        return df
    step = int(np.ceil(len(df) / max_points))
    return df.iloc[::step]


def trained_models():
    """扫一眼 checkpoints 目录,列出已经训练好、可以直接用的模型。"""
    return [(a, m) for a in list_appliances() for m in ("seq2point", "seq2seq")
            if (CKPT_DIR / f"{a}_{m}.pt").exists()]


# ---------- 页面整体设置 ----------
st.set_page_config(page_title="NILM 负荷监测系统", page_icon="⚡", layout="wide")
st.title("⚡ NILM 非侵入式负荷监测演示系统")
st.caption("Seq2Point / Seq2Seq 深度学习负荷分解 —— 只用总电表数据,估计每个电器的功率曲线")

# ---------- 左侧控制面板 ----------
appliances = list_appliances()
if not appliances:
    # 数据没生成时给个明确提示,并停止运行(st.stop = 后面的代码不执行了)
    st.error("未找到数据。请先运行: `python make_demo_data.py`")
    st.stop()

with st.sidebar:
    st.header("控制面板")
    # selectbox = 下拉选择框,返回值是被选中的那一项
    appliance = st.selectbox("目标电器", appliances,
                             format_func=lambda a: APPLIANCE_CN.get(a, a))
    model_type = st.selectbox("分解模型", ["seq2point", "seq2seq"],
                              format_func=lambda m: MODEL_CN[m])

    # slider = 双头时间条:控制主图显示哪一段(默认最近 3 天)
    df = load_data(appliance)
    t_min = df["time"].min().to_pydatetime()
    t_max = df["time"].max().to_pydatetime()
    date_range = st.slider(
        "查看时间段", min_value=t_min, max_value=t_max,
        value=(max(t_max - pd.Timedelta(days=3), t_min), t_max),
        step=pd.Timedelta(hours=1), format="MM-DD HH:mm",
    )
    st.divider()  # 分隔线
    st.markdown("**已训练模型**")
    done = trained_models()
    if done:
        for a, m in done:
            st.markdown(f"- ✅ {APPLIANCE_CN.get(a, a)} · {MODEL_CN[m]}")
    else:
        st.markdown("- 无,请先运行 `python train.py`")

# ---------- 按所选时间段截取数据 ----------
mask = (df["time"] >= pd.Timestamp(date_range[0])) & (df["time"] <= pd.Timestamp(date_range[1]))
view = df.loc[mask].reset_index(drop=True)
if len(view) < 200:
    st.warning("所选时间段太短,请扩大范围")
    st.stop()

# 该电器的"开机阈值"(算 F1 用),从 meta.json 里读
threshold = 50.0
meta_path = DATA_DIR / "meta.json"
if meta_path.exists():
    try:
        threshold = float(json.loads(meta_path.read_text(encoding="utf-8"))
                          ["appliances"][appliance]["on_threshold"])
    except (KeyError, ValueError):
        pass

# ---------- 用模型对这段数据做分解 ----------
pred = None
ckpt_path = CKPT_DIR / f"{appliance}_{model_type}.pt"
if ckpt_path.exists():
    with st.spinner("正在用模型分解当前时间段..."):
        model, cfg = load_model(appliance, model_type)
        # 只对页面上显示的这一段做推理(几万个点,一两秒就完)
        pred = disaggregate(view["mains"].to_numpy(np.float32), model,
                            cfg["window"], cfg["max_power"], stride=8)
else:
    # 这个电器还没训练过:给出训练命令,界面退化为"只看真实值"
    st.info(f"该电器还没有 `{MODEL_CN[model_type]}` 模型,下面显示真实值作为参考。"
            f"训练命令: `python train.py --appliance {appliance} --model {model_type}`")

# ---------- 指标卡 ----------
# 没有模型时拿全 0 当"预测",指标自然很差,但界面不会崩
gt = view[appliance].to_numpy()
metrics = evaluate(gt, pred if pred is not None else np.zeros(len(view)), threshold)

c1, c2, c3, c4 = st.columns(4)  # 一行四列的指标卡
c1.metric("MAE 平均绝对误差", f"{metrics['mae_w']:.1f} W")
c2.metric("SAE 总电能误差", f"{metrics['sae'] * 100:.1f} %")
c3.metric("F1 · 开关状态", f"{metrics['state_f1']:.3f}")
c4.metric("F1 · 事件检测", f"{metrics['event_f1']:.3f}")

# ---------- 功率曲线对比图(Plotly) ----------
plot_df = view[["time", "mains", appliance]].rename(columns={appliance: "真实值"})
if pred is not None:
    plot_df["模型预测"] = pred
d = downsample(plot_df)

fig = go.Figure()
# 三条曲线:总电表(灰)、真实电器功率(蓝实线)、模型预测(橙虚线)
fig.add_trace(go.Scatter(x=d["time"], y=d["mains"], name="总电表 Mains",
                         line=dict(color="#9ca3af", width=1)))
fig.add_trace(go.Scatter(x=d["time"], y=d["真实值"], name="真实功率 Ground Truth",
                         line=dict(color="#2563eb", width=1.6)))
if pred is not None:
    fig.add_trace(go.Scatter(x=d["time"], y=d["模型预测"], name="模型预测 Prediction",
                             line=dict(color="#f97316", width=1.6, dash="dot")))
fig.update_layout(height=460, margin=dict(l=10, r=10, t=30, b=10),
                  yaxis_title="功率 (W)", xaxis_title="时间",
                  legend=dict(orientation="h", y=1.12))
st.plotly_chart(fig, width="stretch")

# ---------- 每日电能柱状图 ----------
st.subheader("每日电能消耗 (kWh)")
# 每天的功率求和 × 6秒 ÷ 3600000 = 该天用了多少度电(千瓦时)
daily = view.set_index("time")[[appliance]].resample("1D").sum() * (6 / 3.6e6)
daily.columns = ["真实 kWh"]
if pred is not None:
    daily["预测 kWh"] = pd.Series(pred, index=view["time"]).resample("1D").sum() * (6 / 3.6e6)
st.bar_chart(daily)

# ---------- 折叠区:原始数据表 ----------
with st.expander("原始数据预览"):
    st.dataframe(downsample(view, 1000))

st.divider()
st.caption("采样间隔 6 s · 输入窗口 99 点 · Seq2Point CNN (Zhang et al., NeurIPS 2018) / "
           "Seq2Seq LSTM · 接入 UK-DALE 等真实数据集请看 README.md")
