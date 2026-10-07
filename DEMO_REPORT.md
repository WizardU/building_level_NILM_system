# 建筑级 NILM 系统 Web Demo 演示报告

## 一、Demo 概述

### 1.1 演示目的

本 Demo 用于验证和展示建筑级非侵入式负荷监测（NILM）系统的完整运行流程，包括：

- 模拟电表数据的实时推送
- 后端对测量数据的接收、存储与事件检测
- 基于 Seq2Point + Attention 的负荷分解推理
- Web 控制台对实时功率、家电状态、能耗账单与模型指标的可视化展示

### 1.2 演示场景

模拟一栋建筑（Building A）的主电表（Meter 101），以 1 Hz 频率推送总功率数据，系统实时分解出冰箱、电热水壶、微波炉、洗碗机、洗衣机五类家电的用电状态与能耗。

---

## 二、系统环境

| 项目 | 配置 |
|------|------|
| 操作系统 | Windows 10/11（亦支持 Linux/macOS） |
| Python | 3.10+ |
| Node.js | 16+ |
| 后端框架 | FastAPI 0.110+ |
| 前端框架 | Vue 3 + Element Plus + ECharts |
| 数据库 | SQLite（本地演示）/ PostgreSQL+TimescaleDB（Docker） |
| 推理引擎 | ONNX Runtime |
| 浏览器 | Chrome / Edge / Firefox |

---

## 三、演示前准备

### 3.1 启动方式

**一键启动（CMD）**：

```cmd
scripts\demo_web.cmd
```

**一键启动（Git Bash）**：

```bash
bash scripts/demo_web.sh
```

脚本会自动打开三个窗口：

1. **NILM Backend**：FastAPI 服务，地址 `http://127.0.0.1:8000`
2. **NILM Replay**：数据重放器，向 backend 推送模拟数据
3. **NILM Web**：前端开发服务器，地址 `http://localhost:3000`

### 3.2 登录信息

| 字段 | 值 |
|------|-----|
| 用户名 | `admin` |
| 密码 | `admin123` |
| 默认建筑 | Building A |
| 默认电表 | Meter 101 |

---

## 四、系统架构（演示视角）

```
┌─────────────────┐     HTTP/1Hz      ┌─────────────────┐
│  Replay Adapter │  ───────────────▶  │  FastAPI Backend│
│  (synthetic     │   measurements    │  /api/v1        │
│   data)         │                   │                 │
└─────────────────┘                   │  JWT Auth       │
                                      │  Disaggregation │
                                      │  Analytics      │
                                      └────────┬────────┘
                                               │
                                               │ RESTful API
                                               ▼
                                      ┌─────────────────┐
                                      │  Vue 3 Web      │
                                      │  Console        │
                                      │  localhost:3000 │
                                      └─────────────────┘
```

---

## 五、演示流程与功能说明

### 5.1 登录页

打开 http://localhost:3000，输入账号 `admin` / `admin123`，点击登录。

**验证点**：
- 前端调用 `POST /api/v1/auth/login`
- 后端返回 JWT access_token
- 前端将 token 存入 localStorage，并跳转 Dashboard

---

### 5.2 Dashboard（控制台）

#### 5.2.1 页面布局

- **顶部工具栏**：建筑选择器、电表选择器、刷新分解按钮
- **KPI 卡片**：总入户功率、激活设备数、F1-Score、MAE、SAE
- **实时曲线图**：总功率 + 各家电分解功率
- **家电网格**：设备名称、实时功率、开关状态、置信度、今日用电量

#### 5.2.2 核心交互

1. 选择建筑/电表后，点击“刷新分解”。
2. 前端调用 `POST /api/v1/disaggregation/run` 提交异步任务。
3. 后端从数据库读取最近 2 小时 aggregate 数据，使用 ONNX Runtime 逐电器推理。
4. 任务完成后，前端调用 `GET /api/v1/disaggregation/result` 获取分解结果。
5. 曲线图和家电网格动态刷新。

#### 5.2.3 技术细节

- 窗口长度 W=599，stride=30
- 推理结果经反标准化后得到实际功率（W）
- 当功率 > 50W 时判定为“开启”状态
- 页面每 15 秒自动轮询一次数据

---

### 5.3 Evaluation（算法评估）

#### 5.3.1 页面内容

- **左侧雷达图**：Baseline 1D-CNN vs Proposed（Dilated Conv + Attention）五维指标对比
  - F1-Score
  - MAE Error
  - SAE Billing Error
  - Inference Speed
  - Generalization
- **右侧说明卡片**：模型改进点描述

#### 5.3.2 数据来源

- `GET /api/v1/analytics/reports`
- 指标来自 `ml/checkpoints/ablation_metrics.json`
- 由 `ml/eval/export_thesis_tables.py` 生成

---

### 5.4 Analytics（用电分析）

#### 5.4.1 页面内容

- **分项用电账单**：各家电 kWh、预估电费、占比进度条
- **安全预警配置**：入户总功率阈值滑块
- **告警日志**：过载、干烧等事件记录

#### 5.4.2 数据来源

- `GET /api/v1/analytics/energy`
- `GET /api/v1/analytics/alerts`
- 当实时功率超过阈值时，`POST /measurements/upload` 会自动写入 Alert 记录

---

## 六、API 调用验证

### 6.1 登录

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

**预期响应**：返回 `access_token` 和 `refresh_token`。

### 6.2 获取建筑列表

```bash
curl -H "Authorization: Bearer <token>" \
  http://127.0.0.1:8000/api/v1/buildings
```

**预期响应**：返回 Building A 的信息。

### 6.3 获取实时数据

```bash
curl -H "Authorization: Bearer <token>" \
  "http://127.0.0.1:8000/api/v1/measurements/realtime?meter_id=101"
```

**预期响应**：返回最新总功率、电压、电流。

### 6.4 运行分解任务

```bash
curl -X POST http://127.0.0.1:8000/api/v1/disaggregation/run \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"meter_id":101,"start":"2026-10-07T08:00:00","end":"2026-10-07T10:00:00"}'
```

**预期响应**：返回 `task_id`。

### 6.5 查询分解结果

```bash
curl -H "Authorization: Bearer <token>" \
  "http://127.0.0.1:8000/api/v1/disaggregation/result?meter_id=101&start=2026-10-07T08:00:00&end=2026-10-07T10:00:00"
```

**预期响应**：返回总电量、各家电能耗、时间序列。

---

## 七、演示结果

### 7.1 实时数据接入

Replay Adapter 以 20 倍速推送合成数据，后端 `/measurements/upload` 成功接收并落库。

### 7.2 负荷分解

系统成功将总功率分解为 5 类家电，输出每台设备的：

- 实时功率
- 开关状态
- 今日能耗（kWh）
- 能耗占比
- 置信度

### 7.3 可视化

Web 控制台正确展示了：

- 实时总功率曲线
- 家电分解曲线
- KPI 指标卡片
- 分项账单表格
- 模型评估雷达图

### 7.4 性能

- 单点推理延迟：约 4–10 ms（CPU）
- 批量分解（2 小时数据，stride=30）：约 1–2 秒
- 页面轮询周期：15 秒

---

## 八、问题与解决

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 登录失败 | 后端未启动或端口被占用 | 检查 `http://127.0.0.1:8000/health`，释放 8000 端口 |
| 无实时数据 | Replay Adapter 未运行 | 启动 `adapters/replay/cli.py` |
| 曲线不更新 | 未点击“刷新分解” | 手动触发或等待 15 秒自动轮询 |
| CMD 无法识别 `.venv/Scripts/uvicorn` | 使用了正斜杠 | 改用反斜杠 `.venv\Scripts\uvicorn` |

---

## 九、Demo 亮点

1. **端到端完整**：从模拟数据采集、存储、推理到可视化，链路完整。
2. **一键启动**：提供 CMD / Bash / PowerShell 三种一键脚本。
3. **模型可解释**：通过雷达图和分电能耗占比展示模型改进效果。
4. **可扩展**：预留 Modbus/MQTT 适配接口，便于接入真实电表。
5. **工程化**：Docker Compose、OpenAPI 文档、API 文档齐全。

---

## 十、后续工作

1. 使用真实 UK-DALE/REDD 数据集重新训练模型，提升指标。
2. 引入迁移学习，增强跨建筑泛化能力。
3. 接入真实 Modbus/MQTT 电表，进行现场部署测试。
4. 优化前端实时推送，引入 WebSocket 减少轮询开销。
5. 完善移动端页面与功能。

---

## 十一、结论

本 Demo 成功验证了建筑级 NILM 系统的核心功能：基于单点总功率数据，利用 Seq2Point + Attention 模型实现多电器负荷分解，并通过 Web 控制台直观展示实时功率、家电状态、能耗账单与模型评估指标。系统具备可运行、可演示、可扩展的特点，为后续真实数据训练与现场部署奠定了基础。
