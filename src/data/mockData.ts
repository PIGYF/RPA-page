import type {
  ChatMessage,
  DashboardRangeData,
  DashboardSeed,
  DateRange,
  FlowItem,
  OperationVolumePoint
} from '../types';

const createVolumes = (
  labels: string[],
  createdSeries: number[],
  completedSeries: number[],
  exceptionSeries: number[]
): OperationVolumePoint[] =>
  labels.map((label, index) => ({
    label,
    created: createdSeries[index],
    completed: completedSeries[index],
    exceptions: exceptionSeries[index]
  }));

const sevenDayVolumes = createVolumes(
  ['07/09', '07/10', '07/11', '07/12', '07/13', '07/14', '07/15'],
  [182, 194, 205, 211, 226, 233, 248],
  [176, 189, 198, 203, 219, 228, 241],
  [8, 10, 9, 11, 13, 12, 10]
);

const fourteenDayVolumes = createVolumes(
  ['07/02', '07/03', '07/04', '07/05', '07/06', '07/07', '07/08', '07/09', '07/10', '07/11', '07/12', '07/13', '07/14', '07/15'],
  [160, 166, 172, 176, 181, 188, 191, 198, 204, 212, 218, 227, 235, 246],
  [154, 160, 167, 171, 176, 182, 186, 193, 198, 205, 213, 220, 228, 239],
  [11, 10, 9, 8, 10, 9, 8, 9, 11, 10, 12, 11, 10, 9]
);

const thirtyDayVolumes = createVolumes(
  [
    '06/16',
    '06/17',
    '06/18',
    '06/19',
    '06/20',
    '06/21',
    '06/22',
    '06/23',
    '06/24',
    '06/25',
    '06/26',
    '06/27',
    '06/28',
    '06/29',
    '06/30',
    '07/01',
    '07/02',
    '07/03',
    '07/04',
    '07/05',
    '07/06',
    '07/07',
    '07/08',
    '07/09',
    '07/10',
    '07/11',
    '07/12',
    '07/13',
    '07/14',
    '07/15'
  ],
  [142, 146, 150, 154, 157, 160, 166, 169, 172, 176, 181, 185, 188, 190, 194, 198, 201, 205, 209, 214, 218, 223, 226, 232, 236, 241, 245, 249, 254, 260],
  [137, 141, 146, 149, 152, 156, 160, 164, 167, 171, 175, 178, 181, 184, 188, 191, 194, 198, 202, 206, 210, 216, 219, 224, 229, 234, 238, 242, 247, 252],
  [10, 11, 9, 10, 12, 10, 9, 8, 9, 10, 11, 10, 9, 8, 9, 8, 10, 9, 8, 10, 11, 12, 11, 10, 9, 10, 11, 12, 10, 9]
);

const flows: FlowItem[] = [
  {
    id: 'p2p-order',
    name: '采购订单创建',
    status: 'healthy',
    owner: 'AI Employee Alpha',
    successRate: 99.1,
    avgHandleTime: '2m 18s',
    queue: 8,
    description: '自动读取采购申请、校验供应商主数据，并写入 SAP ME21N 相关字段，当前处于稳定批量执行状态。',
    nextAction: '继续保持自动审批链路；若晚间批次超过 280 单，建议提前预热机器人实例。',
    steps: [
      { label: 'Input Validation', value: '100%' },
      { label: 'Vendor Match', value: '99.4%' },
      { label: 'SAP Post', value: '98.9%' }
    ],
    lastRun: '2026-07-15 10:21'
  },
  {
    id: 'vendor-master',
    name: '供应商主数据维护',
    status: 'warning',
    owner: 'AI Employee Beta',
    successRate: 95.8,
    avgHandleTime: '4m 02s',
    queue: 19,
    description: '自动比对新供应商资料与黑名单信息，近期 OCR 附件质量下降导致复核请求上升。',
    nextAction: '优先清理低清晰度营业执照附件，并将 OCR 阈值从 0.86 调整至 0.82 以缓解积压。',
    steps: [
      { label: 'Document OCR', value: '93.5%' },
      { label: 'Risk Check', value: '97.8%' },
      { label: 'Master Update', value: '96.1%' }
    ],
    lastRun: '2026-07-15 10:18'
  },
  {
    id: 'invoice-check',
    name: '应付发票校验',
    status: 'critical',
    owner: 'AI Employee Gamma',
    successRate: 91.7,
    avgHandleTime: '5m 44s',
    queue: 27,
    description: '三方匹配流程受到高峰期发票行项目膨胀影响，税码异常和 PO 历史价差触发了多次人工升级。',
    nextAction: '建议立即执行异常分流命令，优先处理税码 ZR1/ZR2 的差异发票，并安排人工复核高风险记录。',
    steps: [
      { label: 'PO Match', value: '92.8%' },
      { label: 'Tax Validation', value: '88.6%' },
      { label: 'Exception Routing', value: '94.3%' }
    ],
    lastRun: '2026-07-15 10:16'
  },
  {
    id: 'inventory-diff',
    name: '库存盘点差异处理',
    status: 'paused',
    owner: 'AI Employee Delta',
    successRate: 97.4,
    avgHandleTime: '3m 11s',
    queue: 6,
    description: '盘点差异补录流程因仓库班次切换暂时暂停，等待 11:00 新批次导入后自动恢复。',
    nextAction: '保持暂停状态；11:00 前确认仓库接口文件到达，再恢复机器人调度。',
    steps: [
      { label: 'File Intake', value: '100%' },
      { label: 'Variance Scan', value: '97.3%' },
      { label: 'Posting Prep', value: '96.9%' }
    ],
    lastRun: '2026-07-15 09:58'
  }
];

const initialChatHistory: ChatMessage[] = [
  {
    id: 'welcome-1',
    sender: 'assistant',
    text: '您好，我已接管 SAP 运营中心。可直接发送“检查发票异常”或点击快捷指令。',
    timestamp: '10:22'
  }
];

const rangeData: Record<DateRange, DashboardRangeData> = {
  7: {
    summaries: [
      {
        id: 'ops-handled',
        label: '自动处理单量',
        value: '1,499',
        change: '+8.2%',
        accent: '#2dd4bf',
        description: '近 7 天 AI 员工完成的 SAP 事务总量'
      },
      {
        id: 'sla',
        label: 'SLA 达成率',
        value: '98.6%',
        change: '+1.1%',
        accent: '#60a5fa',
        description: '核心流程在承诺时间内完成比例'
      },
      {
        id: 'manual-review',
        label: '待人工复核',
        value: '18',
        change: '-3',
        accent: '#f59e0b',
        description: '需要人工确认的高风险记录数量'
      },
      {
        id: 'hours-saved',
        label: '节省工时',
        value: '312h',
        change: '+26h',
        accent: '#a78bfa',
        description: '按当前自动化率折算的人力节省'
      }
    ],
    kpis: [
      {
        id: 'utilization',
        label: '机器人利用率',
        value: '84',
        unit: '%',
        trend: '+5.4%',
        trendLabel: '较上周',
        progress: 84,
        direction: 'up'
      },
      {
        id: 'automation-rate',
        label: '端到端自动化率',
        value: '76',
        unit: '%',
        trend: '+2.1%',
        trendLabel: '稳定提升',
        progress: 76,
        direction: 'up'
      },
      {
        id: 'closure-time',
        label: '异常闭环时长',
        value: '38',
        unit: 'm',
        trend: '-4m',
        trendLabel: '处理更快',
        progress: 63,
        direction: 'down'
      },
      {
        id: 'night-load',
        label: '晚高峰负载预测',
        value: '72',
        unit: '%',
        trend: '+6%',
        trendLabel: '18:00-20:00',
        progress: 72,
        direction: 'up'
      }
    ],
    volumes: sevenDayVolumes,
    insights: [
      {
        id: 'insight-7-1',
        title: '发票异常集中在税码校验',
        detail: '近 24 小时 61% 的例外发生在 ZR1/ZR2 税码映射，建议优先清理规则表。',
        confidence: 92,
        tag: 'Exception Hotspot',
        impact: '预计可减少 11 条人工复核'
      },
      {
        id: 'insight-7-2',
        title: '采购订单夜间批次可再扩容',
        detail: '19:00 后订单创建吞吐还有 18% 余量，可承接额外亚洲区域批次。',
        confidence: 88,
        tag: 'Capacity',
        impact: '可新增 40-55 单/小时'
      },
      {
        id: 'insight-7-3',
        title: '供应商 OCR 置信度下滑',
        detail: '供应商主数据流程 OCR 平均置信度降至 0.81，低于标准线 0.85。',
        confidence: 90,
        tag: 'Data Quality',
        impact: '建议本周修复扫描件来源'
      }
    ],
    brief: {
      headline: '今日 SAP 运营总体稳定，AI 员工已提前识别发票侧异常抬升。',
      sections: [
        {
          title: '吞吐表现',
          detail: '采购订单与库存差异处理吞吐持续抬升，近 7 日完成量较前一周期增长 8.2%。',
          emphasis: '高峰承载正常'
        },
        {
          title: '风险提示',
          detail: '应付发票税码校验仍是当前主要瓶颈，需关注 ZR1/ZR2 异常清理。',
          emphasis: '建议优先干预'
        },
        {
          title: '资源建议',
          detail: '若晚间发票量继续上涨，可临时将 1 个机器人从库存流程切换至 AP 例外分流。',
          emphasis: '单点调度即可'
        }
      ],
      recommendedActions: ['刷新应付发票异常队列', '输出税码差异清单', '确认 11:00 仓库接口恢复']
    }
  },
  14: {
    summaries: [
      {
        id: 'ops-handled',
        label: '自动处理单量',
        value: '3,011',
        change: '+12.5%',
        accent: '#2dd4bf',
        description: '近 14 天 AI 员工完成的 SAP 事务总量'
      },
      {
        id: 'sla',
        label: 'SLA 达成率',
        value: '98.1%',
        change: '+0.7%',
        accent: '#60a5fa',
        description: '核心流程在承诺时间内完成比例'
      },
      {
        id: 'manual-review',
        label: '待人工复核',
        value: '26',
        change: '-5',
        accent: '#f59e0b',
        description: '需要人工确认的高风险记录数量'
      },
      {
        id: 'hours-saved',
        label: '节省工时',
        value: '618h',
        change: '+58h',
        accent: '#a78bfa',
        description: '按当前自动化率折算的人力节省'
      }
    ],
    kpis: [
      {
        id: 'utilization',
        label: '机器人利用率',
        value: '81',
        unit: '%',
        trend: '+3.2%',
        trendLabel: '两周对比',
        progress: 81,
        direction: 'up'
      },
      {
        id: 'automation-rate',
        label: '端到端自动化率',
        value: '74',
        unit: '%',
        trend: '+1.6%',
        trendLabel: '连续提升',
        progress: 74,
        direction: 'up'
      },
      {
        id: 'closure-time',
        label: '异常闭环时长',
        value: '41',
        unit: 'm',
        trend: '-2m',
        trendLabel: '略有优化',
        progress: 59,
        direction: 'down'
      },
      {
        id: 'night-load',
        label: '晚高峰负载预测',
        value: '69',
        unit: '%',
        trend: '+4%',
        trendLabel: '趋势平稳',
        progress: 69,
        direction: 'up'
      }
    ],
    volumes: fourteenDayVolumes,
    insights: [
      {
        id: 'insight-14-1',
        title: '双周订单量抬升显著',
        detail: '采购订单创建在双周尺度上增长 12.5%，主要来自东南亚工厂补货需求。',
        confidence: 91,
        tag: 'Trend',
        impact: '建议锁定晚间资源'
      },
      {
        id: 'insight-14-2',
        title: '供应商主数据质量波动可控',
        detail: '尽管 OCR 质量下降，但风控环节保持 97% 以上稳定，未出现高风险放行。',
        confidence: 86,
        tag: 'Control',
        impact: '无需扩大人工审核'
      },
      {
        id: 'insight-14-3',
        title: '发票侧异常与 PO 历史价差关联',
        detail: 'AP 例外中 43% 可追溯至历史 PO 价格未同步更新，建议联动采购团队。',
        confidence: 89,
        tag: 'Root Cause',
        impact: '可减少重复异常'
      }
    ],
    brief: {
      headline: '近 14 天看板显示采购与 AP 压力同步走高，但整体 SLA 仍保持在安全区间。',
      sections: [
        {
          title: '整体趋势',
          detail: '订单与发票处理量同步增加，AI 员工池保持稳定吞吐，尚无系统性积压。',
          emphasis: '趋势向上'
        },
        {
          title: '需关注流程',
          detail: '应付发票校验连续两周高于其他流程的异常占比，需要专项治理税码与价差规则。',
          emphasis: '连续高风险'
        },
        {
          title: '协同建议',
          detail: '建议采购、财务共享与 RPA 团队在本周同步更新 PO 价格规则库。',
          emphasis: '跨团队联动'
        }
      ],
      recommendedActions: ['导出双周异常根因分析', '锁定 PO 历史价格差异记录', '更新 OCR 低置信度白名单']
    }
  },
  30: {
    summaries: [
      {
        id: 'ops-handled',
        label: '自动处理单量',
        value: '6,302',
        change: '+18.4%',
        accent: '#2dd4bf',
        description: '近 30 天 AI 员工完成的 SAP 事务总量'
      },
      {
        id: 'sla',
        label: 'SLA 达成率',
        value: '97.8%',
        change: '+0.5%',
        accent: '#60a5fa',
        description: '核心流程在承诺时间内完成比例'
      },
      {
        id: 'manual-review',
        label: '待人工复核',
        value: '33',
        change: '-7',
        accent: '#f59e0b',
        description: '需要人工确认的高风险记录数量'
      },
      {
        id: 'hours-saved',
        label: '节省工时',
        value: '1,284h',
        change: '+146h',
        accent: '#a78bfa',
        description: '按当前自动化率折算的人力节省'
      }
    ],
    kpis: [
      {
        id: 'utilization',
        label: '机器人利用率',
        value: '79',
        unit: '%',
        trend: '+6.8%',
        trendLabel: '月度表现',
        progress: 79,
        direction: 'up'
      },
      {
        id: 'automation-rate',
        label: '端到端自动化率',
        value: '73',
        unit: '%',
        trend: '+3.4%',
        trendLabel: '稳步提升',
        progress: 73,
        direction: 'up'
      },
      {
        id: 'closure-time',
        label: '异常闭环时长',
        value: '44',
        unit: 'm',
        trend: '-6m',
        trendLabel: '月度优化',
        progress: 55,
        direction: 'down'
      },
      {
        id: 'night-load',
        label: '晚高峰负载预测',
        value: '67',
        unit: '%',
        trend: '+5%',
        trendLabel: '仍有余量',
        progress: 67,
        direction: 'up'
      }
    ],
    volumes: thirtyDayVolumes,
    insights: [
      {
        id: 'insight-30-1',
        title: '月度自动化收益持续兑现',
        detail: '30 天累计节省工时已超过 1,280 小时，采购和财务共享中心收益最明显。',
        confidence: 94,
        tag: 'ROI',
        impact: '支持扩容更多流程'
      },
      {
        id: 'insight-30-2',
        title: 'AP 例外流程需要专项治理',
        detail: '尽管闭环时间缩短 6 分钟，但发票税码与 PO 价差仍反复出现，建议创建专项机器人队列。',
        confidence: 90,
        tag: 'Optimization',
        impact: '减少长期复发异常'
      },
      {
        id: 'insight-30-3',
        title: '库存盘点流程具备再自动化空间',
        detail: '盘点差异处理整体稳定，若打通仓库接口校验，可再减少 9% 人工介入。',
        confidence: 84,
        tag: 'Expansion',
        impact: '释放更多机器人时段'
      }
    ],
    brief: {
      headline: '月度运营显示 AI 员工已形成稳定收益曲线，下一阶段应聚焦发票异常专项治理。',
      sections: [
        {
          title: '收益回顾',
          detail: '本月累计处理 6,302 条 SAP 事务，节省工时 1,284 小时，运营中心自动化收益显著。',
          emphasis: 'ROI 持续提升'
        },
        {
          title: '瓶颈回顾',
          detail: 'AP 例外仍是影响月度 SLA 的主要原因，建议按税码、供应商、PO 差异三维拆分处理。',
          emphasis: '优先专项治理'
        },
        {
          title: '扩容建议',
          detail: '采购订单和库存差异流程具备扩容条件，可在下月接入更多工厂与仓库场景。',
          emphasis: '进入下一阶段'
        }
      ],
      recommendedActions: ['制定 AP 专项机器人编排', '评估库存接口自动校验', '准备月度管理层汇报']
    }
  }
};

export const dashboardSeed: DashboardSeed = {
  employee: {
    name: 'Ava-SAP Ops AI',
    role: 'AI Employee / SAP Operations Center',
    status: 'online',
    greeting: '我在离线模式下持续监控 SAP 关键运营流程。',
    description:
      '聚焦采购、供应商主数据、AP 发票与库存差异四类高频流程，提供吞吐监控、异常预警、智能建议与即时指令应答。',
    specialties: ['P2P 订单处理', '供应商主数据校验', '三方匹配异常分流', '库存差异回写'],
    queueFocus: '当前重点关注：应付发票异常队列',
    responseSla: 'AI 响应 SLA：≤ 30 秒'
  },
  ranges: rangeData,
  flows,
  timeline: [
    {
      id: 'timeline-1',
      time: '10:18',
      title: '发票异常分流规则被触发',
      description: 'Gamma 将 6 条税码异常转入人工复核池。',
      severity: 'warning',
      actor: 'AI Employee Gamma'
    },
    {
      id: 'timeline-2',
      time: '10:12',
      title: '采购订单批次完成',
      description: 'Alpha 完成东南亚工厂 48 条采购订单落账。',
      severity: 'success',
      actor: 'AI Employee Alpha'
    },
    {
      id: 'timeline-3',
      time: '10:05',
      title: 'OCR 置信度告警',
      description: '供应商营业执照扫描件低于阈值 0.82。',
      severity: 'warning',
      actor: 'AI Employee Beta'
    },
    {
      id: 'timeline-4',
      time: '09:58',
      title: '库存盘点流程暂停',
      description: '等待仓库新批次文件到达后恢复。',
      severity: 'info',
      actor: 'AI Employee Delta'
    },
    {
      id: 'timeline-5',
      time: '09:41',
      title: '月度 ROI 摘要已生成',
      description: 'AI 自动汇总 30 天节省工时与异常分布。',
      severity: 'success',
      actor: 'Ava-SAP Ops AI'
    }
  ],
  quickCommands: ['检查发票异常', '刷新采购订单状态', '生成今日运营简报', '预测晚高峰负载'],
  chatHistory: initialChatHistory
};

export const chatReplyMatchers: Array<{
  keywords: string[];
  reply: string;
}> = [
  {
    keywords: ['发票', '异常'],
    reply:
      '已聚焦应付发票异常：当前 27 条在队列中，其中 11 条与税码 ZR1/ZR2 相关，建议先执行差异清理。'
  },
  {
    keywords: ['采购订单', '订单'],
    reply:
      '采购订单流程运行稳定，最近一批 48 单已全部完成；预计晚间 19:00 前仍可额外承接约 40 单/小时。'
  },
  {
    keywords: ['简报', 'brief'],
    reply:
      '今日简报已准备完成：整体 SLA 98.6%，重点风险仍在 AP 税码校验，建议锁定人工复核优先级。'
  },
  {
    keywords: ['负载', '高峰'],
    reply:
      '根据当前趋势，18:00-20:00 负载预测约 72%，建议将 1 个备用机器人预留给 AP 例外分流。'
  }
];

export const findFlowById = (flowId: string): FlowItem | undefined =>
  dashboardSeed.flows.find((flow) => flow.id === flowId);
