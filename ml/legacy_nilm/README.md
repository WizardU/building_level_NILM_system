# NILM 非侵入式负荷监测系统

基于 Seq2Point / Seq2Seq 深度学习模型的负荷分解(NILM)演示系统。系统只接入入户总线的一路功率数据,即可估计出电水壶、微波炉、洗衣机、冰箱等单个电器的功率曲线,并通过网页界面展示分解结果和评测指标。

## 1. 原理简介

非侵入式负荷监测(Non-Intrusive Load Monitoring, NILM)要解决的问题是:在只安装一块总电表的前提下,从总功率曲线中分离出每个电器的用电情况,从而不必给每个电器单独安装监测插座,就能知道"电用在了哪里"。

本系统的处理流程:

```text
总电表曲线(每 6 秒一个采样点)
      | 滑动窗口截取,每次取 99 个点
      v
Seq2Point CNN / Seq2Seq LSTM
      | 输出窗口中点处的功率预测
      v
拼接还原,得到电器功率曲线
      | 与真实曲线对比
      v
MAE / SAE / F1 指标 + Streamlit 网页展示
```

系统内置一套 30 天的模拟家庭用电数据(总电表 = 家底负荷 + 各电器 + 传感器噪声),用于跑通全流程;同时提供 UK-DALE 数据集的加载接口,可以换成真实数据重新训练。

## 2. 环境要求

- Windows 10/11(Linux、macOS 也可以,个别命令需要调整)
- Python 3.10 及以上版本,推荐 3.12
- 训练和推理在 CPU 上即可完成,有 NVIDIA 显卡会更快

## 3. 安装

(1)安装 Python。到 python.org 下载 3.12 版安装包,安装时勾选 "Add python.exe to PATH"。

(2)在项目根目录打开命令行,创建并激活虚拟环境:

```bat
python -m venv .venv
.venv\Scripts\activate
```

(3)安装依赖:

```bat
pip install -r requirements.txt
```

如果希望使用 GPU 训练,先确认装好了 NVIDIA 驱动和 CUDA,再执行 `pip install torch --index-url https://download.pytorch.org/whl/cu124` 覆盖安装 GPU 版 torch,其余依赖不变。

使用 PyCharm 的场合:File → Open 打开本项目目录,然后在 Settings → Project → Python Interpreter 中把解释器指向 `.venv\Scripts\python.exe`,依赖安装步骤相同。

## 4. 使用步骤

按顺序执行三步。

第一步,生成模拟数据(约几秒钟):

```bat
python make_demo_data.py
```

运行后 `data/` 目录下会生成总电表数据 `mains.csv`、四个电器的真实功率数据 `appliances/*.csv`,以及配置文件 `meta.json`。

第二步,训练模型。每个电器训练一个独立的模型:

```bat
python train.py --appliance kettle --model seq2point --epochs 6
python train.py --appliance microwave --model seq2point --epochs 6
python train.py --appliance washing_machine --model seq2point --epochs 6
python train.py --appliance fridge --model seq2point --epochs 6
python train.py --appliance kettle --model seq2seq --epochs 4
```

CPU 上 seq2point 每轮约 11 秒,一个电器一分钟出头就能训完。训练脚本会把数据按时间顺序切成 8 : 1 : 1 三份,分别用于训练、验证和测试;每轮训练都会打印损失,训练结束在最后 10% 的数据上输出一组测试指标,模型保存在 `outputs/checkpoints/` 目录。

可调参数(均有默认值):

| 参数 | 含义 | 默认值 |
|---|---|---|
| `--appliance` | 目标电器名 | kettle |
| `--model` | 模型类型,seq2point 或 seq2seq | seq2point |
| `--window` | 输入窗口长度(采样点数) | 99 |
| `--stride` | 切窗口时的滑动步长 | 4 |
| `--epochs` | 训练轮数 | 6 |
| `--batch-size` | 每批样本数 | 256 |
| `--lr` | 学习率 | 0.001 |

第三步,启动网页界面:

```bat
python -m streamlit run app.py
```

终端出现 `Local URL: http://localhost:8501` 后,在浏览器打开该地址即可。

## 5. 界面说明

左侧是控制面板:选择目标电器、选择分解模型、拖动时间条控制主图显示哪一段;下方会列出当前已经训练好的模型。

右侧依次是:

- 四个指标卡:MAE、SAE、开关状态 F1、事件检测 F1,数值只针对当前所选时间段计算;
- 功率曲线对比图:灰色为总电表读数,蓝色实线为该电器的真实功率,橙色虚线为模型预测,三条线叠在一张图上,直观看出预测和真实值的贴合程度;
- 每日电能柱状图:对比真实用电量和模型估计的用电量(单位 kWh);
- 原始数据预览:折叠区,点开可查看当前时间段的数据表。

## 6. 代码结构

| 文件 | 职责 |
|---|---|
| make_demo_data.py | 生成模拟家庭用电数据(总表 = 底噪 + 各电器 + 噪声) |
| data_utils.py | 数据读取、UK-DALE 加载接口、滑动窗口切分、PyTorch 数据集 |
| models.py | Seq2PointCNN 和 Seq2SeqLSTM 两个网络的定义 |
| train.py | 训练脚本:切分数据、训练循环、保存最优模型、输出测试指标 |
| disaggregate.py | 推理:把整条总功率曲线切窗口预测再拼接还原 |
| evaluate.py | 评测指标:MAE、SAE、状态级与事件级 P/R/F1 |
| app.py | Streamlit 网页界面 |
| data/ | 数据目录(make_demo_data.py 生成) |
| outputs/checkpoints/ | 训练得到的模型权重 |

想读懂代码,建议按这个顺序看:先看 `make_demo_data.py` 明白数据长什么样,再看 `data_utils.py` 里的 `create_windows()`(滑动窗口是整个方法的核心),然后看 `models.py` 和 `train.py`,最后看 `disaggregate.py` 和 `app.py`。各文件开头都写有说明和背景概念。

## 7. 两种模型的区别

两种模型解决同一个问题:给定一段总功率窗口,预测对应的电器功率。

Seq2Seq(Kelly & Knottenbelt, 2015)输入长度 L 的窗口,输出长度 L 的功率序列,一次还原整段曲线。信息量足,但模型大、训练慢,预测段边界容易发虚。

Seq2Point(Zhang et al., 2018)输入长度 L 的窗口,只输出窗口正中间一个点的功率。推理时让窗口逐点滑动、拼接成完整曲线。参数量约为 seq2seq 的十分之一,训练快、精度通常更好,是目前低频 NILM 论文里最常见的对比基线。

本项目中两者共用同一套窗口和数据流水线,训练时用 `--model` 参数切换,界面上也可以直接对比两者的分解结果。

## 8. 评测指标

| 指标 | 计算方式 | 说明 |
|---|---|---|
| MAE | 各时刻绝对误差的平均值,单位瓦 | 回归精度,越小越好 |
| SAE | 预测总电能与真实总电能之差的相对比例 | 衡量能量守恒,越小越好 |
| 状态 P/R/F1 | 按开/关阈值二值化后逐采样点计算 | 精确率反映误报,召回率反映漏报 |
| 事件 P/R/F1 | 每次"从关到开"算一个事件,预测事件落在真实事件前后 tol 个采样点内算命中 | 更贴近实际应用,对边界偏移宽容、对漏检严格 |

## 9. 数据集

模拟数据只用于跑通流程,做正式实验应使用公开数据集。常用的低频 NILM 数据集如下,均免费开放科研使用:

| 数据集 | 规模 | 采样间隔 | 下载 |
|---|---|---|---|
| UK-DALE | 5 户英国家庭,2012 年起 | 6 s(另有 16 kHz 录音) | http://jack-kelly.com/data |
| REDD | 6 户美国家庭,2011 | 1~3 s | http://redd.csail.mit.edu |
| REFIT | 20 户英国家庭,约 2 年 | 8 s | https://pureportal.strath.ac.uk/en/datasets/refit-electrical-load-measurements-cleaned |
| AMPds2 | 1 户加拿大家庭,2 年 | 1 min | https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/FIE0S4 |
| ECO | 6 户瑞士家庭 | 1 s | https://www.vs.inf.ethz.ch/res/show.html?what=eco-data |
| Pecan Street | 数千户美国家庭 | 1 min | https://www.pecanstreet.org/dataport (需注册) |

入门建议从 UK-DALE 的 house 1 开始,只取 kettle、fridge、washing machine、microwave 四类电器,与本项目的演示设定一致。接入方法:下载低频 CSV 版本并解压后,用 `data_utils.py` 提供的加载函数读入:

```python
from data_utils import load_ukdale

# 第二个参数是电器名到渠道号的对应表,渠道号查每套房子的说明文件
df = load_ukdale("ukdale/house_1", {"kettle": 9, "fridge": 5, "washing_machine": 6})
```

读进来的表和模拟数据结构一致(time / mains / 各电器列),再按 `mains.csv` 和 `appliances/*.csv` 的格式存到 `data/` 目录,后续训练和界面无需任何改动。各房子每个电器对应哪个渠道,见渠道说明文档。

## 10. 相关开源项目

| 项目 | 说明 |
|---|---|
| NILMTK (github.com/nilmtk/NILMTK) | NILM 领域的标准工具库,内置多种数据集加载器、预处理方法和传统算法 |
| nilmtk-contrib (github.com/nilmtk/nilmtk-contrib) | NILMTK 的深度学习扩展,收录 seq2point、seq2seq、RNN、BERT、Transformer 等模型,适合快速跑通多种方法做对比 |
| seq2point-nilm (github.com/MingjunZhong/seq2point-nilm) | seq2point 原论文作者放出的实现 |
| NeuralNetNilm (github.com/MingjunZhong/NeuralNetNilm) | 同一作者,包含 seq2seq 与 seq2point 两套实现 |
| BERT4NILM (github.com/Zhenhua18/BERT4NILM) | 双向 Transformer 结构的 NILM 模型 |
| awesome-NILM-with-code (github.com/zhgqcn/awesome-NILM-with-code) | 按模型和年份整理的 NILM 论文与代码列表 |
| UK-DALE_metadata (github.com/JackKelly/UK-DALE_metadata) | UK-DALE 各房子的电器渠道对照表 |

## 11. 关于是否基于现有项目开发

分三个层面考虑。

数据层面,直接使用公开数据集。自己部署电表和分路监测设备周期长、成本高,而且使用标准数据集的结果才能与文献中的数值直接比较。

代码层面,建议参考他人实现、自己搭建项目。seq2point 的核心代码只有几十行,自己实现一遍才能真正掌握窗口长度、归一化、拼接推理这些细节;多数公开实现基于 Theano 或旧版 TensorFlow,直接整套移植反而要花大量时间处理环境问题。需要快速比较十几种模型时,可以在 Linux 或 WSL 里使用 nilmtk-contrib。

引用方面,使用数据集和参考他人实现时,按学术惯例引用对应论文(见文末参考文献),注意查看各仓库的开源许可证(NILMTK 为 MIT,上述项目均为宽松许可)。

## 12. 常见问题

python 命令找不到。确认安装时勾选了 Add to PATH,或者直接使用完整路径 `.venv\Scripts\python.exe`。

提示 No module named torch / streamlit。虚拟环境没有激活,或者依赖没有安装,重做第 3 节第 (3) 步。

8501 端口被占用。启动命令末尾追加 `--server.port 8502`,换一个端口。

模型文件加载报错。权重和网络结构是配套的,修改过 `models.py` 之后需要重新训练,旧的 .pt 文件无法直接复用。

训练时损失不下降。优先检查三处:输入和标签是否都做了同样的归一化;标签是否与窗口步长一致对齐(见 `create_windows` 注释);验证与推理时的预处理是否一致。

## 参考文献

- Zhang, C., Zhong, M., Wang, Z., Goddard, N., Sutton, C. Sequence-to-point learning for energy disaggregation. NeurIPS 2018.
- Kelly, J., Knottenbelt, W. Neural NILM: Deep neural networks applied to energy disaggregation. BuildSys 2015.
- Kelly, J., Knottenbelt, W. The UK-DALE dataset, domestic appliance-level electricity demand and whole-house demand from five UK homes. Scientific Data 2, 150007 (2015).
- Kolter, J. Z., Johnson, M. J. REDD: A public data set for energy disaggregation research. KDD Workshop 2011.
- Murray, D., Stankovic, L., Stankovic, V. An electrical load measurements dataset of United Kingdom households from a two-year longitudinal study. Scientific Data 4, 160122 (2017). (REFIT 数据集论文)
- Yue, Z., et al. BERT4NILM: A deep bidirectional transformer model for non-intrusive load monitoring. ACM BuildSys 2020.
