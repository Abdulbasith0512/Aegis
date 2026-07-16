import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer,
} from 'recharts';
import { ArrowUpRight } from 'lucide-react';
import {
  DataTable, FilterBar, RiskBadge, Drawer, ChartContainer,
  SharedTooltip, CHART_COLORS, AXIS_PROPS, GRID_PROPS,
} from '@/components/ui';
import type { ColumnDef } from '@/components/ui/DataTable';
import { MOCK_TRANSACTIONS, generateTransaction } from '@/lib/mockData';
import type { Transaction, RiskLevel, TxStatus } from '@/lib/mockData';
import { eventStream } from '@/lib/eventStream';
import type { StreamEvent } from '@/lib/eventStream';

// Amount histogram data
function buildAmountHistogram(txs: Transaction[]) {
  const buckets = [0, 100, 500, 1000, 5000, 10000, 25000];
  return buckets.slice(0, -1).map((min, i) => {
    const max = buckets[i + 1];
    return {
      label: `$${min}–${max}`,
      count: txs.filter(t => t.amount >= min && t.amount < max).length,
    };
  });
}

function buildRiskHistogram(txs: Transaction[]) {
  const buckets = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90];
  return buckets.map(b => ({
    label: `${b}–${b + 10}`,
    count: txs.filter(t => t.riskScore >= b && t.riskScore < b + 10).length,
    color: b >= 80 ? CHART_COLORS.critical : b >= 60 ? CHART_COLORS.high : b >= 40 ? CHART_COLORS.medium : CHART_COLORS.low,
  }));
}

const STATUS_COLORS: Record<TxStatus, string> = {
  approved: 'var(--status-success)',
  declined: 'var(--risk-critical-text)',
  review: 'var(--risk-medium-text)',
  flagged: 'var(--risk-high-text)',
};

// ── Columns ────────────────────────────────────────────────────────────────
const COLUMNS: ColumnDef<Transaction>[] = [
  { key: 'id', header: 'TX ID', width: 130, mono: true, sortable: false,
    render: (v) => <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--gray-400)' }}>{String(v)}</span> },
  { key: 'customerName', header: 'Customer', sortable: true, minWidth: 130 },
  { key: 'merchantName', header: 'Merchant', sortable: true, minWidth: 120 },
  { key: 'merchantCategory', header: 'Category', sortable: true, minWidth: 100 },
  { key: 'amount', header: 'Amount', sortable: true, mono: true, width: 110,
    render: (v, row) => (
      <span style={{ fontFamily: 'var(--font-mono)', fontSize: 12 }}>
        {(row as Transaction).currency} {Number(v).toLocaleString('en', { minimumFractionDigits: 2 })}
      </span>
    )},
  { key: 'riskScore', header: 'Risk Score', sortable: true, width: 100,
    render: (v, row) => <RiskBadge level={(row as Transaction).riskLevel} score={Number(v)} /> },
  { key: 'status', header: 'Status', sortable: true, width: 90,
    render: (v) => (
      <span style={{
        fontSize: 'var(--text-11)', fontFamily: 'var(--font-mono)', fontWeight: 600,
        color: STATUS_COLORS[v as TxStatus], textTransform: 'uppercase', letterSpacing: '0.04em',
      }}>
        {String(v)}
      </span>
    )},
  { key: 'country', header: 'Country', sortable: true, width: 70, mono: true },
  { key: 'timestamp', header: 'Time', sortable: true, width: 160, mono: true,
    render: (v) => <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--gray-500)' }}>{new Date(String(v)).toLocaleString()}</span> },
];

// ── Transactions Page ──────────────────────────────────────────────────────
export default function Transactions() {
  const [allTxs, setAllTxs] = useState<Transaction[]>(MOCK_TRANSACTIONS);
  const [newRowIds, setNewRowIds] = useState<Set<string>>(new Set());
  const [newCount, setNewCount] = useState(0);
  const [pendingRows, setPendingRows] = useState<Transaction[]>([]);
  const [search, setSearch] = useState('');
  const [activeFilters, setActiveFilters] = useState<Record<string, string[]>>({});
  const [selectedTx, setSelectedTx] = useState<Transaction | null>(null);

  // Accept new transactions into the table (capped at 2000 total)
  const MAX_ROWS = 2000;
  const flushPending = useCallback(() => {
    setAllTxs(prev => {
      const ids = new Set<string>(pendingRows.map(t => t.id));
      setNewRowIds(ids);
      setTimeout(() => setNewRowIds(new Set()), 2000);
      return [...pendingRows, ...prev].slice(0, MAX_ROWS);
    });
    setPendingRows([]);
    setNewCount(0);
  }, [pendingRows]);

  useEffect(() => {
    const unsub = eventStream.on('new_transaction', (e: StreamEvent) => {
      const tx = e.payload as Transaction;
      setPendingRows(prev => [tx, ...prev].slice(0, 50));
      setNewCount(c => c + 1);
    });
    return unsub;
  }, []);

  // Filter logic
  const filtered = useMemo(() => {
    let rows = allTxs;
    if (search) {
      const q = search.toLowerCase();
      rows = rows.filter(t =>
        t.id.toLowerCase().includes(q) ||
        t.customerName.toLowerCase().includes(q) ||
        t.merchantName.toLowerCase().includes(q) ||
        t.country.toLowerCase().includes(q)
      );
    }
    const riskF = activeFilters['riskLevel'];
    if (riskF?.length) rows = rows.filter(t => riskF.includes(t.riskLevel));
    const statusF = activeFilters['status'];
    if (statusF?.length) rows = rows.filter(t => statusF.includes(t.status));
    return rows;
  }, [allTxs, search, activeFilters]);

  const amountHisto = useMemo(() => buildAmountHistogram(filtered.slice(0, 500)), [filtered]);
  const riskHisto   = useMemo(() => buildRiskHistogram(filtered.slice(0, 500)), [filtered]);

  return (
    <div style={{ maxWidth: 1600 }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', marginBottom: 20 }}>
        <div>
          <h1 style={{ fontSize: 'var(--text-20)', fontWeight: 700, color: 'var(--gray-50)', lineHeight: 1 }}>Transactions</h1>
          <p style={{ fontSize: 'var(--text-13)', color: 'var(--gray-500)', marginTop: 4 }}>
            {allTxs.length.toLocaleString()} total · live stream active
          </p>
        </div>
      </div>

      {/* Distribution charts */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14, marginBottom: 14 }}>
        <ChartContainer title="Amount Distribution" subtitle="Tx count by amount bucket" height={160}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={amountHisto} margin={{ top: 4, right: 4, bottom: 0, left: 0 }}>
              <CartesianGrid {...GRID_PROPS} />
              <XAxis dataKey="label" {...AXIS_PROPS} />
              <YAxis {...AXIS_PROPS} width={36} />
              <Tooltip content={<SharedTooltip />} />
              <Bar dataKey="count" fill={CHART_COLORS.accent} radius={[3, 3, 0, 0]} isAnimationActive={false} />
            </BarChart>
          </ResponsiveContainer>
        </ChartContainer>
        <ChartContainer title="Risk Score Distribution" subtitle="Tx count by risk bucket (0–100)" height={160}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={riskHisto} margin={{ top: 4, right: 4, bottom: 0, left: 0 }}>
              <CartesianGrid {...GRID_PROPS} />
              <XAxis dataKey="label" {...AXIS_PROPS} />
              <YAxis {...AXIS_PROPS} width={36} />
              <Tooltip content={<SharedTooltip />} />
              <Bar dataKey="count" radius={[3, 3, 0, 0]} isAnimationActive={false}>
                {riskHisto.map((entry, i) => (
                  <rect key={i} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartContainer>
      </div>

      {/* Table card */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <div style={{ padding: '14px 14px 10px', borderBottom: '1px solid var(--border-0)' }}>
          {/* "N new" pill */}
          {newCount > 0 && (
            <button
              onClick={flushPending}
              style={{
                display: 'block',
                width: '100%',
                padding: '8px',
                marginBottom: 10,
                background: 'var(--accent-dim)',
                border: '1px dashed var(--accent-muted)',
                borderRadius: 'var(--radius-md)',
                color: 'var(--accent)',
                fontSize: 'var(--text-13)',
                fontWeight: 600,
                cursor: 'pointer',
                textAlign: 'center',
              }}
            >
              ↑ {newCount} new transaction{newCount !== 1 ? 's' : ''} — click to show
            </button>
          )}
          <FilterBar
            searchPlaceholder="Search by ID, customer, merchant, country…"
            searchValue={search}
            onSearchChange={setSearch}
            filters={[
              { key: 'riskLevel', label: 'Risk Level', options: ['critical','high','medium','low','safe'].map(v => ({ value: v, label: v.charAt(0).toUpperCase() + v.slice(1) })) },
              { key: 'status', label: 'Status', options: ['approved','declined','review','flagged'].map(v => ({ value: v, label: v.charAt(0).toUpperCase() + v.slice(1) })) },
            ]}
            activeFilters={activeFilters}
            onFilterChange={(key, vals) => setActiveFilters(prev => ({ ...prev, [key]: vals }))}
            onClearAll={() => { setSearch(''); setActiveFilters({}); }}
            totalCount={allTxs.length}
            filteredCount={filtered.length}
          />
        </div>
        <DataTable
          columns={COLUMNS}
          data={filtered}
          rowKey={(t) => t.id}
          maxHeight={560}
          newRowIds={newRowIds}
          onRowClick={(tx) => setSelectedTx(tx)}
        />
      </div>

      {/* Transaction detail drawer */}
      <Drawer
        open={!!selectedTx}
        onClose={() => setSelectedTx(null)}
        title={selectedTx?.id}
        subtitle={`${selectedTx?.customerName} · ${selectedTx?.merchantName}`}
      >
        {selectedTx && <TxDetail tx={selectedTx} />}
      </Drawer>
    </div>
  );
}

// ── Transaction Detail Content ─────────────────────────────────────────────
function TxDetail({ tx }: { tx: Transaction }) {
  const timelineEvents = [
    { label: 'Transaction received', ts: tx.timestamp, status: 'done' },
    { label: `${tx.rulesFireCount} rules evaluated`, ts: tx.timestamp, status: 'done' },
    { label: `Model scored: ${(tx.modelScore * 100).toFixed(1)}%`, ts: tx.timestamp, status: 'done' },
    { label: `Agent verdict: ${tx.agentVerdict}`, ts: tx.timestamp, status: tx.agentVerdict === 'BLOCK' ? 'error' : 'done' },
    { label: `Final decision: ${tx.status.toUpperCase()}`, ts: tx.timestamp, status: tx.status === 'declined' || tx.status === 'flagged' ? 'error' : 'done' },
  ];

  const fields: [string, string][] = [
    ['Transaction ID', tx.id],
    ['Customer ID', tx.customerId],
    ['Device ID', tx.deviceId],
    ['Amount', `${tx.currency} ${tx.amount.toFixed(2)}`],
    ['Merchant', tx.merchantName],
    ['Category', tx.merchantCategory],
    ['Country', tx.country],
    ['Risk Score', `${tx.riskScore} / 100`],
    ['Model Score', `${(tx.modelScore * 100).toFixed(3)}%`],
    ['Rules Fired', String(tx.rulesFireCount)],
    ['Timestamp', new Date(tx.timestamp).toLocaleString()],
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      {/* Status + Risk */}
      <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
        <RiskBadge level={tx.riskLevel} score={tx.riskScore} />
        <span style={{
          fontSize: 'var(--text-11)', fontFamily: 'var(--font-mono)', fontWeight: 700,
          color: STATUS_COLORS[tx.status], textTransform: 'uppercase',
          letterSpacing: '0.04em', padding: '2px 7px', borderRadius: 9999,
          background: 'var(--surface-3)', border: '1px solid var(--border-2)',
        }}>{tx.status}</span>
      </div>

      {/* Fields grid */}
      <div>
        <div className="text-label" style={{ marginBottom: 8 }}>Transaction Details</div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px 16px' }}>
          {fields.map(([label, value]) => (
            <div key={label} style={{ paddingBottom: 6, borderBottom: '1px solid var(--border-0)' }}>
              <div style={{ fontSize: 10, color: 'var(--gray-600)', fontWeight: 600, letterSpacing: '0.04em', textTransform: 'uppercase', marginBottom: 2 }}>{label}</div>
              <div style={{ fontSize: 'var(--text-12)', color: 'var(--gray-200)', fontFamily: 'var(--font-mono)', wordBreak: 'break-all' }}>{value}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Decision timeline */}
      <div>
        <div className="text-label" style={{ marginBottom: 10 }}>Decision Timeline</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
          {timelineEvents.map((evt, i) => (
            <div key={i} style={{ display: 'flex', gap: 10, alignItems: 'flex-start' }}>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', flexShrink: 0, paddingTop: 2 }}>
                <div style={{
                  width: 10, height: 10, borderRadius: '50%',
                  background: evt.status === 'error' ? 'var(--risk-critical)' : 'var(--status-success)',
                  border: `2px solid ${evt.status === 'error' ? 'var(--risk-critical-dim)' : 'var(--risk-low-dim)'}`,
                  flexShrink: 0,
                }} />
                {i < timelineEvents.length - 1 && (
                  <div style={{ width: 1, flex: 1, minHeight: 20, background: 'var(--border-1)', margin: '4px 0' }} />
                )}
              </div>
              <div style={{ paddingBottom: 10 }}>
                <div style={{ fontSize: 'var(--text-13)', color: 'var(--gray-200)' }}>{evt.label}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
