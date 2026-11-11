# -*- coding: utf-8 -*-
"""
data_utils.py —— 数据"装卸工":读文件、对齐时间、切成神经网络要的形状。

本文件 4 个部分:
  load_demo()       读入 make_demo_data.py 生成的模拟数据(本项目默认数据)
  load_ukdale()     读入 UK-DALE 真实数据集(以后做真实实验时用)
  create_windows()  【核心】把长曲线切成一个个小窗口(seq2point 的输入和答案)
  NILMDataset()     PyTorch 数据集包装类,训练器按批取数据时用

【什么是"滑动窗口"?】(NILM 最核心的概念,看懂这段就懂了一半)
总功率是一条 43 万个点的长曲线,而网络一次只能看 99 个点。
就像拿着一个 99 格的小相框,在曲线上每次往右挪几格"拍一张照片":

    照片(输入 x)   = 相框里这 99 个点的总功率
    答案(标签 y)   = 相框正中间那一刻,电器的真实功率

几十万张这样的 (照片, 答案) 对,就是全部训练材料。
"""

from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"


def load_demo(appliance: str) -> pd.DataFrame:
    """读入模拟数据,返回一张三列表格:time(时间) / mains(总功率) / <appliance>(电器真实功率)。"""
    mains = pd.read_csv(DATA_DIR / "mains.csv", parse_dates=["time"])     # parse_dates 把时间列解析成时间类型
    app = pd.read_csv(DATA_DIR / "appliances" / f"{appliance}.csv", parse_dates=["time"])
    # 按时间戳把两张表左右拼起来(和 Excel 的 VLOOKUP 一个意思)
    return mains.merge(app, on="time").rename(columns={"power": appliance})


def load_ukdale_channel(path):
    """读一个 UK-DALE 渠道文件:两列文本(UNIX 时间戳 秒, 功率瓦)。"""
    df = pd.read_csv(path, sep=r"\s+", header=None, names=["time", "power"])
    df["time"] = pd.to_datetime(df["time"], unit="s", errors="coerce")  # UNIX 秒 → 日期时间
    return df.dropna()


def load_ukdale(house_dir, appliance_channels: dict, freq="6s") -> pd.DataFrame:
    """读入一套 UK-DALE 房子的数据,对齐成统一间隔,返回 表格(time/mains/各电器)。

    house_dir          house_1 这样的文件夹路径(里面是 channel_1.dat 等文件)
    appliance_channels 电器名 → 渠道号的对应表,例如 {"kettle": 9, "fridge": 5}
                       渠道号查 github.com/JackKelly/UK-DALE_metadata
    freq               重采样间隔;不同电器的原始采样点对不齐,统一取平均
    """
    house_dir = Path(house_dir)
    # channel_1.dat 固定是总电表(aggregate)
    mains = (load_ukdale_channel(house_dir / "channel_1.dat")
             .set_index("time")["power"].resample(freq).mean())
    out = mains.to_frame("mains")
    # 再把每个电器的渠道读进来,按时间对齐 join 到总表后面
    for name, ch in appliance_channels.items():
        out[name] = (load_ukdale_channel(house_dir / f"channel_{ch}.dat")
                     .set_index("time")["power"].resample(freq).mean())
    return out.dropna()  # 有缺失时刻的行直接丢掉


def create_windows(x, y, window=99, stride=1):
    """【核心函数】在曲线上滑窗,生成 (输入窗口, 窗口中点答案) 的训练样本。

    x       总功率数组(已经除以 3000 归一化)
    y       电器真实功率数组(和 x 一一对应,同样归一化)
    window  相框宽度,默认 99 个点
    stride  相框每次往右挪几个点(挪得越大,样本越少、生成越快)

    返回两个数组:
      x_win  形状 (样本数, 99) —— 一张张"照片"
      y_point 形状 (样本数,)   —— 每张照片对应的答案
    注意答案必须跟着 stride 一起跳:y_point[i] 对应第 i*stride 个窗口的中点,
    两边步长不一致模型就会被"教坏"(这是 NILM 复现最容易踩的 bug)。
    """
    # sliding_window_view 是 numpy 提供的"滑窗"工具,效率很高
    x_win = np.lib.stride_tricks.sliding_window_view(np.asarray(x), window)[::stride]
    # 第 i 个窗口覆盖 x[i*stride : i*stride+99],中点是 x[i*stride+49],
    # 所以答案取 y 从下标 49 开始、每隔 stride 取一个
    y_point = np.asarray(y)[window // 2::stride][:len(x_win)]
    return x_win, y_point


def create_windows_seq(y, window=99, stride=1):
    """给 seq2seq 模型用的答案:不是中点一个数,而是整段 99 个点的答案窗口。"""
    return np.lib.stride_tricks.sliding_window_view(np.asarray(y), window)[::stride]


class NILMDataset(Dataset):
    """把 numpy 数组包装成 PyTorch 的"数据集"。

    PyTorch 训练时需要按批(batch)随机取数据,Dataset 就是约定好
    "一共多少条(len) + 给我第 i 条(getitem)"两个接口的盒子。
    train.py 里的 DataLoader 会自动打乱并按 256 条一组来取。
    """

    def __init__(self, x_win, y_point, y_seq=None):
        # ascontiguousarray:把数据拷贝成内存连续的 float32 数组(torch 要求)
        self.x = torch.as_tensor(np.ascontiguousarray(x_win, dtype=np.float32))
        self.y_point = torch.as_tensor(np.ascontiguousarray(y_point, dtype=np.float32))
        self.y_seq = None
        if y_seq is not None:  # 只有训 seq2seq 时才有第三份数据
            self.y_seq = torch.as_tensor(np.ascontiguousarray(y_seq, dtype=np.float32))

    def __len__(self):
        return len(self.x)  # 一共有多少个训练样本

    def __getitem__(self, i):
        # 训练循环每次拿一条;seq2seq 多返回一份整段答案
        if self.y_seq is not None:
            return self.x[i], self.y_point[i], self.y_seq[i]
        return self.x[i], self.y_point[i]
