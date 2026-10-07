# NILM 后端 API 文档

本文档描述建筑级 NILM 系统后端提供的 REST API，主要面向前端开发者和集成测试人员。

- **Base URL**: `http://127.0.0.1:8000/api/v1`
- **协议**: HTTP（本地开发）/ HTTPS（生产部署）
- **内容类型**: `application/json`
- **认证**: JWT Bearer Token

---

## 认证方式

除 `/auth/login` 外，所有接口需要在请求头携带：

```http
Authorization: Bearer <access_token>
```

JWT 通过 `/auth/login` 获取，默认 60 分钟有效。

---

## 通用响应格式

```json
{
  "code": 200,
  "message": "success",
  "data": { ... },
  "timestamp": "2026-10-07T10:00:00Z"
}
```

错误时 `code` 会返回对应业务码，`message` 描述错误原因。

---

## 1. 认证 (Auth)

### POST /auth/login

用户登录，返回 JWT。

**请求体**:

```json
{
  "username": "admin",
  "password": "admin123"
}
```

**响应**:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "expires_in": 3600,
  "user": {
    "id": 1,
    "username": "admin",
    "role": "system_admin",
    "building_ids": [1]
  }
}
```

---

### POST /auth/logout

登出（当前为无状态实现，仅做校验）。

**请求头**: `Authorization: Bearer <token>`

**响应**:

```json
{ "logged_out": true }
```

---

### POST /auth/refresh

用 refresh_token 换取新的 access_token。

**请求体**:

```json
{
  "refresh_token": "<refresh_token>"
}
```

**响应**: 同 `/auth/login`

---

### GET /auth/me

获取当前登录用户信息。

**响应**:

```json
{
  "id": 1,
  "username": "admin",
  "role": "system_admin",
  "building_ids": [1]
}
```

---

## 2. 建筑 (Buildings)

### GET /buildings

列出所有建筑。

**查询参数**:

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| page | int | 1 | 页码 |
| size | int | 20 | 每页数量 |

**响应**:

```json
{
  "total": 1,
  "items": [
    {
      "id": 1,
      "name": "Building A",
      "address": "Demo Campus No.1",
      "floors_count": 1,
      "meters_count": 1,
      "total_power_kw": 0.078,
      "status": "online"
    }
  ]
}
```

---

### POST /buildings

创建建筑。

**请求体**:

```json
{
  "name": "Building B",
  "address": "Demo Campus No.2",
  "floors_count": 2
}
```

**响应**: 返回创建后的建筑对象。

---

### GET /buildings/{building_id}

获取单个建筑详情。

---

### PUT /buildings/{building_id}

更新建筑信息。

**请求体**: 同 `POST /buildings`

---

### DELETE /buildings/{building_id}

删除建筑。

**响应**:

```json
{ "deleted": 1 }
```

---

### GET /buildings/{building_id}/floors

列出某建筑下的所有楼层。

**响应**:

```json
{
  "total": 1,
  "items": [
    {
      "id": 1,
      "building_id": 1,
      "floor_number": 1,
      "name": "Floor 1",
      "zones_count": 1
    }
  ]
}
```

---

### POST /buildings/{building_id}/floors

创建楼层。

**请求体**:

```json
{
  "floor_number": 2,
  "name": "Floor 2"
}
```

---

### GET /floors/{floor_id}/zones

列出某楼层下的所有区域。

---

### POST /floors/{floor_id}/zones

创建区域。

**请求体**:

```json
{
  "name": "Office Zone B",
  "type": "office"
}
```

---

## 3. 电表 (Meters)

### GET /meters

按建筑列出电表。

**查询参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| building_id | int | 建筑 ID |
| page | int | 页码 |
| size | int | 每页数量 |

**响应**:

```json
{
  "total": 1,
  "items": [
    {
      "id": 101,
      "name": "Building A - Floor 1 Main Meter",
      "type": "three_phase",
      "location": {
        "building_id": 1,
        "floor_id": 1,
        "zone_id": 1
      },
      "sampling_rate_hz": 1,
      "protocol": "http",
      "status": "online",
      "last_seen": "2026-10-07T10:00:00Z",
      "current": {
        "phase_a": { "voltage": 220, "current": 0.5, "power_kw": 0.11 },
        "phase_b": { "voltage": 220, "current": 0, "power_kw": 0 },
        "phase_c": { "voltage": 220, "current": 0, "power_kw": 0 },
        "total_power_kw": 0.11
      }
    }
  ]
}
```

---

### POST /meters

创建电表。

**请求体**:

```json
{
  "name": "Meter 102",
  "type": "three_phase",
  "location": {
    "building_id": 1,
    "floor_id": 1,
    "zone_id": 1
  },
  "sampling_rate_hz": 1,
  "protocol": "http"
}
```

---

### GET /meters/{meter_id}

获取电表详情。

---

### GET /meters/{meter_id}/current

获取电表当前读数。

---

## 4. 测量数据 (Measurements)

### GET /measurements/realtime

获取电表最新实时数据。

**查询参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| meter_id | int | 电表 ID |

**响应**:

```json
{
  "meter_id": 101,
  "timestamp": "2026-10-07T10:00:00Z",
  "total_power_kw": 0.192,
  "phase_a": {
    "voltage": 220,
    "current": 0.876,
    "power_kw": 0.192
  }
}
```

---

### GET /measurements/history

查询历史测量数据。

**查询参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| meter_id | int | 电表 ID |
| start | datetime | 开始时间（ISO 8601） |
| end | datetime | 结束时间（ISO 8601） |
| page | int | 页码，默认 1 |
| size | int | 每页数量，默认 1000 |

**响应**:

```json
{
  "total": 1800,
  "items": [
    {
      "timestamp": "2026-10-07T09:00:00Z",
      "phase_a": { "voltage": 220, "current": 0.5, "power_kw": 0.11 },
      "phase_b": { "voltage": 220, "current": 0, "power_kw": 0 },
      "phase_c": { "voltage": 220, "current": 0, "power_kw": 0 }
    }
  ]
}
```

---

### POST /measurements/upload

批量上传测量数据，同时会触发简单的事件检测和过载告警。

**请求体**:

```json
{
  "meter_id": 101,
  "edge_node_id": "edge-001",
  "samples": [
    {
      "timestamp": "2026-10-07T10:00:00Z",
      "power_w": 192.5,
      "phase_a": { "voltage": 220, "current": 0.876, "power_kw": 0.193 }
    }
  ]
}
```

**响应**:

```json
{ "uploaded": 1 }
```

---

## 5. 事件 (Events)

### GET /events

列出电表事件（ON/OFF/state_change）。

**查询参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| meter_id | int | 电表 ID |
| start | datetime | 开始时间 |
| end | datetime | 结束时间 |
| page | int | 页码 |
| size | int | 每页数量 |

---

### POST /events

手动创建事件。

**请求体**:

```json
{
  "meter_id": 101,
  "timestamp": "2026-10-07T10:00:00Z",
  "type": "on",
  "phase": "a",
  "delta_power_kw": 1.8,
  "appliance_guess": "kettle",
  "confidence": 0.85
}
```

---

## 6. 家电 (Appliances)

### GET /appliances

按电表列出家电清单。

**查询参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| meter_id | int | 电表 ID |

---

### POST /appliances

为电表添加家电。

**请求体**:

```json
{
  "name": "智能冰箱",
  "type": "fridge",
  "meter_id": 101,
  "zone_id": 1,
  "rated_power_kw": 0.15
}
```

---

### GET /appliances/{appliance_id}

获取家电详情。

---

## 7. 负荷分解 (Disaggregation)

### GET /disaggregation/overview

获取 Dashboard KPI 数据。

**查询参数**:

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| meter_id | int | 101 | 电表 ID |

**响应**:

```json
{
  "mainsPower": 192.7,
  "activeDevices": 1,
  "totalDevices": 5,
  "f1Score": 0.85,
  "maeScore": 12.5,
  "saeScore": 0.05,
  "latency": 4.2,
  "meter_id": 101
}
```

---

### POST /disaggregation/run

提交一个分解任务（异步）。

**请求体**:

```json
{
  "meter_id": 101,
  "start": "2026-10-07T08:00:00Z",
  "end": "2026-10-07T10:00:00Z"
}
```

**响应**:

```json
{
  "task_id": "task-a1b2c3d4e5f6"
}
```

---

### GET /disaggregation/status/{task_id}

查询任务状态。

**响应**:

```json
{
  "task_id": "task-a1b2c3d4e5f6",
  "status": "completed",
  "progress": 100,
  "message": ""
}
```

状态可能为：`pending` / `running` / `completed` / `failed`

---

### GET /disaggregation/result

获取分解结果（同步，如果已有缓存直接返回）。

**查询参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| meter_id | int | 电表 ID |
| start | datetime | 开始时间 |
| end | datetime | 结束时间 |
| appliance_types | string | 可选，逗号分隔过滤，如 `fridge,kettle` |

**响应**:

```json
{
  "meter_id": 101,
  "period": "2026-10-07",
  "total_energy_kwh": 0.32,
  "appliances": [
    {
      "appliance_id": 201,
      "type": "fridge",
      "name": "智能冰箱",
      "energy_kwh": 0.05,
      "percentage": 16.0,
      "runtime_hours": 0.5,
      "series": [
        { "timestamp": "2026-10-07T08:00:00Z", "power_kw": 0.12 }
      ],
      "power_w": 120.0,
      "state": true,
      "confidence": 0.94
    }
  ],
  "mains_series": [
    { "timestamp": "2026-10-07T08:00:00Z", "power_kw": 0.192 }
  ]
}
```

---

## 8. 分析 (Analytics)

### GET /analytics/overview

获取建筑概览数据。

**查询参数**:

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| building_id | int | 1 | 建筑 ID |

**响应**:

```json
{
  "building_id": 1,
  "timestamp": "2026-10-07T10:00:00Z",
  "total_power_kw": 0.192,
  "today_energy_kwh": 2.3,
  "month_energy_kwh": 69.1,
  "active_appliances": 5,
  "floors": [
    { "floor_id": 1, "power_kw": 0.192, "energy_kwh": 1.54 }
  ],
  "top_appliances": [
    { "appliance_id": 201, "name": "智能冰箱", "power_kw": 0.15 }
  ]
}
```

---

### GET /analytics/energy

获取分项用电账单。

**查询参数**:

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| building_id | int | 1 | 建筑 ID |
| meter_id | int | 101 | 电表 ID |

**响应**:

```json
{
  "totalCost": 0.19,
  "totalKWh": 0.32,
  "breakdown": [
    {
      "key": "fridge",
      "name": "智能冰箱",
      "kWh": 0.05,
      "cost": 0.03,
      "ratio": 16.0
    }
  ]
}
```

---

### GET /analytics/alerts

获取告警列表。

**查询参数**:

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| building_id | int | 1 | 建筑 ID |

**响应**:

```json
{
  "total": 2,
  "items": [
    {
      "id": 1,
      "key": "overload",
      "type": "danger",
      "title": "总功率过载预警",
      "message": "实时总功率达到 3100W，超过安全阈值 (3000W)",
      "time": "10:05:30",
      "status": "未处理"
    }
  ]
}
```

---

### GET /analytics/reports

获取模型评估雷达图数据。

**响应**:

```json
{
  "indicators": [
    { "name": "F1-Score", "max": 100 },
    { "name": "MAE Error", "max": 100 },
    { "name": "SAE Billing Error", "max": 100 },
    { "name": "Inference Speed", "max": 100 },
    { "name": "Generalization", "max": 100 }
  ],
  "series": [
    { "key": "baseline", "value": [75, 60, 65, 80, 70] },
    { "key": "proposed", "value": [95, 90, 92, 88, 94] }
  ],
  "ablation_csv": "C:/.../ml/checkpoints/ablation_metrics.csv"
}
```

---

## 9. 健康检查

### GET /health

无需认证，用于服务探活。

**响应**:

```json
{ "status": "ok" }
```

---

## 10. 前端代理配置

本地开发时，前端 `web/vite.config.js` 已配置代理：

```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true
    }
  }
}
```

因此前端代码中 axios 的 `baseURL` 设为 `/api/v1` 即可。

---

## 11. 快速测试命令

```bash
# 登录获取 token
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 列出建筑（将 <token> 替换为实际 access_token）
curl -H "Authorization: Bearer <token>" \
  http://127.0.0.1:8000/api/v1/buildings

# 获取分解结果
curl -H "Authorization: Bearer <token>" \
  "http://127.0.0.1:8000/api/v1/disaggregation/result?meter_id=101&start=2026-10-07T08:00:00Z&end=2026-10-07T10:00:00Z"
```

---

## 12. 相关文件

| 文件 | 说明 |
|------|------|
| `openapi/NILM.json` | 完整 OpenAPI 3.0 规范 |
| `backend/app/routers/` | 各模块路由实现 |
| `backend/app/schemas.py` | Pydantic 请求/响应模型 |
| `backend/app/models.py` | SQLAlchemy 数据库模型 |
