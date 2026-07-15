import type { FC } from 'react';
import type { DailyBriefData } from '../types';

interface DailyBriefProps {
  brief: DailyBriefData;
}

export const DailyBrief: FC<DailyBriefProps> = ({ brief }) => (
  <section className="sidebar-card card">
    <div className="panel-header">
      <div>
        <p className="eyebrow">Daily Brief</p>
        <h3>运营简报</h3>
      </div>
    </div>

    <p className="brief-headline">{brief.headline}</p>

    <div className="brief-sections">
      {brief.sections.map((section) => (
        <article key={section.title} className="brief-section">
          <div className="brief-section-top">
            <strong>{section.title}</strong>
            <span>{section.emphasis}</span>
          </div>
          <p>{section.detail}</p>
        </article>
      ))}
    </div>

    <div className="recommended-actions">
      {brief.recommendedActions.map((action) => (
        <span key={action} className="tag">
          {action}
        </span>
      ))}
    </div>
  </section>
);
