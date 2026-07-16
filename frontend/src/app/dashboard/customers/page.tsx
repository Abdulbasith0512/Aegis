"use client";

import React, { useState, useMemo } from 'react';
import { DataTable, FilterBar, RiskBadge, Drawer } from '@/components/ui';
import type { ColumnDef } from '@/components/ui/DataTable';
import { MOCK_CUSTOMERS } from '@/lib/mockData';
import type { Customer, RiskLevel } from '@/lib/mockData';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { CHART_COLORS, AXIS_PROPS, GRID_PROPS, SharedTooltip, ChartContainer } from '@/components/ui';
import { generateSparkline } from '@/lib/mockData';

const COLUMNS: ColumnDef<Customer>[] = [
  { key: 'id', header: 'Customer ID', width: 140, mono: true },
  { key: 'name', header: 'Name', sortable: true, minWidth: 130 },
  { key: 'email', header: 'Email', sortable: true, minWidth: 180 },
  { key: 'country', header: 'Country', sortable: true, width: 80, mono: true },
  { key: 'riskLevel', header: 'Risk', width: 110, sortable: true,
    render: (v, row) => <RiskBadge level={(row as Customer).riskLevel} score={(row as Customer).riskScore} /> },
  { key: 'txCount', header: 'Txs', sortable: true, width: 80, mono: true },
  { key: 'lifetimeValue', header: 'LTV', sortable: true, width: 110, mono: true,
    render: (v) => `$${Number(v).toLocaleString('en', { maximumFractionDigits: 0 })}` },
  { key: 'flaggedCount', header: 'Flags', sortable: true, width: 70, mono: true,
    render: (v) => <span style={{ color: Number(v) > 5 ? 'var(--risk-critical-text)' : 'inherit' }}>{String(v)}</span> },
  { key: 'lastSeenAt', header: 'Last Seen', sortable: true, width: 130, mono: true,
    render: (v) => <span style={{ fontSize: 11, color: 'var(--gray-500)' }}>{new Date(String(v)).toLocaleDateString()}</span> },
];

export default function Customers() {
  const [search, setSearch] = useState('');
  const [activeFilters, setActiveFilters] = useState<Record<string, string[]>>({});
  const [selected, setSelected] = useState<Customer | null>(null);

  const filtered = useMemo(() => {
    let rows = MOCK_CUSTOMERS;
    if (search) {
      const q = search.toLowerCase();
      rows = rows.filter(c => c.name.toLowerCase().includes(q) || c.email.toLowerCase().includes(q) || c.id.toLowerCase().includes(q));
    }
    const rf = activeFilters['riskLevel'];
    if (rf?.length) rows = rows.filter(c => rf.includes(c.riskLevel));
    return rows;
  }, [search, activeFilters]);

  const riskTrend = generateSparkline(30, selected?.riskScore || 50, 10);

  return (
    <div style={{ maxWidth: 1600 }}>
      <div style={{ marginBottom: 20 }}>
        <h1 style={{ fontSize: 'var(--text-20)', fontWeight: 700, color: 'var(--gray-50)' }}>Customers</h1>
        <p style={{ fontSize: 'var(--text-13)', color: 'var(--gray-500)', marginTop: 4 }}>{MOCK_CUSTOMERS.length.toLocaleString()} total customers</p>
      </div>
      <div className="card" style={{ padding: 0 }}>
        <div style={{ padding: '14px 14px 10px', borderBottom: '1px solid var(--border-0)' }}>
          <FilterBar
            searchPlaceholder="Search by name, email, ID…"
            searchValue={search}
            onSearchChange={setSearch}
            filters={[{ key: 'riskLevel', label: 'Risk Level', options: ['critical','high','medium','low','safe'].map(v => ({ value: v, label: v.charAt(0).toUpperCase() + v.slice(1) })) }]}
            activeFilters={activeFilters}
            onFilterChange={(k, v) => setActiveFilters(p => ({ ...p, [k]: v }))}
            onClearAll={() => { setSearch(''); setActiveFilters({}); }}
            totalCount={MOCK_CUSTOMERS.length}
            filteredCount={filtered.length}
          />
        </div>
        <DataTable columns={COLUMNS} data={filtered} rowKey={c => c.id} maxHeight={580} onRowClick={setSelected} />
      </div>
      <Drawer open={!!selected} onClose={() => setSelected(null)} title={selected?.name} subtitle={selected?.id}>
        {selected && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
            <RiskBadge level={selected.riskLevel} score={selected.riskScore} />
            <div>
              <div className="text-label" style={{ marginBottom: 8 }}>Risk Score Trend (30 days)</div>
              <div style={{ height: 120 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={riskTrend}>
                    <CartesianGrid {...GRID_PROPS} />
                    <XAxis dataKey="ts" hide />
                    <YAxis {...AXIS_PROPS} domain={[0, 100]} width={28} />
                    <Tooltip content={<SharedTooltip />} />
                    <Line type="monotone" dataKey="value" stroke={CHART_COLORS.high} strokeWidth={1.5} dot={false} isAnimationActive={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
            {([['Email', selected.email], ['Country', selected.country], ['Transactions', selected.txCount], ['LTV', `$${selected.lifetimeValue.toLocaleString()}`], ['Devices', selected.devices], ['Payment Methods', selected.paymentMethods], ['Flags', selected.flaggedCount], ['Joined', new Date(selected.joinedAt).toLocaleDateString()]] as [string, unknown][]).map(([k, v]) => (
              <div key={k} style={{ display: 'flex', justifyContent: 'space-between', padding: '5px 0', borderBottom: '1px solid var(--border-0)', fontSize: 'var(--text-13)' }}>
                <span style={{ color: 'var(--gray-500)' }}>{k}</span>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--gray-200)' }}>{String(v)}</span>
              </div>
            ))}
          </div>
        )}
      </Drawer>
    </div>
  );
}
