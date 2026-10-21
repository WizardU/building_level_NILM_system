# NILM Uni-app Mobile Client

建筑级 NILM 系统的跨平台移动端 Demo，使用 Uni-app + Vue 3 开发，可编译为 H5 / 微信小程序 / Android / iOS。

## 功能

- JWT 登录（默认 `admin` / `admin123`）
- 建筑 / 电表切换
- 实时监测：总功率、激活设备数、F1-Score、MAE
- 实时功率曲线（总功率 + 各家电分解曲线）
- 家电运行状态与置信度
- 手动触发负荷分解任务
- 用电分析：分项账单、告警日志
- 功率预警阈值设置、语言切换、退出登录

## 技术栈

- Uni-app Vue 3
- Vite (`@dcloudio/vite-plugin-uni`)
- uCharts (`@qiun/uni-ucharts`) 绘制图表
- 复用后端 FastAPI RESTful API

## 快速开始

### 1. 安装依赖

```bash
cd mobile
npm install
```

### 2. 配置后端地址

编辑 `src/utils/config.js`：

```js
// 本地浏览器/模拟器预览
export const API_BASE = 'http://127.0.0.1:8000/api/v1'

// 真机同局域网预览时，改成运行后端电脑的局域网 IP
// export const API_BASE = 'http://192.168.1.xxx:8000/api/v1'
```

### 3. 启动后端

参考项目根目录 `DEMO.md`，或使用一键脚本：

```bash
# 项目根目录
bash scripts/demo_web.sh
```

然后保持后端和 replay 适配器运行。

### 4. 启动移动端 H5 预览

```bash
cd mobile
npm run dev:h5
```

打开控制台输出的地址（默认 `http://localhost:3100`）。

## 一键启动 Mobile Demo（后端 + 移动端）

```bash
# Windows CMD
scripts\demo_mobile.cmd

# PowerShell
.\scripts\demo_mobile.ps1

# Git Bash / WSL / macOS / Linux
bash scripts/demo_mobile.sh
```

脚本会自动：
1. 检查并生成合成数据与 ONNX 模型（如不存在）。
2. 启动 FastAPI 后端（端口 8000）。
3. 启动 replay 适配器推送实时数据。
4. 安装移动端依赖并启动 H5 开发服务器（端口 3100）。

## 常用命令

```bash
# H5 开发
npm run dev:h5

# 构建 H5
npm run build:h5

# 微信小程序
npm run dev:mp-weixin

# App（需要 HBuilderX 或 CLI 配置）
npm run dev:app
```

## 目录说明

```
mobile/
├── scripts/
│   └── postinstall.js   # 安装后复制 u-charts 所需文件
├── src/
│   ├── components/      # 可复用组件
│   │   ├── AlertBanner.vue
│   │   ├── ApplianceItem.vue
│   │   ├── BuildingPicker.vue
│   │   ├── KpiCard.vue
│   │   └── PowerChart.vue
│   ├── pages/           # 页面
│   │   ├── login/
│   │   ├── home/        # 实时监测 Dashboard
│   │   ├── appliances/  # 电器分解
│   │   ├── analytics/   # 用电分析
│   │   └── profile/     # 我的
│   ├── utils/           # 工具与 API
│   │   ├── api.js       # 后端接口封装
│   │   ├── chart.js     # 图表数据转换
│   │   ├── config.js    # 全局配置
│   │   └── store.js     # 本地状态
│   ├── App.vue
│   ├── main.js
│   ├── manifest.json
│   └── pages.json
├── index.html
├── package.json
├── package-lock.json
└── vite.config.js
```

## 真机调试提示

1. 确保手机和电脑在同一 Wi-Fi。
2. 修改 `src/utils/config.js` 中的 `API_BASE` 为电脑局域网 IP。
3. 启动时脚本会尝试打印局域网地址，例如 `http://192.168.1.xxx:3100`。
4. 在 H5 模式下用浏览器访问该地址即可。

## 注意

- 当前 Demo 默认使用合成数据，模型指标仅用于演示流程。
- 若后端端口不是 8000，请同步修改 `src/utils/config.js` 与 `src/manifest.json` 中相关配置。
