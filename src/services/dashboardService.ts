import { chatReplyMatchers, dashboardSeed, findFlowById } from '../data/mockData';
import type { ChatMessage, DashboardView, DateRange, FlowItem } from '../types';

const delay = (ms: number) =>
  new Promise<void>((resolve) => {
    window.setTimeout(resolve, ms);
  });

const timeFormatter = new Intl.DateTimeFormat('zh-CN', {
  year: 'numeric',
  month: '2-digit',
  day: '2-digit',
  hour: '2-digit',
  minute: '2-digit'
});

const minuteFormatter = new Intl.DateTimeFormat('zh-CN', {
  hour: '2-digit',
  minute: '2-digit'
});

const cloneFlow = (flow: FlowItem): FlowItem => ({
  ...flow,
  steps: flow.steps.map((step) => ({ ...step }))
});

const buildDashboardView = (range: DateRange): DashboardView => {
  const rangeSnapshot = dashboardSeed.ranges[range];

  return {
    range,
    employee: { ...dashboardSeed.employee, specialties: [...dashboardSeed.employee.specialties] },
    summaries: rangeSnapshot.summaries.map((summary) => ({ ...summary })),
    kpis: rangeSnapshot.kpis.map((kpi) => ({ ...kpi })),
    volumes: rangeSnapshot.volumes.map((point) => ({ ...point })),
    insights: rangeSnapshot.insights.map((insight) => ({ ...insight })),
    brief: {
      headline: rangeSnapshot.brief.headline,
      sections: rangeSnapshot.brief.sections.map((section) => ({ ...section })),
      recommendedActions: [...rangeSnapshot.brief.recommendedActions]
    },
    flows: dashboardSeed.flows.map(cloneFlow),
    timeline: dashboardSeed.timeline.map((item) => ({ ...item })),
    quickCommands: [...dashboardSeed.quickCommands],
    chatHistory: dashboardSeed.chatHistory.map((message) => ({ ...message })),
    updatedAt: timeFormatter.format(new Date())
  };
};

const resolveReply = (command: string): string => {
  const normalized = command.toLowerCase();
  const matchedReply = chatReplyMatchers.find((matcher) =>
    matcher.keywords.every((keyword) => normalized.includes(keyword.toLowerCase()))
  );

  if (matchedReply) {
    return matchedReply.reply;
  }

  return '指令已接收。当前为离线演示模式，我会基于现有 Mock 数据继续给出建议与下一步动作。';
};

export async function getDashboardData(range: DateRange): Promise<DashboardView> {
  await delay(1100);
  return buildDashboardView(range);
}

export async function refreshDashboardData(range: DateRange): Promise<DashboardView> {
  await delay(450);
  return buildDashboardView(range);
}

export async function getFlowDetail(flowId: string): Promise<FlowItem> {
  await delay(280);

  const flow = findFlowById(flowId);

  if (!flow) {
    throw new Error(`Flow "${flowId}" not found`);
  }

  return cloneFlow(flow);
}

export async function sendChatCommand(command: string): Promise<ChatMessage> {
  await delay(650);

  return {
    id: `assistant-${Date.now()}`,
    sender: 'assistant',
    text: resolveReply(command),
    timestamp: minuteFormatter.format(new Date())
  };
}
