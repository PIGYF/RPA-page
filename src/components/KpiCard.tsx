import type { FC } from 'react';
import type { KpiMetric } from '../types';

interface KpiCardProps {
  kpi: KpiMetric;
}

export const KpiCard: FC<KpiCardProps> = ({ kpi }) => (
  <article className="kpi-card card">
    <div className="kpi-top-row">
      <span>{kpi.label}</span>
      <span className={`trend-chip trend-${kpi.direction}`}>{kpi.trend}</span>
    </div>

    <div className="kpi-value-row">
      <strong>
        {kpi.value}
        {kpi.unit ? <small>{kpi.unit}</small> : null}
      </strong>
      <span>{kpi.trendLabel}</span>
    </div>

    <div className="progress-track">
      <div className="progress-bar" style={{ width: `${kpi.progress}%` }} />
    </div>
  </article>
);
