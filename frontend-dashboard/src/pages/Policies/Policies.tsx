import React, { useState } from 'react';
import { Shield, Plus, ChevronRight } from 'lucide-react';

interface Policy {
  id: string;
  name: string;
  version: string;
  conditions: string[];
  action: 'BLOCK' | 'REVIEW' | 'APPROVE';
  enabled: boolean;
  hitRate: number;
  lastModified: string;
}

const POLICIES: Policy[] = [
  { id: 'POL-001', name: 'High-Value Crypto Block', version: 'v2.3', conditions: ['amount > $5000', 'merchant.category = Crypto'], action: 'BLOCK', enabled: true, hitRate: 2.1, lastModified: '2026-07-10' },
  { id: 'POL-002', name: 'New Device + High Amount', version: 'v1.1', conditions: ['device.is_new = true', 'amount > $1000'], action: 'REVIEW', enabled: true, hitRate: 5.8, lastModified: '2026-07-08' },
  { id: 'POL-003', name: 'Velocity Check (5/hr)', version: 'v3.0', conditions: ['tx_count_1h > 5'], action: 'BLOCK', enabled: true, hitRate: 0.9, lastModified: '2026-07-12' },
  { id: 'POL-004', name: 'Known Good Customer Bypass', version: 'v1.0', conditions: ['customer.tenure_days > 365', 'amount < $200'], action: 'APPROVE', enabled: false, hitRate: 18.4, lastModified: '2026-07-01' },
  { id: 'POL-005', name: 'Sanctioned Country Block', version: 'v4.1', conditions: ['country IN [KP, IR, SY, BY]'], action: 'BLOCK', enabled: true, hitRate: 0.3, lastModified: '2026-07-13' },
];

const ACTION_COLORS = { BLOCK: 'var(--risk-critical-text)', REVIEW: 'var(--risk-medium-text)', APPROVE: 'var(--status-success)' };

export default function Policies() {
  const [policies, setPolicies] = useState(POLICIES);
  const toggle = (id: string) => setPolicies(ps => ps.map(p => p.id === id ? { ...p, enabled: !p.enabled } : p));

  return (
    <div style={{ maxWidth: 1100 }}>
      <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', marginBottom: 20 }}>
        <div>
          <h1 style={{ fontSize: 'var(--text-20)', fontWeight: 700, color: 'var(--gray-50)' }}>Policies</h1>
          <p style={{ fontSize: 'var(--text-13)', color: 'var(--gray-500)', marginTop: 4 }}>{policies.filter(p => p.enabled).length} active rules</p>
        </div>
        <button className="btn btn-primary"><Plus size={13} /> New Policy</button>
      </div>
      <div className="card" style={{ padding: 0 }}>
        {policies.map((policy, i) => (
          <div key={policy.id} style={{ display: 'flex', alignItems: 'flex-start', gap: 14, padding: '14px 16px', borderBottom: i < policies.length - 1 ? '1px solid var(--border-0)' : 'none', opacity: policy.enabled ? 1 : 0.5 }}>
            {/* Toggle */}
            <button
              onClick={() => toggle(policy.id)}
              style={{
                width: 36, height: 20, borderRadius: 10, border: 'none',
                background: policy.enabled ? 'var(--accent-dim)' : 'var(--surface-4)',
                cursor: 'pointer', position: 'relative', flexShrink: 0, marginTop: 2,
                borderColor: policy.enabled ? 'var(--accent-muted)' : 'var(--border-2)',
                outline: '1px solid',
                outlineColor: policy.enabled ? 'var(--accent-muted)' : 'var(--border-2)',
                transition: 'all var(--motion-fast)',
              }}
            >
              <div style={{
                width: 14, height: 14, borderRadius: '50%', background: policy.enabled ? 'var(--accent)' : 'var(--gray-500)',
                position: 'absolute', top: 3, left: policy.enabled ? 19 : 3, transition: 'left var(--motion-fast)',
              }} />
            </button>
            {/* Content */}
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                <span style={{ fontSize: 'var(--text-14)', fontWeight: 600, color: 'var(--gray-100)' }}>{policy.name}</span>
                <span style={{ fontSize: 10, fontFamily: 'var(--font-mono)', color: 'var(--gray-500)', background: 'var(--surface-3)', padding: '1px 5px', borderRadius: 3 }}>{policy.version}</span>
                <span style={{
                  fontSize: 10, fontFamily: 'var(--font-mono)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em',
                  color: ACTION_COLORS[policy.action], background: `${ACTION_COLORS[policy.action]}22`, padding: '2px 6px', borderRadius: 4, border: `1px solid ${ACTION_COLORS[policy.action]}`,
                }}>{policy.action}</span>
              </div>
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 6 }}>
                {policy.conditions.map(cond => (
                  <span key={cond} style={{
                    fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--accent)',
                    background: 'var(--accent-dim)', border: '1px solid var(--accent-muted)',
                    padding: '2px 7px', borderRadius: 4,
                  }}>{cond}</span>
                ))}
              </div>
              <div style={{ display: 'flex', gap: 14, fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--gray-500)' }}>
                <span>Hit rate: {policy.hitRate}%</span>
                <span>Last modified: {policy.lastModified}</span>
                <span>ID: {policy.id}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
