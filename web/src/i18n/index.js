import { createI18n } from 'vue-i18n'

const messages = {
  zh: {
    // 0. 系统与顶栏导航 (Navbar)
    system: {
      title: 'NILM 智能负荷分解系统'
    },
    nav: {
      dashboard: '控制台',
      evaluation: '算法评估',
      analytics: '用电分析',
      team: '团队信息'
    },
    model: {
      baseline: '基础模型 ',
      proposed: '改进模型 '
    },

    // 1. Dashboard 顶部 KPI 卡片与实时图表
    kpi: {
      mainsPower: '总入户功率',
      activeAppliances: '当前激活家电',
      units: '台',
      f1Score: '平均 F1-Score (精准度)',
      mae: 'MAE (平均绝对误差)'
    },
    chart: {
      title: '实时总功率与家电分解曲线 ',
      sub: '599 Sliding Window · ONNX Runtime 毫秒级推理',
      liveTag: '实时数据推送中',
      yAxis: '功率',
      mains: '总功率 '
    },
    section: {
      fleet: '家电运行监控与负荷分解 '
    },

    // 2. 家电名称与通用字段
    appliances: {
      fridge: '智能冰箱',
      washingMachine: '滚筒洗衣机',
      washer: '滚筒洗衣机',
      kettle: '电热水壶',
      dishwasher: '洗碗机',
      microwave: '微波炉',
      confidence: '置信度',
      today: '今日'
    },

    // 3. 算法评估页 (Evaluation)
    evaluation: {
      radarTitle: 'Seq2Point 算法改进评估',
      ablationTitle: '模型性能对比 ',
      ablationDesc: '对比基础 Baseline 1D-CNN 与融合 Dilated Convolutions & Temporal Attention 改进模型在不同数据集上的 MAE 与 F1-Score 表现。'
    },
    
    //KpiCards
    kpi: {
        mainsPower: '总入户功率 ',
        activeAppliances: '当前激活家电',
        units: '台',
        f1Score: '平均 F1-Score (精准度)',
        mae: 'MAE (平均绝对误差)'
    },
    //TeamRoles:
    team: {
        drawerTitle: '项目架构与毕业设计分工',
        rolesTitle: '团队分工',
        sysTitle: '系统架构与参数',
        slidingWindow: '滑动窗口大小',
        inferenceEngine: '推理引擎',
        techStack: '技术栈',
        roles: {
            jin: {
                title: 'JinXinyi • 全栈与数据流水线负责人',
                desc: '负责 UK-DALE/REDD 数据清洗与滑动窗口切片；后端 API & 数据库设计；Vue 3 控制台全栈开发。'
            },
            yang: {
                title: 'YangYifei • AI 与算法负责人',
                desc: 'Seq2Point 1D-CNN 实现与 Dilated Conv + Attention 优化，PyTorch 转 ONNX 模型。'
            },
            yu: {
                title: 'YuShengbin • 移动端负责人',
                desc: '跨平台 Mobile 客户端 UI/UX 开发，实时功率推送与状态监控。'
            }
        }
    },

    // 4. 能耗账单与安全页 (Analytics)
    analytics: {
      billingTitle: '本月家电分项用电账单',
      estTotalCost: '预估总电费',
      totalUsage: '总用电量',
      colAppliance: '家电名称',
      colUsage: '用电量',
      colCost: '预估电费 (元)',
      colRatio: '占比',
      safetyConfig: '安全预警配置',
      powerLimitLabel: '入户总功率预警阈值',
      alertLogTitle: '告警日志记录',
      // 日志结构映射
      logs: {
        overload: {
          title: '总功率过载预警',
          msg: '实时总功率达到 {power}W，超过安全阈值 ({limit}W)'
        },
        dryRun: {
          title: '设备干烧/长时间运行',
          msg: '电热水壶持续高功率运行超过 15 分钟'
        }
      }
    }
  },

  en: {
    // 0. System & Header Navbar
    system: {
      title: 'NILM Smart Disaggregation System'
    },
    nav: {
      dashboard: 'Dashboard',
      evaluation: 'Evaluation',
      analytics: 'Analytics',
      team: 'Team'
    },
    model: {
      baseline: 'Baseline Model',
      proposed: 'Proposed Model'
    },

    // 1. Dashboard KPI Cards & Real-time Chart
    kpi: {
      mainsPower: 'Mains Power',
      activeAppliances: 'Active Appliances',
      units: 'Units',
      f1Score: 'Avg F1-Score (Precision)',
      mae: 'MAE (Mean Absolute Error)'
    },
    chart: {
      title: 'Real-time Disaggregation Stream',
      sub: '599 Sliding Window · ONNX Runtime Millisecond Inference',
      liveTag: 'Live Stream Active',
      yAxis: 'Power (Watts)',
      mains: 'Total Mains'
    },
    section: {
      fleet: 'Appliance Monitor Fleet'
    },

    // 2. Appliance Names & General Terms
    appliances: {
      fridge: 'Smart Refrigerator',
      washingMachine: 'Washing Machine',
      washer: 'Washing Machine',
      kettle: 'Electric Kettle',
      dishwasher: 'Dishwasher',
      microwave: 'Microwave',
      confidence: 'Confidence',
      today: 'Today'
    },

    // 3. Algorithm Evaluation Page
    evaluation: {
      radarTitle: 'Seq2Point Algorithm Improvement Evaluation',
      ablationTitle: 'Model Performance Comparison',
      ablationDesc: 'Comparing baseline 1D-CNN against the proposed Dilated Convolutions & Temporal Attention model in MAE and F1-Score metrics across datasets.'
    },


    //KpiCards
    kpi: {
        mainsPower: 'Mains Power',
        activeAppliances: 'Active Appliances',
        units: 'Units',
        f1Score: 'Avg F1-Score (Precision)',
        mae: 'MAE (Mean Absolute Error)'
    },




    //TeamRoles
    team: {
        drawerTitle: 'Project Architecture & Roles',
        rolesTitle: 'Team Roles',
        sysTitle: 'System Architecture & Specs',
        slidingWindow: 'Sliding Window Size',
        inferenceEngine: 'Inference Engine',
        techStack: 'Tech Stack',
        roles: {
            jin: {
                title: 'JinXinyi • Full-Stack & Data Pipeline Lead',
                desc: 'Responsible for UK-DALE/REDD data preprocessing & sliding window slicing; Backend API & DB design; Vue 3 dashboard development.'
            },
            yang: {
                title: 'YangYifei • AI & Algorithm Lead',
                desc: 'Seq2Point 1D-CNN implementation, Dilated Conv + Attention optimization, PyTorch to ONNX model export.'
            },
            yu: {
                title: 'YuShengbin • Mobile App Lead',
                desc: 'Cross-platform mobile UI/UX development, real-time power stream push & status monitoring.'
            }
        }
    },


    // 4. Analytics & Safety Settings Page
    analytics: {
      billingTitle: 'Monthly Appliance Energy Bill',
      estTotalCost: 'Est. Total Cost',
      totalUsage: 'Total Energy',
      colAppliance: 'Appliance',
      colUsage: 'Usage',
      colCost: 'Est.Cost',
      colRatio: 'Ratio',
      safetyConfig: 'Safety Alert Settings',
      powerLimitLabel: 'Mains Overload Threshold',
      alertLogTitle: 'Alert Logs',
      // Log Structure Mapping
      logs: {
        overload: {
          title: 'Mains Overload Alert',
          msg: 'Live total power reached {power}W, exceeding threshold ({limit}W)'
        },
        dryRun: {
          title: 'Long Run Alert',
          msg: 'Kettle operating at high power for over 15 mins'
        }
      }
    }
  }
}

const i18n = createI18n({
  legacy: false,
  locale: localStorage.getItem('lang') || 'zh',
  fallbackLocale: 'zh',
  messages
})

export default i18n