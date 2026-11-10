# NILM 系统演示指南（真实数据版）

面向答辩/期中展示，Windows 10/11 环境。

> 当前系统使用 **UK-DALE house 1** 真实数据（6 秒采样、5 类电器），推理后端为
> **ONNX Runtime**。可在 `http://127.0.0.1:8000/readyz` 查看当前后端与模型版本。

---

## 1. 环境要求

| 组件 | 版本 |
|------|------|
| Python | 3.10+ |
| Node.js（Web） | 16+ |
| Node.js（移动端） | **≥ 22.12**（uni-app 要求） |
| 浏览器 | Chrome / Edge |
| 磁盘 | ≥ 10 GB（UK-DALE HDF5 约 5.9 GB） |
| GPU | 可选；有 NVIDIA GPU 时训练更快 |

项目在 `.tools/node-v22.14.0-win-x64` 内置了便携版 Node 22，供移动端构建使用。

---

## 2. 准备数据与模型（仅首次）

```powershell
# 下载 UK-DALE（5.1 GB，可续传）并解压
python scripts/download_datasets.py --dataset ukdale
python scripts/extract_ukdale.py

# 生成真实数据窗口
cd ml
.\.venv\Scripts\python.exe -m preprocess.ukdale --h5 ..\data\raw\ukdale.h5 --house 1

# 训练 + 评估 + 导出 ONNX
.\.venv\Scripts\python.exe -m train.train_all --models attention baseline --epochs 3 --device cuda
.\.venv\Scripts\python.exe -m export.export_onnx --all
```

一键脚本会自动检查这些步骤，缺失时提示或执行：

```powershell
.\scripts\demo_web.ps1 -Download     # 首次：下载 + 预处理 + 训练 + 启动
.\scripts\demo_web.ps1              # 之后：直接启动
```

可选：下载 WHITED（电器启动暂态数据，用于设备识别实验）

```powershell
python scripts/download_datasets.py --dataset whited
```

---

## 3. 一键启动

### Web

```powershell
.\scripts\demo_web.ps1
```

会打开三个窗口：Backend（8000）、Replay（推送真实日数据）、Web（3000）。

### 移动端 H5

```powershell
.\scripts\demo_mobile.ps1
```

打开 http://127.0.0.1:3100（英文界面）。

### 手动启动（排错）

```powershell
# 窗口 1
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# 窗口 2
backend\.venv\Scripts\python.exe -m adapters.replay.cli --meter-id 101 --speed 20

# 窗口 3
cd web
npm run dev
```

首次启动会自动建库，并预载最近 24 小时的真实 UK-DALE 采样（约 14,400 条）。

---

## 4. 登录与页面

| 项 | 值 |
|----|-----|
| 地址 | http://localhost:3000 |
| 账号 | `admin` |
| 密码 | `admin123` |
| 默认建筑 | Building A · UK-DALE House 1 |
| 默认电表 | UK-DALE House 1 · Mains |

### 4.1 Dashboard（控制台）

- 顶部显示推理后端（ONNX / 降级）与模型版本
- KPI：总功率、激活设备数、状态 F1、事件 F1、MAE、推理耗时
- 曲线：总功率 + 5 台家电分解曲线（最近 2 小时）
- 家电卡片：实时功率、状态、模型事件 F1、时段电量、开机阈值
- 点击「刷新分解」触发异步任务并轮询完成

### 4.2 Evaluation（算法评估）

- 雷达图：State F1 / Event F1 / Precision / Recall / SAE Score
- 每电器测试集指标表（10 行 = 5 电器 × 2 模型）
- 数据来自 `ml/checkpoints/ablation_metrics.json`，无占位分数

### 4.3 Analytics（用电分析）

- 分项电量/电费（基于真实时间戳积分）
- 未分解电量单独列出，避免把基荷摊给电器
- 可修改功率阈值与电价（持久化到 `settings` 表）
- 告警列表支持「标记已处理」

---

## 5. 端口

| 服务 | 端口 |
|------|------|
| FastAPI | 8000 |
| Vue Web | 3000 |
| 移动端 H5 | 3100 |

释放端口：

```powershell
netstat -ano | findstr ":8000"
taskkill /PID <PID> /F
```

---

## 6. 常见问题

**Q1 页面显示「当前推理后端不是 ONNX」**

模型未加载。检查：

```powershell
curl http://127.0.0.1:8000/readyz
dir ml\checkpoints\*_attention.onnx
```

若为空：`cd ml; .\.venv\Scripts\python.exe -m export.export_onnx --all`。

**Q2 Dashboard 没有曲线**

- 确认数据库有数据：`/measurements/realtime?meter_id=101`
- 确认 replay 适配器在运行（或重新执行 `demo_web.ps1` 让 seed 预载一天数据）
- 曲线窗口是「最近 2 小时」，若数据太旧需要重新 seed

**Q3 移动端构建报 engine 错误**

uni-app 要求 Node ≥ 22.12。使用脚本自带的 `.tools/node-v22.14.0-win-x64`，或：

```powershell
node --version   # 需 >= 22.12
```

**Q4 训练很慢 / 没有 GPU**

`--device cpu` 可用，但建议至少 3 个 epoch；没有 GPU 时把窗口数或 epoch 调小。

**Q5 端口被占用**

先关闭旧进程，或修改 `web/vite.config.js`、`mobile/src/manifest.json` 与启动命令中的端口。

---

## 7. 数据集与许可

- UK-DALE：CC BY 4.0，引用 Kelly & Knottenbelt, *Scientific Data* 2:150007 (2015)。
- WHITED：CC BY 4.0，引用 Kahl et al. (2016)。

数据不进入 Git；`data/raw/datasets_manifest.json` 记录来源、大小与 SHA-256。
