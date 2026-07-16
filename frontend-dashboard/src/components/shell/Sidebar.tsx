import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard, ArrowLeftRight, Users, Bot, ShieldCheck,
  Lightbulb, FileText, ClipboardList, Zap, AlertTriangle,
  BarChart3, Network, Settings, ChevronLeft, ChevronRight,
  Activity,
} from 'lucide-react';
import { useUiStore } from '@/store/uiStore';

interface NavItem {
  to: string;
  label: string;
  icon: React.ElementType;
}

interface NavSection {
  title: string;
  items: NavItem[];
}

const NAV_SECTIONS: NavSection[] = [
  {
    title: 'Monitoring',
    items: [
      { to: '/', label: 'Overview', icon: LayoutDashboard },
      { to: '/incidents', label: 'Incidents', icon: Activity },
    ],
  },
  {
    title: 'Trust & Safety',
    items: [
      { to: '/trust', label: 'Trust Center', icon: ShieldCheck },
      { to: '/policies', label: 'Policies', icon: FileText },
    ],
  },
  {
    title: 'Operations',
    items: [
      { to: '/transactions', label: 'Transactions', icon: ArrowLeftRight },
      { to: '/customers', label: 'Customers', icon: Users },
      { to: '/reviews', label: 'Human Reviews', icon: ClipboardList },
    ],
  },
  {
    title: 'Intelligence',
    items: [
      { to: '/agents', label: 'Agents', icon: Bot },
      { to: '/explainability', label: 'Explainability', icon: Lightbulb },
      { to: '/analytics', label: 'Analytics', icon: BarChart3 },
    ],
  },
  {
    title: 'Engineering',
    items: [
      { to: '/chaos', label: 'Chaos Engineering', icon: Zap },
      { to: '/knowledge-graph', label: 'Knowledge Graph', icon: Network },
    ],
  },
  {
    title: 'Admin',
    items: [
      { to: '/settings', label: 'Settings', icon: Settings },
    ],
  },
];

export const Sidebar: React.FC = () => {
  const { sidebarCollapsed, toggleSidebar } = useUiStore();

  return (
    <nav className={`sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}>
      {/* Logo + collapse toggle */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: sidebarCollapsed ? 'center' : 'space-between',
          padding: '14px 12px',
          borderBottom: '1px solid var(--border-0)',
          flexShrink: 0,
        }}
      >
        {!sidebarCollapsed && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <div
              style={{
                width: 26,
                height: 26,
                borderRadius: 6,
                background: 'var(--accent-dim)',
                border: '1px solid var(--accent-muted)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
              }}
            >
              <ShieldCheck size={14} color="var(--accent)" />
            </div>
            <span
              style={{
                fontSize: 'var(--text-14)',
                fontWeight: 700,
                color: 'var(--gray-100)',
                letterSpacing: '-0.01em',
              }}
            >
              AegisAI
            </span>
            <span
              style={{
                fontSize: 'var(--text-11)',
                fontWeight: 600,
                color: 'var(--gray-500)',
                background: 'var(--surface-3)',
                padding: '1px 6px',
                borderRadius: 9999,
                fontFamily: 'var(--font-mono)',
              }}
            >
              OPS
            </span>
          </div>
        )}
        {sidebarCollapsed && (
          <div
            style={{
              width: 26, height: 26, borderRadius: 6,
              background: 'var(--accent-dim)', border: '1px solid var(--accent-muted)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}
          >
            <ShieldCheck size={14} color="var(--accent)" />
          </div>
        )}
        <button
          onClick={toggleSidebar}
          className="btn btn-ghost btn-icon"
          aria-label={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          style={{ marginLeft: sidebarCollapsed ? 0 : 4, display: sidebarCollapsed ? 'none' : 'flex' }}
        >
          <ChevronLeft size={14} />
        </button>
      </div>

      {/* Nav sections */}
      <div style={{ flex: 1, overflowY: 'auto', overflowX: 'hidden', padding: '8px 8px' }}>
        {NAV_SECTIONS.map((section) => (
          <div key={section.title} style={{ marginBottom: 4 }}>
            {!sidebarCollapsed && (
              <div className="nav-section-label">{section.title}</div>
            )}
            {section.items.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === '/'}
                className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
                title={sidebarCollapsed ? item.label : undefined}
              >
                <item.icon size={15} strokeWidth={1.75} style={{ flexShrink: 0 }} />
                {!sidebarCollapsed && <span>{item.label}</span>}
              </NavLink>
            ))}
          </div>
        ))}
      </div>

      {/* Expand button when collapsed */}
      {sidebarCollapsed && (
        <div style={{ padding: '8px', borderTop: '1px solid var(--border-0)' }}>
          <button
            onClick={toggleSidebar}
            className="btn btn-ghost btn-icon"
            style={{ width: '100%', justifyContent: 'center' }}
            aria-label="Expand sidebar"
          >
            <ChevronRight size={14} />
          </button>
        </div>
      )}
    </nav>
  );
};
