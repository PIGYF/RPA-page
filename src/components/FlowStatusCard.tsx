import type { FC } from 'react';
import type { FlowItem } from '../types';
import { StatusIcon } from './StatusIcon';

interface FlowStatusCardProps {
  flow: FlowItem;
  onClick: (flowId: string) => void;
}

export const FlowStatusCard: FC<FlowStatusCardProps> = ({ flow, onClick }) => (
  <button type="button" className="flow-card" onClick={() => onClick(flow.id)}>
    <div className="flow-card-top">
      <div className="flow-name-group">
        <StatusIcon tone={flow.status} />
        <div>
          <strong>{flow.name}</strong>
          <span>{flow.owner}</span>
        </div>
      </div>
      <span className="queue-pill">{flow.queue} pending</span>
    </div>

    <div className="flow-metrics">
      <div>
        <span>成功率</span>
        <strong>{flow.successRate}%</strong>
      </div>
      <div>
        <span>平均耗时</span>
        <strong>{flow.avgHandleTime}</strong>
      </div>
    </div>

    <p>{flow.description}</p>
  </button>
);
