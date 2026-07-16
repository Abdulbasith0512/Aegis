import React from 'react';
import { MOCK_INCIDENTS } from '@/lib/mockData';
import { RiskBadge, ChartContainer, SharedTooltip, CHART_COLORS, AXIS_PROPS, GRID_PROPS } from '@/components/ui';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { AlertTriangle, CheckCircle2, Clock, Activity } from 'lucide-react';

const STATUS_ICON: Record<string, React.ReactNode> = {
  open: <AlertTriangle size={13} color="var(--risk-critical-text)" />,
  investigating: <Activity size={13} color="var(--risk-medium-text)" />,
  resolved: <CheckCircle2 size={13} color="var(--status-success)" />,
  postmortem: <Clock size={13} color="var(--gray-400)" />,
};

const MTTR_DATA = MOCK_INCIDENTS.filter(i => i.mttrMinutes).slice(0, 15).map(i => ({
  id: i.id.slice(-6),
  mttr: i.mttrMinutes,
}));

export default function Incidents() {
  return (
    <div style={{ maxWidth: 1600 }}>
      <div style={{ marginBottom: 20 }}>
        <h1 style={{ fontSize: 'var(--text-20)', fontWeight: 700, color: 'var(--gray-50)' }}>Incidents</h1>
        <p style={{ fontSize: 'var(--text-13)', color: 'var(--gray-500)', marginTop: 4 }}>
          {MOCK_INCIDENTS.filter(i => i.status === 'open' || i.status === 'investigating').length} active · {MOCK_INCIDENTS.length} total
        </p>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 360px', gap: 14 }}>
        <div>
          {/* MTTR chart */}
          <div style={{ marginBottom: 14 }}>
            <ChartContainer title="Mean Time to Resolve (MTTR)" subtitle="Minutes per incident" height={160}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={MTTR_DATA} margin={{ top: 4, right: 4, bottom: 0, left: 0 }}>
                  <CartesianGrid {...GRID_PROPS} />
                  <XAxis dataKey="id" {...AXIS_PROPS} />
                  <YAxis {...AXIS_PROPS} width={36} />
                  <Tooltip content={<SharedTooltip />} />
                  <Bar dataKey="mttr" fill={CHART_COLORS.high} radius={[3, 3, 0, 0]} isAnimationActive={false} name="MTTR (min)" />
                </BarChart>
              </ResponsiveContainer>
            </ChartContainer>
          </div>
          {/* Incident list */}
          <div className="card" style={{ padding: 0 }}>
            {MOCK_INCIDENTS.slice(0, 20).map(inc => (
              <div key={inc.id} style={{ display: 'flex', gap: 12, padding: '12px 16px', borderBottom: '1px solid var(--border-0)' }}>
                <div style={{ flexShrink: 0, marginTop: 2 }}>{STATUS_ICON[inc.status]}</div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                    <span style={{ fontSize: 'var(--text-14)', fontWeight: 500, color: 'var(--gray-100)' }}>{inc.title}</span>
                    <RiskBadge level={inc.severity} />
                  </div>
                  <div style={{ display: 'flex', gap: 12, fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--gray-500)' }}>
                    <span>Started: {new Date(inc.startedAt).toLocaleString()}</span>
                    {inc.mttrMinutes && <span>MTTR: {inc.mttrMinutes}m</span>}
                    <span>Services: {inc.affectedServices.join(', ')}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
        {/* Timeline sidebar */}
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{ padding: '14px 16px 10px', borderBottom: '1px solid var(--border-0)' }}>
            <div className="text-title" style={{ fontSize: 'var(--text-14)' }}>Latest Updates</div>
          </div>
          <div style={{ overflowY: 'auto', maxHeight: 560 }}>
            {MOCK_INCIDENTS.slice(0, 5).flatMap(inc => inc.updates.map((u, i) => ({ ...u, incId: inc.id, incTitle: inc.title, severity: inc.severity, idx: i }))).sort((a, b) => new Date(b.ts).getTime() - new Date(a.ts).getTime()).slice(0, 25).map((update, i) => (
              <div key={i} style={{ padding: '10px 14px', borderBottom: '1px solid var(--border-0)' }}>
                <div style={{ fontSize: 10, fontFamily: 'var(--font-mono)', color: 'var(--gray-600)', marginBottom: 3 }}>{new Date(update.ts).toLocaleString()}</div>
                <div style={{ fontSize: 'var(--text-12)', color: 'var(--gray-400)', marginBottom: 2 }}><span style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent)', fontSize: 10 }}>{update.incTitle}</span></div>
                <div style={{ fontSize: 'var(--text-13)', color: 'var(--gray-300)' }}>{update.message}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
