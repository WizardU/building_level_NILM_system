# -*- coding: utf-8 -*-
"""
make_demo_data.py —— 生成一套"模拟家庭用电数据",用来先把整个系统跑起来。

【为什么需要这一步?】
做 NILM(非侵入式负荷监测)需要两类数据:
  1. 总电表读数 mains    —— 全屋电器功率加在一起的一根曲线(系统唯一能"看到"的东西)
  2. 每个电器的单独读数  —— 当"标准答案"用,训练时告诉网络猜得对不对
现实中第 2 类数据要给每个电器装监测插座,很麻烦。所以我们用电脑模拟一套出来:
    总电表 = 家里底噪 + 各个电器 + 传感器噪声
运行后数据保存到项目下的 data/ 文件夹(CSV 格式,用 Excel 直接打开就能看)。

【以后想用真实数据?】
换 UK-DALE 等公开数据集即可,见 README.md 和 data_utils.py 里的 load_ukdale()。

运行方式:在 PyCharm 里右键本文件 → Run,或在终端执行
    python make_demo_data.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

# ---------- 基本参数(想改数据长度/精度,改这里就行) ----------
SEED = 42             # 随机数种子:固定后每次生成的数据一模一样,方便复现
SAMPLE_SEC = 6        # 采样间隔:每 6 秒记录一次功率(著名数据集 UK-DALE 也是 6 秒)
DAYS = 30             # 生成多少天的数据
START = "2025-09-01"  # 数据从哪天开始(只影响时间戳,不影响波形)
DATA_DIR = Path(__file__).resolve().parent / "data"  # 数据保存目录:项目根/data

# 每个电器的"铭牌信息":
#   on_threshold  判定电器"开着"的功率门槛(瓦)。比如水壶只有 0 瓦和 2000 瓦两种
#                 状态,高于 50 瓦就算开着。后面计算 F1 指标时会用到
#   nominal_power 正常工作时的功率(瓦),只是备注
APPLIANCE_META = {
    "kettle":          {"on_threshold": 50,  "nominal_power": 2000},
    "microwave":       {"on_threshold": 200, "nominal_power": 1100},
    "washing_machine": {"on_threshold": 20,  "nominal_power": 900},
    "fridge":          {"on_threshold": 50,  "nominal_power": 140},
}

# 总采样点数 = 天数 × 每天 86400 秒 ÷ 每 6 秒一个点(30 天 = 432000 个点)
T = DAYS * 86400 // SAMPLE_SEC
rng = np.random.default_rng(SEED)  # 随机数生成器(带着种子,保证可复现)


def _place(power, start_sec, dur_sec, watts):
    """把一次用电写进功率曲线:从第 start_sec 秒开始,持续 dur_sec 秒,功率 watts 瓦。

    power 是一个很长的一维数组,每个格子代表 6 秒;
    比如"开机后第 8315 个格子" = 从 0 时刻算起第 8315×6 秒那一点的功率。
    """
    i0 = start_sec // SAMPLE_SEC                      # 开始时刻 → 换算成数组下标
    i1 = min(i0 + max(dur_sec // SAMPLE_SEC, 1), T)   # 结束下标(不能超出数组)
    if i0 < T:
        power[i0:i1] = watts                          # 这一段全部填成 watts 瓦


def add_kettle(power):
    """电水壶:每天烧水 2~5 次,集中在做饭喝茶的钟点,一次 90~300 秒,2000 瓦。"""
    for day in range(DAYS):
        for _ in range(rng.integers(2, 6)):  # 随机决定今天烧几次水(2~5 次)
            hour = int(rng.choice([7, 8, 12, 13, 17, 18, 19, 20, 21]))  # 随机挑个钟点
            # 第 day 天的第 hour 小时内,再随机一个偏移量,得到开始秒数
            start = day * 86400 + hour * 3600 + int(rng.integers(0, 3600))
            _place(power, start, int(rng.integers(90, 300)), 2000.0)


def add_microwave(power):
    """微波炉:每天用 1~3 次,一次 40~180 秒,1100 瓦。"""
    for day in range(DAYS):
        for _ in range(rng.integers(1, 4)):
            hour = int(rng.choice([7, 11, 12, 17, 18, 19, 20]))
            start = day * 86400 + hour * 3600 + int(rng.integers(0, 3600))
            _place(power, start, int(rng.integers(40, 180)), 1100.0)


# 洗衣机的一个完整洗涤程序分 5 个阶段:(持续秒数, 该阶段功率)
WASH_PHASES = [(120, 100.0), (720, 800.0), (120, 200.0), (360, 500.0), (240, 900.0)]


def add_washing_machine(power):
    """洗衣机:每天 0~2 次洗涤程序,每次按 浸泡→洗涤→排水→漂洗→脱水 五段走完。"""
    for day in range(DAYS):
        # 80% 的概率今天洗衣服,洗 1~2 次;否则今天不洗
        runs = int(rng.integers(1, 3)) if rng.random() < 0.8 else 0
        for _ in range(runs):
            # 上午 8 点到晚上 8 点之间随机开始
            cursor = day * 86400 + int(rng.integers(8, 20)) * 3600 + int(rng.integers(0, 3600))
            for dur, watts in WASH_PHASES:
                _place(power, cursor, dur, watts)
                cursor += dur  # 上一阶段结束的时刻 = 下一阶段开始的时刻


def add_fridge(power):
    """冰箱:压缩机循环工作 —— 运转 10~18 分钟,停 25~45 分钟,运转时 140 瓦。"""
    cursor = 0  # 从第 0 秒开始一直循环到数据末尾(冰箱 7×24 小时工作)
    while cursor < T:
        on = int(rng.integers(600, 1081)) // SAMPLE_SEC    # 运转 600~1080 秒
        off = int(rng.integers(1500, 2701)) // SAMPLE_SEC  # 停机 25~45 分钟
        power[cursor:min(cursor + on, T)] = 140.0
        cursor += on + off


def main():
    # 1. 依次生成 4 个电器各自的功率曲线(互相独立,各自是一条长数组)
    idx = pd.date_range(START, periods=T, freq=f"{SAMPLE_SEC}s")  # 时间戳列表
    appliance_powers = {}
    for name, fn in [("kettle", add_kettle), ("microwave", add_microwave),
                     ("washing_machine", add_washing_machine), ("fridge", add_fridge)]:
        p = np.zeros(T)  # 先建一条全 0 的曲线
        fn(p)            # 把这个电器的用电"画"上去
        appliance_powers[name] = p

    # 2. 家里底噪(冰箱插头、路由器、待机功耗等):在 50~160 瓦之间慢慢漂移
    base = np.clip(90 + np.cumsum(rng.normal(0, 1.5, T)), 50, 160)

    # 3. 总电表 = 底噪 + 所有电器 + 传感器噪声(±4 瓦)
    #    —— 这正是 NILM 要解的题:模型只能拿到右边这根加总的曲线
    mains = base + sum(appliance_powers.values()) + rng.normal(0, 4, T)
    mains = np.clip(mains, 0, None)  # 功率不会是负数

    # 4. 保存成 CSV:总表一份,每个电器一份,再存一份配置 meta.json
    (DATA_DIR / "appliances").mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"time": idx, "mains": mains.round(1)}).to_csv(DATA_DIR / "mains.csv", index=False)
    for name, p in appliance_powers.items():
        pd.DataFrame({"time": idx, "power": p}).to_csv(DATA_DIR / "appliances" / f"{name}.csv", index=False)

    meta = {"sample_sec": SAMPLE_SEC, "days": DAYS, "start": START, "appliances": APPLIANCE_META}
    (DATA_DIR / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    # 5. 打印一份小结,方便确认数据生成正常
    print(f"Generated {DAYS} days x {SAMPLE_SEC}s data -> {DATA_DIR}")
    print(f"mains.csv: {T} rows, mean {mains.mean():.0f} W")
    for name, p in appliance_powers.items():
        print(f"  {name:16s} on-ratio {(p > 0).mean():.2f}  energy {p.sum() * SAMPLE_SEC / 3.6e6:.1f} kWh")


if __name__ == "__main__":
    main()
