import type { FC } from 'react';
import type { TimelineItem } from '../types';
import { StatusIcon } from './StatusIcon';

interface LiveActivityTimelineProps {
  items: TimelineItem[];
}

export const LiveActivityTimeline: FC<LiveActivityTimelineProps> = ({ items }) => (
  <section className="sidebar-card card">
    <div className="panel-header">
      <div>
        <p className="eyebrow">Live Activity</p>
        <h3>实时活动时间线</h3>
      </div>
    </div>

    <div className="timeline-list">
      {items.map((item) => (
        <article key={item.id} className="timeline-item">
          <div className="timeline-marker">
            <StatusIcon tone={item.severity} />
          </div>
          <div className="timeline-content">
            <div className="timeline-top-row">
              <strong>{item.title}</strong>
              <span>{item.time}</span>
            </div>
            <p>{item.description}</p>
            <small>{item.actor}</small>
          </div>
        </article>
      ))}
    </div>
  </section>
);
