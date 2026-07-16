"use client";

import React, { useState } from 'react';
import { MOCK_REVIEW_CASES } from '@/lib/mockData';
import { RiskBadge, DataTable, FilterBar, Drawer } from '@/components/ui';
import type { ColumnDef } from '@/components/ui/DataTable';
import type { ReviewCase } from '@/lib/mockData';
import { Clock, AlertTriangle } from 'lucide-react';

function slaStatus(deadline: string): { label: string; color: string } {
  const msLeft = new Date(deadline).getTime() - Date.now();
  if (msLeft < 0) return { label: 'Breached', color: 'var(--risk-critical-text)' };
  if (msLeft < 3600000) return { label: `${Math.round(msLeft / 60000)}m left`, color: 'var(--risk-high-text)' };
  return { label: `${(msLeft / 3600000).toFixed(1)}h left`, color: 'var(--risk-low-text)' };
}

const COLUMNS: ColumnDef<ReviewCase>[] = [
  { key: 'id', header: 'Case ID', width: 130, mono: true },
  { key: 'customerName', header: 'Customer', sortable: true },
  { key: 'amount', header: 'Amount', sortable: true, mono: true, width: 110,
    render: (v) => `$${Number(v).toLocaleString('en', { minimumFractionDigits: 2 })}` },
  { key: 'riskLevel', header: 'Risk', width: 110, render: (v, row) => <RiskBadge level={(row as ReviewCase).riskLevel} score={(row as ReviewCase).riskScore} /> },
  { key: 'reason', header: 'Reason', minWidth: 180 },
  { key: 'assignedTo', header: 'Assigned', width: 120, mono: true },
  { key: 'status', header: 'Status', width: 100, sortable: true,
    render: (v) => <span style={{ fontSize: 11, fontFamily: 'var(--font-mono)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em', color: v === 'pending' ? 'var(--risk-medium-text)' : v === 'in_review' ? 'var(--accent)' : v === 'approved' ? 'var(--status-success)' : v === 'rejected' ? 'var(--risk-critical-text)' : 'var(--gray-400)' }}>{String(v)}</span> },
  { key: 'slaDeadline', header: 'SLA', width: 100,
    render: (v) => { const { label, color } = slaStatus(String(v)); return <span style={{ fontSize: 11, fontFamily: 'var(--font-mono)', fontWeight: 600, color }}>{label}</span>; } },
];

export default function HumanReviews() {
  const [search, setSearch] = useState('');
  const [activeFilters, setActiveFilters] = useState<Record<string, string[]>>({});
  const [selected, setSelected] = useState<ReviewCase | null>(null);

  const filtered = MOCK_REVIEW_CASES.filter(c => {
    if (search && !c.customerName.toLowerCase().includes(search.toLowerCase()) && !c.id.toLowerCase().includes(search.toLowerCase())) return false;
    const sf = activeFilters['status'];
    if (sf?.length && !sf.includes(c.status)) return false;
    return true;
  });

  return (
    <div style={{ maxWidth: 1600 }}>
      <div style={{ marginBottom: 20 }}>
        <h1 style={{ fontSize: 'var(--text-20)', fontWeight: 700, color: 'var(--gray-50)' }}>Human Reviews</h1>
        <p style={{ fontSize: 'var(--text-13)', color: 'var(--gray-500)', marginTop: 4 }}>{MOCK_REVIEW_CASES.length} cases in queue</p>
      </div>
      <div className="card" style={{ padding: 0 }}>
        <div style={{ padding: '14px 14px 10px', borderBottom: '1px solid var(--border-0)' }}>
          <FilterBar
            searchPlaceholder="Search cases…"
            searchValue={search}
            onSearchChange={setSearch}
            filters={[{ key: 'status', label: 'Status', options: ['pending','in_review','approved','rejected','escalated'].map(v => ({ value: v, label: v.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) })) }]}
            activeFilters={activeFilters}
            onFilterChange={(k, v) => setActiveFilters(p => ({ ...p, [k]: v }))}
            onClearAll={() => { setSearch(''); setActiveFilters({}); }}
            totalCount={MOCK_REVIEW_CASES.length}
            filteredCount={filtered.length}
          />
        </div>
        <DataTable columns={COLUMNS} data={filtered} rowKey={c => c.id} maxHeight={580} onRowClick={setSelected} />
      </div>
      <Drawer open={!!selected} onClose={() => setSelected(null)} title={selected?.id} subtitle={selected?.customerName}>
        {selected && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <div style={{ display: 'flex', gap: 8 }}>
              <RiskBadge level={selected.riskLevel} score={selected.riskScore} />
            </div>
            <div>
              <p style={{ fontSize: 'var(--text-13)', color: 'var(--gray-400)', marginBottom: 12 }}><strong style={{ color: 'var(--gray-200)' }}>Reason:</strong> {selected.reason}</p>
              {[['Amount', `$${selected.amount.toFixed(2)}`], ['Assigned To', selected.assignedTo], ['SLA Deadline', new Date(selected.slaDeadline).toLocaleString()], ['Created', new Date(selected.createdAt).toLocaleString()]].map(([k, v]) => (
                <div key={k} style={{ display: 'flex', justifyContent: 'space-between', padding: '5px 0', borderBottom: '1px solid var(--border-0)', fontSize: 'var(--text-13)' }}>
                  <span style={{ color: 'var(--gray-500)' }}>{k}</span>
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--gray-200)' }}>{v}</span>
                </div>
              ))}
            </div>
            <div style={{ display: 'flex', gap: 8, paddingTop: 8 }}>
              <button className="btn btn-primary" style={{ flex: 1, justifyContent: 'center' }}>✓ Approve</button>
              <button className="btn btn-danger" style={{ flex: 1, justifyContent: 'center' }}>✗ Reject</button>
              <button className="btn btn-outline">↑ Escalate</button>
            </div>
          </div>
        )}
      </Drawer>
    </div>
  );
}
