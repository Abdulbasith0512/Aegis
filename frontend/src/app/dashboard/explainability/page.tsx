"use client";

import React, { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Cell, ResponsiveContainer } from 'recharts';
import { ChartContainer, RiskBadge, SharedTooltip, CHART_COLORS, AXIS_PROPS, GRID_PROPS } from '@/components/ui';

// Mock SHAP waterfall data for a sample transaction
const SHAP_DATA = [
  { feature: 'Base rate', value: 0.0, type: 'base' },
  { feature: 'Tx amount ($1500)', value: 28, type: 'positive' },
  { feature: 'New device', value: 22, type: 'positive' },
  { feature: 'Crypto merchant', value: 18, type: 'positive' },
  { feature: 'Velocity (5/hr)', value: 15, type: 'positive' },
  { feature: 'Country: NG', value: 9, type: 'positive' },
  { feature: 'Customer tenure (2y)', value: -12, type: 'negative' },
  { feature: 'KYC verified', value: -8, type: 'negative' },
  { feature: 'Normal hour', value: -4, type: 'negative' },
];

const RULES_FIRED = [
  { id: 'R-001', name: 'High-value crypto transfer', weight: 0.28, matched: true },
  { id: 'R-004', name: 'New device fingerprint', weight: 0.22, matched: true },
  { id: 'R-012', name: 'Velocity: >5 txs/hour', weight: 0.15, matched: true },
  { id: 'R-019', name: 'High-risk merchant category', weight: 0.18, matched: true },
  { id: 'R-033', name: 'Known good customer', weight: -0.12, matched: true },
  { id: 'R-044', name: 'KYC full verification', weight: -0.08, matched: true },
];

export default function Explainability() {
  const [selectedTx] = useState('TX_9B8C3D1A');
  const finalScore = 92;

  return (
    <div style={{ maxWidth: 1200 }}>
      <div style={{ marginBottom: 20 }}>
        <h1 style={{ fontSize: 'var(--text-20)', fontWeight: 700, color: 'var(--gray-50)' }}>Explainability</h1>
        <p style={{ fontSize: 'var(--text-13)', color: 'var(--gray-500)', marginTop: 4 }}>Per-decision feature attribution and rule impact</p>
      </div>

      {/* Transaction selector */}
      <div className="card" style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 16 }}>
        <div style={{ fontSize: 'var(--text-13)', color: 'var(--gray-400)' }}>Explaining decision for:</div>
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--text-14)', color: 'var(--accent)', fontWeight: 600 }}>{selectedTx}</span>
        <RiskBadge level="critical" score={finalScore} />
        <div style={{ marginLeft: 'auto', display: 'flex', gap: 10, fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--gray-500)' }}>
          <span>Model: FraudShield-v2</span>
          <span>Agent verdict: BLOCK</span>
          <span>Final: DECLINED</span>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14, marginBottom: 14 }}>
        {/* SHAP waterfall */}
        <ChartContainer title="Feature Attribution (SHAP)" subtitle="Impact of each feature on fraud score" height={280}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={SHAP_DATA}
              layout="vertical"
              margin={{ top: 4, right: 20, bottom: 0, left: 140 }}
            >
              <CartesianGrid {...GRID_PROPS} />
              <XAxis type="number" {...AXIS_PROPS} />
              <YAxis dataKey="feature" type="category" {...AXIS_PROPS} width={140} tick={{ ...AXIS_PROPS.tick, textAnchor: 'end' }} />
              <Tooltip content={<SharedTooltip />} />
              <Bar dataKey="value" radius={[0, 3, 3, 0]} isAnimationActive={false} name="SHAP value">
                {SHAP_DATA.map((entry, index) => (
                  <Cell
                    key={index}
                    fill={entry.type === 'positive' ? CHART_COLORS.critical : entry.type === 'negative' ? CHART_COLORS.low : CHART_COLORS.accent}
                    opacity={0.85}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartContainer>

        {/* Confidence gauge */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 16 }}>
          <div className="text-label">Model Confidence</div>
          <svg width={180} height={180} viewBox="0 0 180 180">
            {/* Track */}
            <circle cx="90" cy="90" r="70" fill="none" stroke="var(--surface-3)" strokeWidth="14" />
            {/* Progress — partial arc from 90deg to angle */}
            <circle
              cx="90" cy="90" r="70"
              fill="none"
              stroke={CHART_COLORS.critical}
              strokeWidth="14"
              strokeDasharray={`${(finalScore / 100) * 2 * Math.PI * 70} ${2 * Math.PI * 70}`}
              strokeDashoffset={2 * Math.PI * 70 * 0.25}
              strokeLinecap="round"
            />
            {/* Center text */}
            <text x="90" y="82" textAnchor="middle" fill="var(--gray-50)" fontSize="32" fontWeight="700" fontFamily="var(--font-mono)">{finalScore}</text>
            <text x="90" y="104" textAnchor="middle" fill="var(--gray-500)" fontSize="11" fontFamily="var(--font-sans)">Risk Score</text>
          </svg>
          <div style={{ display: 'flex', gap: 20, fontSize: 12, fontFamily: 'var(--font-mono)', color: 'var(--gray-400)' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 'var(--text-16)', fontWeight: 700, color: 'var(--gray-100)' }}>97.2%</div>
              <div>Confidence</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 'var(--text-16)', fontWeight: 700, color: 'var(--gray-100)' }}>0.918</div>
              <div>Model score</div>
            </div>
          </div>
        </div>
      </div>

      {/* Rules fired */}
      <div className="card" style={{ padding: 0 }}>
        <div style={{ padding: '14px 16px 10px', borderBottom: '1px solid var(--border-0)' }}>
          <div className="text-title" style={{ fontSize: 'var(--text-14)' }}>Rules Fired ({RULES_FIRED.length})</div>
        </div>
        {RULES_FIRED.map(rule => (
          <div key={rule.id} style={{ display: 'flex', alignItems: 'center', gap: 14, padding: '10px 16px', borderBottom: '1px solid var(--border-0)' }}>
            <span style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--gray-600)', minWidth: 56 }}>{rule.id}</span>
            <span style={{ flex: 1, fontSize: 'var(--text-13)', color: 'var(--gray-200)' }}>{rule.name}</span>
            <div style={{ width: 160, background: 'var(--surface-3)', borderRadius: 4, height: 6, overflow: 'hidden' }}>
              <div style={{
                width: `${Math.abs(rule.weight) * 100 * 3.5}%`,
                height: '100%',
                background: rule.weight > 0 ? CHART_COLORS.critical : CHART_COLORS.low,
                borderRadius: 4,
              }} />
            </div>
            <span style={{
              fontSize: 11, fontFamily: 'var(--font-mono)', fontWeight: 600, minWidth: 50, textAlign: 'right',
              color: rule.weight > 0 ? CHART_COLORS.critical : CHART_COLORS.low,
            }}>
              {rule.weight > 0 ? '+' : ''}{(rule.weight * 100).toFixed(0)}pts
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
