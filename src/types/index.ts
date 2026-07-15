export type DateRange = 7 | 14 | 30;

export type FlowStatus = 'healthy' | 'warning' | 'critical' | 'paused';
export type EmployeeStatus = 'online' | 'busy' | 'maintenance';
export type ActivitySeverity = 'success' | 'info' | 'warning' | 'critical';
export type TrendDirection = 'up' | 'down' | 'flat';
export type ChatSender = 'user' | 'assistant';
export type StatusTone = FlowStatus | EmployeeStatus | ActivitySeverity;

export interface AiEmployeeProfile {
  name: string;
  role: string;
  status: EmployeeStatus;
  greeting: string;
  description: string;
  specialties: string[];
  queueFocus: string;
  responseSla: string;
}

export interface SummaryMetric {
  id: string;
  label: string;
  value: string;
  change: string;
  accent: string;
  description: string;
}

export interface KpiMetric {
  id: string;
  label: string;
  value: string;
  unit?: string;
  trend: string;
  trendLabel: string;
  progress: number;
  direction: TrendDirection;
}

export interface OperationVolumePoint {
  label: string;
  created: number;
  completed: number;
  exceptions: number;
}

export interface FlowStep {
  label: string;
  value: string;
}

export interface FlowItem {
  id: string;
  name: string;
  status: FlowStatus;
  owner: string;
  successRate: number;
  avgHandleTime: string;
  queue: number;
  description: string;
  nextAction: string;
  steps: FlowStep[];
  lastRun: string;
}

export interface Insight {
  id: string;
  title: string;
  detail: string;
  confidence: number;
  tag: string;
  impact: string;
}

export interface TimelineItem {
  id: string;
  time: string;
  title: string;
  description: string;
  severity: ActivitySeverity;
  actor: string;
}

export interface DailyBriefSection {
  title: string;
  detail: string;
  emphasis: string;
}

export interface DailyBriefData {
  headline: string;
  sections: DailyBriefSection[];
  recommendedActions: string[];
}

export interface ChatMessage {
  id: string;
  sender: ChatSender;
  text: string;
  timestamp: string;
}

export interface DashboardRangeData {
  summaries: SummaryMetric[];
  kpis: KpiMetric[];
  volumes: OperationVolumePoint[];
  insights: Insight[];
  brief: DailyBriefData;
}

export interface DashboardSeed {
  employee: AiEmployeeProfile;
  ranges: Record<DateRange, DashboardRangeData>;
  flows: FlowItem[];
  timeline: TimelineItem[];
  quickCommands: string[];
  chatHistory: ChatMessage[];
}

export interface DashboardView extends DashboardRangeData {
  range: DateRange;
  employee: AiEmployeeProfile;
  flows: FlowItem[];
  timeline: TimelineItem[];
  quickCommands: string[];
  chatHistory: ChatMessage[];
  updatedAt: string;
}
