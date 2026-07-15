import type { FC } from 'react';

interface HeaderProps {
  currentTime: Date;
  lastUpdated: string;
  refreshing: boolean;
  onRefresh: () => void;
}

const timeFormatter = new Intl.DateTimeFormat('zh-CN', {
  weekday: 'short',
  hour: '2-digit',
  minute: '2-digit'
});

export const Header: FC<HeaderProps> = ({ currentTime, lastUpdated, refreshing, onRefresh }) => (
  <header className="dashboard-header card">
    <div>
      <p className="eyebrow">AI EMPLOYEE · SAP OPERATIONS CENTER</p>
      <h1>离线 SAP 运营指挥看板</h1>
      <p className="header-subtitle">面向 1920×1080 大屏与桌面浏览器的 React + Vite + TypeScript 仪表盘</p>
    </div>

    <div className="header-meta">
      <div className="header-clock">
        <span>当前时间</span>
        <strong>{timeFormatter.format(currentTime)}</strong>
      </div>

      <div className="header-refresh">
        <span>{refreshing ? '正在刷新…' : '分钟级自动刷新中'}</span>
        <strong>最近更新：{lastUpdated}</strong>
      </div>

      <button type="button" className="ghost-button" onClick={onRefresh}>
        立即刷新
      </button>
    </div>
  </header>
);
