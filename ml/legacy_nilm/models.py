# -*- coding: utf-8 -*-
"""
models.py —— 两个"神经网络模型"的定义(整个系统的大脑)。

【背景:网络到底在干什么?】
NILM 的目标:只看全屋总电表的一根曲线,让网络"猜"出某个电器(如电水壶)
的功率曲线。做法很朴素:
  1. 从总功率曲线上截 99 个点当输入
  2. 网络输出预测(见下面两种网络,输出方式不同)
  3. 训练 = 拿几十万条 (输入, 正确答案) 让网络不断修正自己的预测

本文件两种网络选哪个都能用,界面里可以切换对比:
  Seq2PointCNN  卷积网络,参数少、训练快(NILM 最常用,论文 Zhang et al., NeurIPS 2018)
  Seq2SeqLSTM   循环网络,一次输出整段窗口(论文 Kelly & Knowlton, 2013)
"""

import torch.nn as nn


class Seq2PointCNN(nn.Module):
    """Seq2Point 卷积网络(推荐入门使用)。

    输入: 一个窗口的总功率,形状 (批大小, 99)
    输出: 窗口正中间那一点的电器功率,形状 (批大小,)

    名字里的 "Seq2Point"(序列到点)= 输入一串序列,只输出 1 个点。
    为什么只输出 1 个点?因为答案只有一个时刻,网络不用费心思猜整段曲线
    的边界,学习目标更简单、精度通常更好。
    """

    def __init__(self, window: int = 99):
        # window: 输入窗口长度(一次给网络看多少个采样点)。
        #         99 是原论文的设定;取奇数是为了"正中间"刚好有 1 个点
        super().__init__()
        # nn.Conv1d(输入通道, 输出通道, 卷积核宽度)
        # 卷积可以理解为:用一根宽度为"核宽"的尺子在曲线上滑动,
        # 检测局部形状(比如"突然升高 2000 瓦"这种模式)。
        # 输出通道越多,能识别的特征种类越多,计算量也越大。
        # ReLU 是激活函数,给网络加"弯折能力",没有它再多层也只能学直线关系。
        self.convs = nn.Sequential(
            nn.Conv1d(1, 30, 10), nn.ReLU(),  # 第 1 层:看最原始的波形
            nn.Conv1d(30, 30, 8), nn.ReLU(),  # 越往后组合出的特征越抽象
            nn.Conv1d(30, 40, 6), nn.ReLU(),
            nn.Conv1d(40, 40, 5), nn.ReLU(),
            nn.Conv1d(40, 50, 4), nn.ReLU(),
        )
        # 每过一层卷积,长度缩短 (核宽-1):99 → 90 → 83 → 78 → 74 → 71
        # 71 个位置 × 50 个通道 = 3550 个特征数
        flat = 50 * self._flat_len(window)
        # 最后一根全连接层:把 3550 个特征汇总成 1 个数 = 预测功率
        # Dropout(0.2):训练时随机"蒙住"20% 的信号,逼网络别死记硬背(防过拟合)
        self.head = nn.Sequential(nn.Dropout(0.2), nn.Flatten(), nn.Linear(flat, 1))

    @staticmethod
    def _flat_len(window):
        """算卷积走完后还剩几个点:每层长度减 (核宽-1)。"""
        for k in (10, 8, 6, 5, 4):
            window -= k - 1
        return window

    def forward(self, x):  # x: (批大小, 99)
        # Conv1d 要求形状 (批, 通道, 长度),所以用 unsqueeze 补一个通道维
        # 输出 (批, 1) → squeeze(-1) 压成 (批,)
        return self.head(self.convs(x.unsqueeze(1))).squeeze(-1)


class Seq2SeqLSTM(nn.Module):
    """Seq2Seq 循环网络(和 Seq2Point 做对比用的)。

    输入: 一个窗口的总功率,形状 (批大小, 99)
    输出: 整段 99 个点的电器功率预测,形状 (批大小, 99)
          (实际使用时和 seq2point 一样,只取正中间那个点)

    LSTM(长短期记忆网络)擅长处理"前后有关系的序列":
    编码器把 99 个点读成摘要,解码器再逐点还原出电器功率。
    缺点:参数量约为 CNN 的 10 倍,训练也慢得多。
    """

    def __init__(self, window: int = 99, hidden: int = 128):
        super().__init__()
        # 先用一层小卷积做"预处理",提取局部波形,hidden=128 是记忆容量
        self.conv = nn.Sequential(nn.Conv1d(1, 16, 3, padding=1), nn.ReLU())
        # 编码器:双向 = 从左往右 + 从右往左各读一遍,输出 2×128 维
        self.encoder = nn.LSTM(16, hidden, batch_first=True, bidirectional=True)
        # 解码器:拿着编码结果逐个时间步"翻译"回功率曲线
        self.decoder = nn.LSTM(hidden * 2, hidden, batch_first=True)
        self.fc = nn.Linear(hidden, 1)  # 每个时间步输出 1 个功率值

    def forward(self, x):  # x: (批大小, 99)
        z = self.conv(x.unsqueeze(1)).transpose(1, 2)  # 换成 LSTM 要的 (批, 长度, 通道)
        enc_out, _ = self.encoder(z)
        dec_out, _ = self.decoder(enc_out)
        return self.fc(dec_out).squeeze(-1)  # (批大小, 99)


def build_model(name: str, window: int = 99) -> nn.Module:
    """按名字创建模型,方便配置文件里只存一个字符串('seq2point'/'seq2seq')。"""
    if name == "seq2point":
        return Seq2PointCNN(window)
    if name == "seq2seq":
        return Seq2SeqLSTM(window)
    raise ValueError(f"unknown model: {name}")
