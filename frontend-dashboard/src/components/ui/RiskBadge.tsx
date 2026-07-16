import React from 'react';
import type { RiskLevel } from '@/lib/mockData';

interface RiskBadgeProps {
  level: RiskLevel;
  score?: number;
  showDot?: boolean;
}

const RISK_LABELS: Record<RiskLevel, string> = {
  critical: 'Critical',
  high: 'High',
  medium: 'Medium',
  low: 'Low',
  safe: 'Safe',
};

export const RiskBadge: React.FC<RiskBadgeProps> = ({ level, score, showDot = true }) => {
  return (
    <span className={`risk-badge ${level}`}>
      {showDot && (
        <span
          style={{
            width: 5,
            height: 5,
            borderRadius: '50%',
            background: 'currentColor',
            flexShrink: 0,
          }}
        />
      )}
      {RISK_LABELS[level]}
      {score !== undefined && (
        <span style={{ opacity: 0.75, marginLeft: 2 }}>· {score}</span>
      )}
    </span>
  );
};
