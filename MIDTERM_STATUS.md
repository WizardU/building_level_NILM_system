# 期中进度报告：建筑级 NILM 系统

> 更新时间：2026-11-11
> 结论：已从"Mock 演示"升级为**真实数据 + 真实模型 + 真实指标**的可运行系统；Web 与移动端（全英文）均可构建、可连接后端。

---

## 1. 目标与完成度

| 模块 | 期中目标 | 状态 | 说明 |
|------|----------|------|------|
| 数据 | 接入真实数据集 | ✅ | UK-DALE house 1，2014-01 ~ 2014-06，6 秒采样 |
| 数据 | 第二数据集 | ✅ | WHITED v1.1 已下载（994 个 FLAC，225 MB） |
| 模型 | 最简单的真实数据训练 | ✅ | Seq2Point attention + baseline，各 3 epoch |
| 部署 | ONNX 推理 | ✅ | 10 个模型全部导出，数值 parity 通过 |
| 后端 | 真实数据链路 | ✅ | ONNX 后端、正确缓存键、UTC 时间、告警去重 |
| Web | 真实指标展示 | ✅ | Evaluation/Analytics 全部改为真实数据 |
| 移动端 | 可构建、可用 | ✅ | H5 构建通过，界面全英文 |
| 工程质量 | 可验证 | ⚠️ | 19 项端到端 API 检查通过；单测/CI 尚未补 |

---

## 2. 数据

| 项目 | 数值 |
|------|------|
| 数据集 | UK-DALE April 2017, house 1 |
| 时间范围 | 2014-01-01 00:00 → 2014-06-30 23:59 UTC |
| 采样率 | 6 秒（NILMTK HDF5 原始粒度） |
| 总样本 | 2,606,400 |
| 窗口 | W=599（约 59.9 分钟） |
| 划分 | train 60,797 / val 13,013 / test 13,013（每电器） |
| 电器 | fridge / kettle / microwave / dishwasher / washing_machine |

开机样本占比（test，按阈值判定）：

| 电器 | 阈值 | 占比 |
|------|------|------|
| fridge | 50 W | 46.6% |
| kettle | 500 W | 0.47% |
| microwave | 200 W | 0.26% |
| dishwasher | 100 W | 2.09% |
| washing machine | 100 W | 3.87% |

> 说明：kettle/microwave 属于极端不平衡（<1% 正样本），是当前指标的主要难点。

---

## 3. 模型与指标

训练环境：RTX 3070 Laptop 8 GB，PyTorch 2.14.1+cu126，batch 128，Adam 1e-4，3 epoch。
attention 使用加权 Huber（pos_weight=10），baseline 使用 MSE；阈值在验证集上按 event-F1 搜索。

| 电器 | Attention MAE | SAE | State F1 | Event F1 | Baseline MAE | State F1 | Event F1 |
|------|--------------:|----:|---------:|---------:|-------------:|---------:|---------:|
| fridge | 21.31 W | 0.006 | 0.781 | 0.861 | 20.53 W | 0.784 | 0.872 |
| kettle | 9.21 W | 0.153 | 0.744 | 0.755 | 8.14 W | 0.821 | 0.835 |
| microwave | 6.76 W | 0.345 | 0.152 | 0.288 | 7.08 W | 0.329 | 0.413 |
| dishwasher | 8.72 W | 0.105 | 0.845 | 0.810 | 9.53 W | 0.724 | 0.759 |
| washing machine | 11.15 W | 0.013 | 0.884 | 0.840 | 13.38 W | 0.952 | 0.909 |
| **均值** | — | — | **0.681** | **0.711** | — | **0.722** | — |

**解读（如实报告）**

1. attention 在洗碗机、洗衣机上明显更好（MAE、SAE、F1 均改善），尤其 SAE 从 0.316 → 0.013（洗衣机）。
2. baseline 在水壶、微波炉上仍更强，导致**平均 State F1 尚未超过 baseline**（0.681 vs 0.722）。
3. 微波炉是最差项（F1 0.152），正样本仅 0.26%，需要更强的类别不平衡策略。
4. 因此当前不能宣称"改进模型全面更优"。下一步应做：阈值/损失消融、更长训练、focal/BCE 辅助头；若仍无提升，论文应聚焦系统工程贡献并如实讨论。

---

## 4. 系统验证

### 4.1 后端（`scripts/smoke_api.py`）

19 项检查全部通过，包括：

- `/readyz` → `backend=onnx`，5 个电器，`sample_period_s=6`，`dataset=ukdale_house1`
- 登录、建筑/电表、实时读数、`/meters/{id}/current`
- 2 小时分解：240 点曲线，**0.18 s**（首次计算）
- 异步任务：`pending → completed`
- KPI：mains 216 W，F1 0.681，event F1 0.711，推理 64.5 ms
- 账单：0.439 kWh / 5 行分项
- 评测：10 行（5 电器 × 2 模型），13,013 测试窗口
- 告警：英文标题 "System Ready"

### 4.2 Web

- `npm run build` 通过（Vite 4，2.4 MB JS / 786 KB gzip）
- 开发服务器 `http://localhost:3000` 可访问
- 页面：Dashboard（实时曲线 + 家电状态）、Evaluation（雷达图 + 真实指标表）、Analytics（分项账单 + 阈值 + 告警处理）

### 4.3 移动端

- `npm run build:h5` 通过（uni-app 5.32 / Node 22.14）
- 产物：`mobile/dist/build/h5`，`<html lang="en">`
- 页面与 Tab 全部英文：Monitor / Devices / Analytics / Profile
- 设备名、告警文案均为英文（后端新增 `title_en` / `message_en`）

---

## 5. 本轮完成的关键修复

| 问题 | 处理 |
|------|------|
| 训练/评估 KeyError（`f1` vs `state_f1`） | 统一指标 schema，新增 `ml/eval/evaluate.py` |
| 测试集仅 21 窗口 | 真实数据重建为 13,013 窗口/电器 |
| 评估页硬编码 88/94 | 删除，改为真实 ablation + 实测算力指标 |
| 分解缓存按日期 | 改为 `meter|start|end|model_version` |
| 时区偏移 8 小时 | 全链路 UTC，API 输出 `Z` |
| Docker 走启发式 | `/readyz` 显式暴露后端，模型缺失可见 |
| 数据库重复/膨胀 | `(meter_id,timestamp)` 唯一约束 + 入库去重 |
| 告警风暴 | 10 分钟冷却 + 每条告警英文文案 |
| 移动端调用不存在接口 | 新增 `/meters/{id}/current` |
| 移动端中文 | 全英文 UI + 英文设备/告警映射 |

---

## 6. 演示路径（约 5 分钟）

1. `.\scripts\demo_web.ps1` → http://localhost:3000，`admin/admin123`
2. Dashboard：查看总功率、F1/事件 F1、推理耗时、5 台家电状态与曲线
3. Evaluation：查看每电器 MAE/SAE/State-F1/Event-F1（真实测试集）
4. Analytics：分项电量/电费、调整阈值、处理告警
5. `.\scripts\demo_mobile.ps1` → http://127.0.0.1:3100（英文界面）

---

## 7. 剩余工作（答辩前）

**P0**

- [ ] 微波炉/水壶的不平衡策略（focal loss、二阶段分类头、阈值搜索扩展）
- [ ] attention 与 baseline 的公平对比（同训练轮数、同损失、同阈值策略）

**P1**

- [ ] 跨房屋泛化（house 1 → house 2）
- [ ] 单元测试 + CI（pytest / Vitest / GitHub Actions）
- [ ] Alembic 迁移与 Postgres/Timescale 实测
- [ ] SSE 实时推送替代 30 秒轮询
- [ ] WHITED 设备识别实验接入

**P2**

- [ ] ONNX INT8 量化（37.5 MB → 更小）
- [ ] 移动端真机/微信小程序验证

---

## 8. 复现命令

```powershell
# 数据（首次）
python scripts/download_datasets.py --dataset ukdale
python scripts/extract_ukdale.py

# 预处理
cd ml
.\.venv\Scripts\python.exe -m preprocess.ukdale --h5 ..\data\raw\ukdale.h5 --house 1

# 训练 + 评估 + 导出
.\.venv\Scripts\python.exe -m train.train_all --models attention baseline --epochs 3 --device cuda
.\.venv\Scripts\python.exe -m export.export_onnx --all
.\.venv\Scripts\python.exe -m eval.export_thesis_tables

# 验证
cd ..
backend\.venv\Scripts\python.exe scripts\smoke_api.py
```
