import type { FC } from 'react';
import type { Insight } from '../types';

interface AiInsightPanelProps {
  insights: Insight[];
}

export const AiInsightPanel: FC<AiInsightPanelProps> = ({ insights }) => (
  <section className="insight-panel card">
    <div className="panel-header">
      <div>
        <p className="eyebrow">AI Insight</p>
        <h3>智能洞察与建议</h3>
      </div>
    </div>

    <div className="insight-list">
      {insights.map((insight) => (
        <article key={insight.id} className="insight-card">
          <div className="insight-top-row">
            <span className="tag">{insight.tag}</span>
            <strong>{insight.confidence}%</strong>
          </div>
          <h4>{insight.title}</h4>
          <p>{insight.detail}</p>
          <footer>{insight.impact}</footer>
        </article>
      ))}
    </div>
  </section>
);
