"use client";

import React from 'react';
import { Shield, AlertTriangle, CheckCircle2, Clock } from 'lucide-react';

const SERVICES = [
  { name: 'Transaction Processor', uptime: 99.98, sla: 99.9, status: 'healthy' },
  { name: 'Fraud Engine', uptime: 99.91, sla: 99.9, status: 'healthy' },
  { name: 'ML Inference API', uptime: 99.74, sla: 99.9, status: 'degraded' },
  { name: 'Rule Evaluator', uptime: 99.99, sla: 99.9, status: 'healthy' },
  { name: 'Identity Service', uptime: 100.0, sla: 99.9, status: 'healthy' },
  { name: 'Audit Ledger', uptime: 100.0, sla: 99.9, status: 'healthy' },
  { name: 'Payment Gateway', uptime: 99.82, sla: 99.9, status: 'degraded' },
  { name: 'Notification Service', uptime: 99.95, sla: 99.9, status: 'healthy' },
];

const STATUS_COLORS: Record<string, string> = {
  healthy: 'var(--status-success)',
  degraded: 'var(--risk-medium)',
  outage: 'var(--risk-critical)',
};

// Calendar heatmap (mock uptime data)
const DAYS = 90;
const CALENDAR_DATA = Array.from({ length: DAYS }, (_, i) => {
  const d = new Date(Date.now() - (DAYS - i) * 86400000);
  const uptime = Math.random() > 0.05 ? 100 : Math.random() > 0.5 ? 99.2 + Math.random() * 0.7 : 95 + Math.random() * 4;
  return {
    date: d.toISOString().slice(0, 10),
    uptime,
    day: d.getDay(),
    week: Math.floor(i / 7),
  };
});

function uptimeColor(u: number): string {
  if (u >= 99.9) return '#22c55e';
  if (u >= 99.0) return '#f59e0b';
  if (u >= 95) return '#ff7a00';
  return '#ff3b3b';
}

export default function TrustCenter() {
  const overallUptime = (SERVICES.reduce((a, s) => a + s.uptime, 0) / SERVICES.length).toFixed(3);
  return (
    <div style={{ maxWidth: 1400 }}>
      <div style={{ marginBottom: 20 }}>
        <h1 style={{ fontSize: 'var(--text-20)', fontWeight: 700, color: 'var(--gray-50)' }}>Trust Center</h1>
        <p style={{ fontSize: 'var(--text-13)', color: 'var(--gray-500)', marginTop: 4 }}>System health, SLA compliance, and uptime history</p>
      </div>
      {/* Overall status banner */}
      <div className="card" style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 14, borderColor: SERVICES.every(s => s.status === 'healthy') ? 'var(--status-success)' : 'var(--risk-medium)' }}>
        {SERVICES.every(s => s.status === 'healthy') ? <CheckCircle2 size={24} color="var(--status-success)" /> : <AlertTriangle size={24} color="var(--risk-medium)" />}
        <div>
          <div style={{ fontSize: 'var(--text-16)', fontWeight: 600, color: 'var(--gray-50)' }}>
            {SERVICES.some(s => s.status !== 'healthy') ? 'Partial System Degradation' : 'All Systems Operational'}
          </div>
          <div style={{ fontSize: 'var(--text-13)', color: 'var(--gray-400)', marginTop: 2 }}>Overall uptime: {overallUptime}% · Last checked: {new Date().toLocaleTimeString()}</div>
        </div>
      </div>
      {/* Service rows */}
      <div className="card" style={{ padding: 0, marginBottom: 14 }}>
        {SERVICES.map((svc, i) => (
          <div key={svc.name} style={{ display: 'flex', alignItems: 'center', gap: 14, padding: '12px 16px', borderBottom: i < SERVICES.length - 1 ? '1px solid var(--border-0)' : 'none' }}>
            <div style={{ width: 8, height: 8, borderRadius: '50%', background: STATUS_COLORS[svc.status], flexShrink: 0 }} />
            <span style={{ flex: 1, fontSize: 'var(--text-14)', color: 'var(--gray-200)' }}>{svc.name}</span>
            <span style={{ fontSize: 11, fontFamily: 'var(--font-mono)', fontWeight: 600, color: STATUS_COLORS[svc.status], textTransform: 'uppercase', letterSpacing: '0.04em', minWidth: 80, textAlign: 'right' }}>{svc.status}</span>
            <div style={{ width: 200, background: 'var(--surface-3)', borderRadius: 4, height: 6, overflow: 'hidden' }}>
              <div style={{ width: `${svc.uptime}%`, height: '100%', background: STATUS_COLORS[svc.status], borderRadius: 4, transition: 'width 1s ease' }} />
            </div>
            <span style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--gray-400)', minWidth: 60, textAlign: 'right' }}>{svc.uptime}%</span>
          </div>
        ))}
      </div>
      {/* Calendar heatmap */}
      <div className="card" style={{ padding: 0 }}>
        <div style={{ padding: '14px 16px 10px', borderBottom: '1px solid var(--border-0)' }}>
          <div className="text-title" style={{ fontSize: 'var(--text-14)' }}>Uptime Calendar (90 days)</div>
          <div className="text-caption" style={{ marginTop: 2 }}>Daily uptime heatmap across all services</div>
        </div>
        <div style={{ padding: '16px', overflowX: 'auto' }}>
          <svg viewBox={`0 0 ${Math.ceil(DAYS / 7) * 16} 120`} style={{ minWidth: 600 }}>
            {['Sun','Mon','Tue','Wed','Thu','Fri','Sat'].map((d, i) => (
              <text key={d} x={-4} y={16 + i * 16} textAnchor="end" fill="var(--gray-600)" fontSize={9} fontFamily="var(--font-sans)">{d}</text>
            ))}
            {CALENDAR_DATA.map((cell) => (
              <rect
                key={cell.date}
                x={cell.week * 16 + 4}
                y={cell.day * 16 + 8}
                width={13}
                height={13}
                rx={2}
                fill={uptimeColor(cell.uptime)}
                opacity={0.8}
              >
                <title>{`${cell.date}: ${cell.uptime.toFixed(2)}%`}</title>
              </rect>
            ))}
          </svg>
          <div style={{ display: 'flex', gap: 12, marginTop: 8, justifyContent: 'flex-end' }}>
            {[['100%', '#22c55e'], ['≥99%', '#f59e0b'], ['≥95%', '#ff7a00'], ['<95%', '#ff3b3b']].map(([label, color]) => (
              <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 10, color: 'var(--gray-500)' }}>
                <span style={{ width: 10, height: 10, borderRadius: 2, background: color }} />{label}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
