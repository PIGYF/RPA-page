import type { FC } from 'react';
import type { StatusTone } from '../types';

interface StatusIconProps {
  tone: StatusTone;
}

const toneLabelMap: Record<StatusTone, string> = {
  healthy: 'Stable',
  warning: 'Warning',
  critical: 'Critical',
  paused: 'Paused',
  online: 'Online',
  busy: 'Busy',
  maintenance: 'Maintenance',
  success: 'Success',
  info: 'Info'
};

export const StatusIcon: FC<StatusIconProps> = ({ tone }) => (
  <span className={`status-icon status-${tone}`} title={toneLabelMap[tone]} aria-label={toneLabelMap[tone]} />
);
