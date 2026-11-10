import { createI18n } from 'vue-i18n'

const zh = {
  system: {
    title: 'NILM 智能负荷分解系统'
  },
  nav: {
    dashboard: '控制台',
    evaluation: '算法评估',
    analytics: '用电分析',
    team: '团队信息',
    logout: '退出登录'
  },
  model: {
    baseline: '基础模型',
    proposed: '改进模型'
  },
  dashboard: {
    building: '建筑',
    meter: '电表',
    refresh: '刷新分解',
    model: '模型版本',
    updated: '更新于'
  },
  status: {
    backend: {
      onnx: 'ONNX 推理',
      'torch-legacy': 'PyTorch 旧模型',
      heuristic: '启发式兜底',
      unknown: '未知'
    },
    degraded: '当前推理后端不是 ONNX（可能是启发式兜底），页面数值仅供流程演示。'
  },
  kpi: {
    mainsPower: '总入户功率',
    activeAppliances: '当前激活家电',
    units: '台',
    f1Score: '状态 F1',
    eventF1: '事件 F1',
    mae: 'MAE',
    latency: '推理耗时',
    liveMainsHint: '来自最近一条电表读数',
    activeHint: '最新一次分解结果',
    f1Hint: '测试集均值（越接近 100% 越好）',
    eventF1Hint: '按开关事件计分（更贴近实际使用）'
  },
  chart: {
    title: '实时总功率与家电分解曲线',
    sub: '599 点滑动窗口 · ONNX Runtime 推理',
    liveTag: '实时数据',
    yAxis: '功率 (W)',
    mains: '总功率',
    empty: '当前时段暂无数据，请启动 replay 适配器或点击刷新'
  },
  section: {
    fleet: '家电运行监控与负荷分解'
  },
  appliances: {
    fridge: '智能冰箱',
    washingMachine: '滚筒洗衣机',
    washer: '滚筒洗衣机',
    kettle: '电热水壶',
    dishwasher: '洗碗机',
    microwave: '微波炉',
    on: '运行中',
    off: '待机',
    confidence: '模型事件 F1',
    today: '时段电量',
    threshold: '开机阈值',
    empty: '暂无家电数据'
  },
  evaluation: {
    radarTitle: 'Seq2Point 模型评估',
    ablationTitle: '模型性能对比',
    ablationDesc:
      '所有指标均来自真实测试集评测结果（ml/checkpoints/ablation_metrics.json），不再使用占位分数。',
    tableTitle: '分电器测试集指标',
    appliance: '电器',
    model: '模型',
    mae: 'MAE (W)',
    sae: 'SAE',
    stateF1: '状态 F1',
    eventF1: '事件 F1',
    samples: '测试窗口数',
    noData: '尚未生成评测结果，请先运行训练与评估脚本',
    engine: '推理引擎',
    dataset: '数据集'
  },
  team: {
    drawerTitle: '项目架构与毕业设计分工',
    rolesTitle: '团队分工',
    sysTitle: '系统架构与参数',
    slidingWindow: '滑动窗口大小',
    inferenceEngine: '推理引擎',
    techStack: '技术栈',
    roles: {
      jin: {
        title: 'JinXinyi · 全栈与数据流水线',
        desc: 'UK-DALE 数据清洗与滑动窗口切片；FastAPI 后端与数据库；Vue 3 控制台。'
      },
      yang: {
        title: 'YangYifei · 算法',
        desc: 'Seq2Point 1D-CNN 实现与 Dilated Conv + Attention 优化，PyTorch 转 ONNX。'
      },
      yu: {
        title: 'YuShengbin · 移动端',
        desc: 'Uni-app 跨平台客户端，实时功率、分解结果与告警页面。'
      }
    }
  },
  analytics: {
    billingTitle: '分项用电与费用',
    estTotalCost: '预估电费',
    totalUsage: '总用电量',
    colAppliance: '家电名称',
    colUsage: '用电量',
    colCost: '预估电费 (元)',
    colRatio: '占比',
    safetyConfig: '安全预警配置',
    powerLimitLabel: '入户总功率预警阈值',
    alertLogTitle: '告警日志',
    window: '统计时段',
    tariff: '电价',
    unmetered: '未分解电量',
    estimated: '当前没有分解结果，仅统计总电量',
    resolve: '标记已处理',
    resolved: '已处理',
    emptyAlerts: '暂无告警',
    saved: '配置已保存',
    logs: {
      overload: {
        title: '总功率过载预警',
        msg: '实时总功率达到 {power}W，超过安全阈值 ({limit}W)'
      },
      system_ready: {
        title: '系统已就绪',
        msg: '真实数据集已预载，可启动 replay 适配器继续推送。'
      },
      dryRun: {
        title: '设备长时间运行',
        msg: '电热水壶持续高功率运行超过 15 分钟'
      }
    }
  },
  login: {
    title: 'Building NILM',
    subtitle: '建筑级非侵入式负荷监测',
    username: '用户名',
    password: '密码',
    submit: '登录',
    hint: '默认账号 admin / admin123',
    success: '登录成功',
    failed: '登录失败，请检查后端是否运行'
  },
  errors: {
    loadMeta: '加载建筑/电表失败',
    refresh: '刷新数据失败',
    task: '分解任务失败'
  }
}

const en = {
  system: { title: 'NILM Smart Disaggregation System' },
  nav: {
    dashboard: 'Dashboard',
    evaluation: 'Evaluation',
    analytics: 'Analytics',
    team: 'Team',
    logout: 'Log out'
  },
  model: { baseline: 'Baseline Model', proposed: 'Proposed Model' },
  dashboard: {
    building: 'Building',
    meter: 'Meter',
    refresh: 'Refresh',
    model: 'Model version',
    updated: 'Updated'
  },
  status: {
    backend: {
      onnx: 'ONNX runtime',
      'torch-legacy': 'Legacy PyTorch',
      heuristic: 'Heuristic fallback',
      unknown: 'Unknown'
    },
    degraded: 'The inference backend is not ONNX (heuristic fallback), numbers are for flow demo only.'
  },
  kpi: {
    mainsPower: 'Mains Power',
    activeAppliances: 'Active Appliances',
    units: 'units',
    f1Score: 'State F1',
    eventF1: 'Event F1',
    mae: 'MAE',
    latency: 'Inference',
    liveMainsHint: 'Latest meter reading',
    activeHint: 'From the latest disaggregation',
    f1Hint: 'Test-set average (higher is better)',
    eventF1Hint: 'Scored on ON/OFF events'
  },
  chart: {
    title: 'Real-time Disaggregation Stream',
    sub: '599-point window · ONNX Runtime',
    liveTag: 'Live',
    yAxis: 'Power (W)',
    mains: 'Total Mains',
    empty: 'No data in this window. Start the replay adapter or click refresh.'
  },
  section: { fleet: 'Appliance Monitor Fleet' },
  appliances: {
    fridge: 'Smart Refrigerator',
    washingMachine: 'Washing Machine',
    washer: 'Washing Machine',
    kettle: 'Electric Kettle',
    dishwasher: 'Dishwasher',
    microwave: 'Microwave',
    on: 'ON',
    off: 'OFF',
    confidence: 'Event F1',
    today: 'Energy',
    threshold: 'ON threshold',
    empty: 'No appliance data'
  },
  evaluation: {
    radarTitle: 'Seq2Point Evaluation',
    ablationTitle: 'Model Comparison',
    ablationDesc:
      'All numbers come from the real test split (ml/checkpoints/ablation_metrics.json); placeholder scores were removed.',
    tableTitle: 'Per-appliance test metrics',
    appliance: 'Appliance',
    model: 'Model',
    mae: 'MAE (W)',
    sae: 'SAE',
    stateF1: 'State F1',
    eventF1: 'Event F1',
    samples: 'Test windows',
    noData: 'No evaluation yet. Run training and evaluation first.',
    engine: 'Engine',
    dataset: 'Dataset'
  },
  team: {
    drawerTitle: 'Architecture & Roles',
    rolesTitle: 'Team Roles',
    sysTitle: 'System Specs',
    slidingWindow: 'Sliding window',
    inferenceEngine: 'Inference engine',
    techStack: 'Tech stack',
    roles: {
      jin: {
        title: 'JinXinyi · Full-stack & data pipeline',
        desc: 'UK-DALE preprocessing and windowing; FastAPI backend and database; Vue 3 console.'
      },
      yang: {
        title: 'YangYifei · Algorithms',
        desc: 'Seq2Point 1D-CNN, dilated conv + attention, PyTorch to ONNX export.'
      },
      yu: {
        title: 'YuShengbin · Mobile',
        desc: 'Uni-app client for live power, disaggregation and alerts.'
      }
    }
  },
  analytics: {
    billingTitle: 'Energy Breakdown & Cost',
    estTotalCost: 'Estimated cost',
    totalUsage: 'Total energy',
    colAppliance: 'Appliance',
    colUsage: 'Usage',
    colCost: 'Cost (CNY)',
    colRatio: 'Ratio',
    safetyConfig: 'Safety Settings',
    powerLimitLabel: 'Mains overload threshold',
    alertLogTitle: 'Alert Log',
    window: 'Window',
    tariff: 'Tariff',
    unmetered: 'Unmetered energy',
    estimated: 'No disaggregation result yet; total energy only.',
    resolve: 'Resolve',
    resolved: 'Resolved',
    emptyAlerts: 'No alerts',
    saved: 'Settings saved',
    logs: {
      overload: {
        title: 'Mains Overload Alert',
        msg: 'Live total power reached {power}W, exceeding threshold ({limit}W)'
      },
      system_ready: {
        title: 'System Ready',
        msg: 'A real dataset has been preloaded. Start the replay adapter to continue.'
      },
      dryRun: {
        title: 'Long Run Alert',
        msg: 'Kettle operating at high power for over 15 min'
      }
    }
  },
  login: {
    title: 'Building NILM',
    subtitle: 'Non-Intrusive Load Monitoring',
    username: 'Username',
    password: 'Password',
    submit: 'Sign in',
    hint: 'Default account admin / admin123',
    success: 'Signed in',
    failed: 'Sign-in failed. Is the backend running?'
  },
  errors: {
    loadMeta: 'Failed to load buildings / meters',
    refresh: 'Failed to refresh data',
    task: 'Disaggregation task failed'
  }
}

const i18n = createI18n({
  legacy: false,
  locale: localStorage.getItem('lang') || 'zh',
  fallbackLocale: 'zh',
  messages: { zh, en }
})

export default i18n
