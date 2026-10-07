# NILM 系统演示指南

本指南面向答辩/展示场景，说明如何在一台 Windows 电脑上快速启动建筑级 NILM 系统的 Web Demo。

> **注意**：当前 Demo 默认使用**合成数据**（synthetic data），无需下载 UK-DALE 即可直接跑通端到端流程。真实数据集（UK-DALE/REDD）的切换方法见文末。

---

## 1. 演示环境

| 组件 | 版本/要求 |
|------|----------|
| 操作系统 | Windows 10/11（也支持 Linux/macOS，命令需自行调整） |
| Python | 3.10+ |
| Node.js | 16+ |
| 浏览器 | Chrome / Edge / Firefox |
| 网络 | 本地 `127.0.0.1`，无需联网 |

---

## 2. 一键启动（推荐）

### Windows CMD

双击或在 CMD 中执行：

```cmd
scripts\demo_web.cmd
```

会自动打开 3 个新窗口：
- **NILM Backend**：FastAPI 服务，端口 8000
- **NILM Replay**：实时数据推送模拟器
- **NILM Web**：Vue 前端开发服务器，端口 3000

然后访问 http://localhost:3000。

### Git Bash / WSL / macOS / Linux

```bash
bash scripts/demo_web.sh
```

### PowerShell

```powershell
.\scripts\demo_web.ps1
```

如果提示执行策略禁止，先运行：

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 3. 手动启动（排错用）

如果一键脚本有问题，可以分三个 CMD 窗口手动启动。

### 窗口 1：启动后端

```cmd
cd backend
.venv\Scripts\uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

确认后端正常：浏览器访问 http://127.0.0.1:8000/health，应返回：

```json
{"status":"ok"}
```

### 窗口 2：启动实时数据推送

```cmd
backend\.venv\Scripts\python -m adapters.replay.cli --meter-id 101 --speed 20
```

### 窗口 3：启动前端

```cmd
cd web
npm run dev
```

然后访问 http://localhost:3000。

---

## 4. 登录账号

| 字段 | 值 |
|------|-----|
| 用户名 | `admin` |
| 密码 | `admin123` |
| 默认建筑 | Building A |
| 默认电表 | Meter 101 |

登录后会跳转到 Dashboard。

---

## 5. 演示流程建议

按以下顺序展示，大约 5–8 分钟：

### 5.1 Dashboard（控制台）

- 顶部下拉框切换 **建筑 / 电表**
- 点击**刷新分解**，触发后端 `/disaggregation/run` 异步任务
- 观察 KPI 卡片：总入户功率、激活设备数、F1/MAE/SAE 指标
- 中间实时曲线：总功率 + 各家电分解曲线
- 底部家电网格：每台设备的实时功率、开关状态、置信度

### 5.2 Evaluation（算法评估）

- 左侧雷达图：Baseline vs Proposed（Dilated Conv + Attention）对比
- 右侧文字说明模型改进点
- 指标来自 `ml/checkpoints/ablation_metrics.json`

### 5.3 Analytics（用电分析）

- 分项用电账单：各家电 kWh、预估电费、占比进度条
- 安全预警配置：可调整功率阈值
- 告警日志：模拟过载等事件

---

## 6. 端口与依赖

| 服务 | 端口 | 说明 |
|------|------|------|
| FastAPI Backend | 8000 | 所有 API 入口 |
| Vite Web Dev | 3000 | 前端页面 |
| Replay Adapter | 无固定端口 | 通过 HTTP 推送数据到 backend |

如果端口被占用，结束旧进程：

```cmd
netstat -ano | findstr ":8000"
taskkill /PID <PID> /F
```

---

## 7. 常见问题

### Q1：浏览器显示“登录失败”

- 确认 backend 已启动：访问 http://127.0.0.1:8000/health
- 确认输入的是 `admin` / `admin123`
- 如果改了 backend 端口，同步修改 `web\vite.config.js` 里的 `proxy`

### Q2：Dashboard 没有实时数据

- 确认 replay 窗口在运行
- 点击“刷新分解”按钮
- 检查 backend 日志是否有 `/measurements/upload` 请求

### Q3：关闭窗口后端口还被占用

```cmd
netstat -ano | findstr ":8000"
taskkill /PID <PID> /F
```

### Q4：模型指标看起来不高

这是正常的，因为当前模型是用**合成数据**快速训练的（仅 2–3 个 epoch），用于演示系统流程。真实数据训练后指标会显著提升。

---

## 8. 切换到真实 UK-DALE 数据

如果想用真实公开数据集跑 demo，需要：

1. **下载 UK-DALE**（https://data.ukedc.rl.ac.uk/）并转为 HDF5 格式
2. **生成真实数据窗口**：
   ```bash
   cd ml
   .venv\Scripts\python -m preprocess.ukdale --path D:\UK-DALE\ukdale.h5 --building 1
   ```
3. **重新训练模型**：
   ```bash
   .venv\Scripts\python -m train.train_all --epochs 20
   .venv\Scripts\python -m export.export_onnx --all
   ```
4. **重新跑 demo**：
   ```cmd
   scripts\demo_web.cmd
   ```

---

## 9. 项目相关文件

| 文件 | 作用 |
|------|------|
| `scripts/demo_web.cmd` | Windows 一键 demo |
| `scripts/demo_web.sh` | Bash 一键 demo |
| `scripts/demo_web.ps1` | PowerShell 一键 demo |
| `web/vite.config.js` | 前端代理配置 |
| `backend/app/seed.py` | 默认建筑/电表/用户初始化 |
| `ml/checkpoints/` | 训练好的 ONNX 模型 |

---

## 10. 快捷命令总结

```cmd
:: 一键启动
scripts\demo_web.cmd

:: 登录
http://localhost:3000
admin / admin123

:: 检查后端
http://127.0.0.1:8000/health

:: 停止进程
netstat -ano | findstr ":8000"
taskkill /PID <PID> /F
```

---

祝答辩顺利！🎓
