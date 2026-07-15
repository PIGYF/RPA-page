import { useEffect, useState } from 'react';
import { AiEmployeePanel } from './components/AiEmployeePanel';
import { AiInsightPanel } from './components/AiInsightPanel';
import { ChatPanel } from './components/ChatPanel';
import { DailyBrief } from './components/DailyBrief';
import { FlowStatusPanel } from './components/FlowStatusPanel';
import { Header } from './components/Header';
import { KpiCard } from './components/KpiCard';
import { LiveActivityTimeline } from './components/LiveActivityTimeline';
import { LoadingScreen } from './components/LoadingScreen';
import { Modal } from './components/Modal';
import { OperationVolumeChart } from './components/OperationVolumeChart';
import { SummaryCard } from './components/SummaryCard';
import { getDashboardData, getFlowDetail, refreshDashboardData, sendChatCommand } from './services/dashboardService';
import type { ChatMessage, DateRange, DashboardView, FlowItem } from './types';

const DEFAULT_RANGE: DateRange = 7;

const formatMinute = (value: Date) =>
  new Intl.DateTimeFormat('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  }).format(value);

const createUserMessage = (text: string): ChatMessage => ({
  id: `user-${Date.now()}`,
  sender: 'user',
  text,
  timestamp: formatMinute(new Date())
});

function App() {
  const [range, setRange] = useState<DateRange>(DEFAULT_RANGE);
  const [dashboard, setDashboard] = useState<DashboardView | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [chatSending, setChatSending] = useState(false);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [selectedFlow, setSelectedFlow] = useState<FlowItem | null>(null);
  const [flowModalOpen, setFlowModalOpen] = useState(false);
  const [flowModalLoading, setFlowModalLoading] = useState(false);

  const loadDashboard = async (nextRange: DateRange, showLoader: boolean) => {
    if (showLoader) {
      setLoading(true);
    } else {
      setRefreshing(true);
    }

    try {
      const nextDashboard = showLoader
        ? await getDashboardData(nextRange)
        : await refreshDashboardData(nextRange);

      setDashboard(nextDashboard);
      setRange(nextRange);
      setCurrentTime(new Date());
      setMessages((previous) => (previous.length > 0 ? previous : nextDashboard.chatHistory));
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    void loadDashboard(DEFAULT_RANGE, true);
  }, []);

  useEffect(() => {
    if (!dashboard) {
      return undefined;
    }

    const intervalId = window.setInterval(() => {
      setCurrentTime(new Date());
      void loadDashboard(range, false);
    }, 60_000);

    return () => window.clearInterval(intervalId);
  }, [dashboard, range]);

  const handleRangeChange = (nextRange: DateRange) => {
    if (nextRange === range) {
      return;
    }

    void loadDashboard(nextRange, false);
  };

  const handleRefresh = () => {
    void loadDashboard(range, false);
  };

  const handleFlowOpen = async (flowId: string) => {
    setFlowModalOpen(true);
    setFlowModalLoading(true);
    setSelectedFlow(null);

    try {
      const detail = await getFlowDetail(flowId);
      setSelectedFlow(detail);
    } finally {
      setFlowModalLoading(false);
    }
  };

  const handleSendMessage = async (text: string) => {
    const trimmed = text.trim();

    if (!trimmed) {
      return;
    }

    setMessages((previous) => [...previous, createUserMessage(trimmed)]);
    setChatSending(true);

    try {
      const reply = await sendChatCommand(trimmed);
      setMessages((previous) => [...previous, reply]);
    } finally {
      setChatSending(false);
    }
  };

  const closeFlowModal = () => {
    setFlowModalOpen(false);
    setSelectedFlow(null);
    setFlowModalLoading(false);
  };

  if (loading || !dashboard) {
    return <LoadingScreen label="AI 员工正在装载 SAP 运营看板…" />;
  }

  return (
    <>
      <div className="dashboard-shell">
        <Header
          currentTime={currentTime}
          lastUpdated={dashboard.updatedAt}
          refreshing={refreshing}
          onRefresh={handleRefresh}
        />

        <main className="dashboard-grid">
          <section className="dashboard-main">
            <AiEmployeePanel employee={dashboard.employee} updatedAt={dashboard.updatedAt} />

            <div className="summary-grid">
              {dashboard.summaries.map((summary) => (
                <SummaryCard key={summary.id} summary={summary} />
              ))}
            </div>

            <div className="kpi-grid">
              {dashboard.kpis.map((kpi) => (
                <KpiCard key={kpi.id} kpi={kpi} />
              ))}
            </div>

            <OperationVolumeChart
              range={range}
              data={dashboard.volumes}
              onRangeChange={handleRangeChange}
            />

            <div className="dual-panel-grid">
              <FlowStatusPanel flows={dashboard.flows} onFlowClick={handleFlowOpen} />
              <AiInsightPanel insights={dashboard.insights} />
            </div>
          </section>

          <aside className="dashboard-sidebar">
            <DailyBrief brief={dashboard.brief} />
            <LiveActivityTimeline items={dashboard.timeline} />
            <ChatPanel
              messages={messages}
              quickCommands={dashboard.quickCommands}
              sending={chatSending}
              onSend={handleSendMessage}
            />
          </aside>
        </main>
      </div>

      <Modal
        title={selectedFlow?.name ?? '流程详情'}
        open={flowModalOpen}
        onClose={closeFlowModal}
      >
        {flowModalLoading ? (
          <div className="modal-loading-state">
            <div className="loading-pulse" />
            <p>正在读取流程指标与最新运行摘要…</p>
          </div>
        ) : selectedFlow ? (
          <div className="flow-detail">
            <div className="flow-detail-grid">
              <div className="flow-detail-card">
                <span>Owner</span>
                <strong>{selectedFlow.owner}</strong>
              </div>
              <div className="flow-detail-card">
                <span>Success Rate</span>
                <strong>{selectedFlow.successRate}%</strong>
              </div>
              <div className="flow-detail-card">
                <span>Average Handle Time</span>
                <strong>{selectedFlow.avgHandleTime}</strong>
              </div>
              <div className="flow-detail-card">
                <span>Last Run</span>
                <strong>{selectedFlow.lastRun}</strong>
              </div>
            </div>

            <div className="flow-detail-section">
              <h4>当前说明</h4>
              <p>{selectedFlow.description}</p>
            </div>

            <div className="flow-detail-section">
              <h4>关键步骤</h4>
              <div className="flow-steps">
                {selectedFlow.steps.map((step) => (
                  <div key={step.label} className="flow-step-chip">
                    <span>{step.label}</span>
                    <strong>{step.value}</strong>
                  </div>
                ))}
              </div>
            </div>

            <div className="flow-detail-section">
              <h4>AI 建议动作</h4>
              <p>{selectedFlow.nextAction}</p>
            </div>
          </div>
        ) : (
          <p className="empty-flow-state">未找到流程详情。</p>
        )}
      </Modal>
    </>
  );
}

export default App;
