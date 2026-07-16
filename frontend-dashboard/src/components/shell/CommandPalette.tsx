import React, { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUiStore } from '@/store/uiStore';
import {
  LayoutDashboard, ArrowLeftRight, Users, Bot, ShieldCheck,
  Lightbulb, FileText, ClipboardList, Zap, AlertTriangle,
  BarChart3, Network, Settings, Activity, Search, X,
} from 'lucide-react';

interface CmdItem {
  label: string;
  description: string;
  to: string;
  icon: React.ElementType;
}

const CMDK_ITEMS: CmdItem[] = [
  { label: 'Overview', description: 'Executive KPI dashboard', to: '/', icon: LayoutDashboard },
  { label: 'Transactions', description: 'High-density transaction table', to: '/transactions', icon: ArrowLeftRight },
  { label: 'Customers', description: 'Customer profiles and risk', to: '/customers', icon: Users },
  { label: 'Agents', description: 'ML model registry and health', to: '/agents', icon: Bot },
  { label: 'Trust Center', description: 'SLA and system health', to: '/trust', icon: ShieldCheck },
  { label: 'Explainability', description: 'Per-decision feature attribution', to: '/explainability', icon: Lightbulb },
  { label: 'Policies', description: 'Rule and policy management', to: '/policies', icon: FileText },
  { label: 'Human Reviews', description: 'Review queue and case management', to: '/reviews', icon: ClipboardList },
  { label: 'Chaos Engineering', description: 'Fault injection experiments', to: '/chaos', icon: Zap },
  { label: 'Incidents', description: 'Incident timeline and war room', to: '/incidents', icon: Activity },
  { label: 'Analytics', description: 'Flexible chart exploration', to: '/analytics', icon: BarChart3 },
  { label: 'Knowledge Graph', description: 'Entity relationship graph', to: '/knowledge-graph', icon: Network },
  { label: 'Settings', description: 'Org, API keys, preferences', to: '/settings', icon: Settings },
];

export const CommandPalette: React.FC = () => {
  const { commandPaletteOpen, setCommandPaletteOpen } = useUiStore();
  const [query, setQuery] = useState('');
  const [selected, setSelected] = useState(0);
  const navigate = useNavigate();
  const inputRef = useRef<HTMLInputElement>(null);

  const filtered = query.trim()
    ? CMDK_ITEMS.filter(
        (item) =>
          item.label.toLowerCase().includes(query.toLowerCase()) ||
          item.description.toLowerCase().includes(query.toLowerCase()),
      )
    : CMDK_ITEMS;

  useEffect(() => {
    if (commandPaletteOpen) {
      setTimeout(() => inputRef.current?.focus(), 50);
      setQuery('');
      setSelected(0);
    }
  }, [commandPaletteOpen]);

  useEffect(() => {
    setSelected(0);
  }, [query]);

  // Global keyboard shortcut
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setCommandPaletteOpen(true);
      }
      if (e.key === 'Escape') setCommandPaletteOpen(false);
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [setCommandPaletteOpen]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelected((s) => Math.min(s + 1, filtered.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelected((s) => Math.max(s - 1, 0));
    } else if (e.key === 'Enter') {
      if (filtered[selected]) {
        navigate(filtered[selected].to);
        setCommandPaletteOpen(false);
      }
    }
  };

  if (!commandPaletteOpen) return null;

  return (
    <div className="cmdk-overlay" onClick={() => setCommandPaletteOpen(false)}>
      <div className="cmdk-panel" onClick={(e) => e.stopPropagation()}>
        {/* Search input */}
        <div
          style={{
            display: 'flex', alignItems: 'center', gap: 10,
            padding: '12px 16px', borderBottom: '1px solid var(--border-1)',
          }}
        >
          <Search size={15} color="var(--gray-500)" />
          <input
            ref={inputRef}
            className="input"
            style={{
              border: 'none', background: 'transparent',
              fontSize: 'var(--text-14)', padding: 0,
            }}
            placeholder="Search pages and actions…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
          />
          {query && (
            <button className="btn btn-ghost btn-icon" onClick={() => setQuery('')}>
              <X size={13} />
            </button>
          )}
        </div>

        {/* Results */}
        <div style={{ maxHeight: 380, overflowY: 'auto', padding: '6px' }}>
          {filtered.length === 0 ? (
            <div style={{ padding: '24px', textAlign: 'center', color: 'var(--gray-500)', fontSize: 'var(--text-13)' }}>
              No results for "{query}"
            </div>
          ) : (
            filtered.map((item, idx) => (
              <button
                key={item.to}
                className="btn btn-ghost"
                style={{
                  width: '100%', justifyContent: 'flex-start',
                  gap: 12, padding: '9px 10px', borderRadius: 'var(--radius-md)',
                  background: idx === selected ? 'var(--surface-4)' : 'transparent',
                }}
                onClick={() => {
                  navigate(item.to);
                  setCommandPaletteOpen(false);
                }}
                onMouseEnter={() => setSelected(idx)}
              >
                <div
                  style={{
                    width: 30, height: 30, borderRadius: 'var(--radius-md)',
                    background: 'var(--surface-3)', border: '1px solid var(--border-1)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
                  }}
                >
                  <item.icon size={14} color="var(--gray-400)" />
                </div>
                <div style={{ textAlign: 'left' }}>
                  <div style={{ fontSize: 'var(--text-14)', fontWeight: 500, color: 'var(--gray-100)' }}>
                    {item.label}
                  </div>
                  <div style={{ fontSize: 'var(--text-12)', color: 'var(--gray-500)' }}>
                    {item.description}
                  </div>
                </div>
                {idx === selected && (
                  <div style={{ marginLeft: 'auto' }}>
                    <kbd style={{
                      fontSize: 10, fontFamily: 'var(--font-mono)',
                      background: 'var(--surface-3)', border: '1px solid var(--border-2)',
                      borderRadius: 4, padding: '2px 6px', color: 'var(--gray-400)',
                    }}>↵</kbd>
                  </div>
                )}
              </button>
            ))
          )}
        </div>

        {/* Footer */}
        <div
          style={{
            display: 'flex', gap: 12, padding: '8px 16px',
            borderTop: '1px solid var(--border-0)',
            fontSize: 'var(--text-11)', color: 'var(--gray-600)', fontFamily: 'var(--font-mono)',
          }}
        >
          <span>↑↓ navigate</span>
          <span>↵ open</span>
          <span>esc close</span>
        </div>
      </div>
    </div>
  );
};
