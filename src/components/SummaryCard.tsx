import type { CSSProperties, FC } from 'react';
import type { SummaryMetric } from '../types';

interface SummaryCardProps {
  summary: SummaryMetric;
}

export const SummaryCard: FC<SummaryCardProps> = ({ summary }) => (
  <article
    className="summary-card card"
    style={{ '--accent-color': summary.accent } as CSSProperties}
  >
    <span className="summary-label">{summary.label}</span>
    <div className="summary-value-row">
      <strong>{summary.value}</strong>
      <span className="summary-change">{summary.change}</span>
    </div>
    <p>{summary.description}</p>
  </article>
);
