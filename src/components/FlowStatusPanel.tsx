import type { FC } from 'react';
import type { FlowItem } from '../types';
import { FlowStatusCard } from './FlowStatusCard';

interface FlowStatusPanelProps {
  flows: FlowItem[];
  onFlowClick: (flowId: string) => void;
}

export const FlowStatusPanel: FC<FlowStatusPanelProps> = ({ flows, onFlowClick }) => {
  const healthyCount = flows.filter((flow) => flow.status === 'healthy').length;
  const attentionCount = flows.filter((flow) => flow.status === 'warning' || flow.status === 'critical').length;

  return (
    <section className="flow-panel card">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Flow Status</p>
          <h3>流程运行状态</h3>
        </div>

        <div className="flow-summary-inline">
          <span>{healthyCount} 条稳定</span>
          <span>{attentionCount} 条需关注</span>
        </div>
      </div>

      <div className="flow-list">
        {flows.map((flow) => (
          <FlowStatusCard key={flow.id} flow={flow} onClick={onFlowClick} />
        ))}
      </div>
    </section>
  );
};
