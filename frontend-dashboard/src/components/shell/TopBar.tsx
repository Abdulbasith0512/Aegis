import React, { useEffect, useState, useCallback } from 'react';
import { Search, Bell, Sun, Moon, Server, ChevronDown, X, LogOut, Settings, User as UserIcon } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useUiStore } from '@/store/uiStore';
import { eventStream } from '@/lib/eventStream';
import type { StreamEvent, RiskAlertPayload } from '@/lib/eventStream';

const ENVS = ['production', 'staging', 'sandbox'] as const;
type Env = typeof ENVS[number];

interface NotificationItem {
  id: string;
  title: string;
  message: string;
  ts: string;
  read: boolean;
}

export const TopBar: React.FC = () => {
  const {
    theme, toggleTheme,
    setCommandPaletteOpen,
    wsConnected, lastUpdated,
    notificationCount, clearNotifications, incrementNotifications,
  } = useUiStore();

  const navigate = useNavigate();

  const [env, setEnv] = useState<Env>('production');
  const [envOpen, setEnvOpen] = useState(false);
  const [notifOpen, setNotifOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);

  // Relative time helper
  const [relTime, setRelTime] = useState('');
  useEffect(() => {
    if (!lastUpdated) return;
    const update = () => {
      const seconds = Math.round((Date.now() - new Date(lastUpdated).getTime()) / 1000);
      setRelTime(seconds < 5 ? 'just now' : `${seconds}s ago`);
    };
    update();
    const interval = setInterval(update, 1000);
    return () => clearInterval(interval);
  }, [lastUpdated]);

  // Collect notifications from risk alerts
  useEffect(() => {
    const unsub = eventStream.on('risk_alert', (e: StreamEvent) => {
      const p = e.payload as RiskAlertPayload;
      const item: NotificationItem = {
        id: `notif-${Date.now()}-${Math.random()}`,
        title: p.riskLevel === 'critical' ? '🚨 Critical Risk' : '⚠️ High Risk',
        message: `${p.customerName} — $${p.amount.toFixed(2)} · ${p.reason}`,
        ts: new Date().toLocaleTimeString(),
        read: false,
      };
      setNotifications(prev => [item, ...prev].slice(0, 50));
    });
    return unsub;
  }, []);

  const markAllRead = useCallback(() => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
    clearNotifications();
  }, [clearNotifications]);

  const dismissNotif = useCallback((id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  }, []);

  // Close dropdowns when clicking outside
  useEffect(() => {
    if (!envOpen && !notifOpen && !userMenuOpen) return;
    const handler = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (!target.closest('[data-dropdown]')) {
        setEnvOpen(false);
        setNotifOpen(false);
        setUserMenuOpen(false);
      }
    };
    document.addEventListener('click', handler);
    return () => document.removeEventListener('click', handler);
  }, [envOpen, notifOpen, userMenuOpen]);

  const envColors: Record<Env, string> = {
    production: 'var(--risk-critical)',
    staging: 'var(--risk-medium)',
    sandbox: 'var(--risk-safe)',
  };

  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <header className="topbar">
      {/* Search / cmd+k trigger */}
      <button
        className="btn btn-outline"
        style={{ flex: 1, maxWidth: 280, justifyContent: 'space-between', gap: 8 }}
        onClick={() => setCommandPaletteOpen(true)}
        aria-label="Open command palette"
      >
        <span style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--gray-500)', fontSize: 'var(--text-13)' }}>
          <Search size={13} />
          Search or jump to…
        </span>
        <kbd
          style={{
            fontSize: 10, fontFamily: 'var(--font-mono)',
            background: 'var(--surface-3)', border: '1px solid var(--border-2)',
            borderRadius: 4, padding: '1px 5px', color: 'var(--gray-400)',
          }}
        >
          ⌘K
        </kbd>
      </button>

      {/* Spacer */}
      <div style={{ flex: 1 }} />

      {/* Environment switcher */}
      <div style={{ position: 'relative' }} data-dropdown>
        <button
          className="btn btn-outline"
          onClick={(e) => { e.stopPropagation(); setEnvOpen(o => !o); setNotifOpen(false); setUserMenuOpen(false); }}
          style={{ gap: 6 }}
        >
          <span
            style={{
              width: 7, height: 7, borderRadius: '50%',
              background: envColors[env], flexShrink: 0,
            }}
          />
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--text-12)', fontWeight: 600 }}>
            {env}
          </span>
          <ChevronDown size={12} />
        </button>
        {envOpen && (
          <div
            style={{
              position: 'absolute', top: 'calc(100% + 6px)', right: 0,
              background: 'var(--surface-3)', border: '1px solid var(--border-2)',
              borderRadius: 'var(--radius-md)', overflow: 'hidden', zIndex: 50,
              minWidth: 130, boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
            }}
          >
            {ENVS.map((e) => (
              <button
                key={e}
                className="btn btn-ghost"
                style={{
                  width: '100%', justifyContent: 'flex-start', borderRadius: 0,
                  gap: 8, padding: '7px 12px',
                  background: e === env ? 'var(--surface-4)' : 'transparent',
                }}
                onClick={() => { setEnv(e); setEnvOpen(false); }}
              >
                <span style={{ width: 7, height: 7, borderRadius: '50%', background: envColors[e] }} />
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--text-12)' }}>{e}</span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Live connection indicator */}
      <div
        style={{
          display: 'flex', alignItems: 'center', gap: 6,
          padding: '4px 10px', borderRadius: 'var(--radius-md)',
          background: 'var(--surface-2)', border: '1px solid var(--border-1)',
          fontSize: 'var(--text-12)', fontFamily: 'var(--font-mono)',
          color: wsConnected ? 'var(--risk-low-text)' : 'var(--risk-critical-text)',
        }}
        title={wsConnected ? `Live — updated ${relTime}` : 'Disconnected'}
      >
        <span
          style={{
            width: 7, height: 7, borderRadius: '50%',
            background: wsConnected ? 'var(--status-success)' : 'var(--risk-critical)',
            animation: wsConnected ? 'live-pulse 2s ease-in-out infinite' : 'none',
          }}
        />
        <Server size={11} />
        <span>{wsConnected ? `live · ${relTime}` : 'disconnected'}</span>
      </div>

      {/* ── Notifications dropdown ── */}
      <div style={{ position: 'relative' }} data-dropdown>
        <button
          className="btn btn-ghost btn-icon"
          onClick={(e) => { e.stopPropagation(); setNotifOpen(o => !o); setEnvOpen(false); setUserMenuOpen(false); }}
          style={{ position: 'relative' }}
          aria-label="Notifications"
        >
          <Bell size={15} />
          {unreadCount > 0 && (
            <span
              style={{
                position: 'absolute', top: 2, right: 2,
                minWidth: 16, height: 16, borderRadius: 9999,
                background: 'var(--risk-critical)',
                fontSize: 9, fontWeight: 700, color: 'white',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontFamily: 'var(--font-mono)', padding: '0 3px',
                lineHeight: 1,
              }}
            >
              {unreadCount > 99 ? '99+' : unreadCount}
            </span>
          )}
        </button>
        {notifOpen && (
          <div
            style={{
              position: 'absolute', top: 'calc(100% + 6px)', right: 0,
              width: 360, maxHeight: 420,
              background: 'var(--surface-2)', border: '1px solid var(--border-2)',
              borderRadius: 'var(--radius-lg)', overflow: 'hidden', zIndex: 50,
              boxShadow: '0 12px 48px rgba(0,0,0,0.5)',
              display: 'flex', flexDirection: 'column',
            }}
          >
            {/* Header */}
            <div style={{
              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              padding: '12px 14px', borderBottom: '1px solid var(--border-1)', flexShrink: 0,
            }}>
              <span style={{ fontSize: 'var(--text-14)', fontWeight: 600, color: 'var(--gray-100)' }}>
                Notifications
              </span>
              {unreadCount > 0 && (
                <button
                  className="btn btn-ghost"
                  style={{ fontSize: 11, color: 'var(--accent)', padding: '2px 6px' }}
                  onClick={markAllRead}
                >
                  Mark all read
                </button>
              )}
            </div>
            {/* List */}
            <div style={{ flex: 1, overflowY: 'auto' }}>
              {notifications.length === 0 ? (
                <div style={{ padding: '32px 16px', textAlign: 'center', color: 'var(--gray-500)', fontSize: 'var(--text-13)' }}>
                  No notifications yet
                </div>
              ) : (
                notifications.slice(0, 20).map(n => (
                  <div
                    key={n.id}
                    style={{
                      display: 'flex', gap: 10, padding: '10px 14px',
                      borderBottom: '1px solid var(--border-0)',
                      background: n.read ? 'transparent' : 'var(--accent-dim)',
                    }}
                  >
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontSize: 'var(--text-13)', fontWeight: n.read ? 400 : 600, color: 'var(--gray-100)', marginBottom: 2 }}>
                        {n.title}
                      </div>
                      <div style={{ fontSize: 'var(--text-12)', color: 'var(--gray-400)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {n.message}
                      </div>
                      <div style={{ fontSize: 10, color: 'var(--gray-600)', fontFamily: 'var(--font-mono)', marginTop: 3 }}>
                        {n.ts}
                      </div>
                    </div>
                    <button
                      className="btn btn-ghost btn-icon"
                      style={{ flexShrink: 0, padding: 2, alignSelf: 'flex-start' }}
                      onClick={(e) => { e.stopPropagation(); dismissNotif(n.id); }}
                    >
                      <X size={11} />
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>
        )}
      </div>

      {/* Theme toggle */}
      <button className="btn btn-ghost btn-icon" onClick={toggleTheme} aria-label="Toggle theme">
        {theme === 'dark' ? <Sun size={15} /> : <Moon size={15} />}
      </button>

      {/* ── User menu dropdown ── */}
      <div style={{ position: 'relative' }} data-dropdown>
        <button
          className="btn btn-ghost"
          style={{ gap: 8, padding: '4px 8px' }}
          aria-label="User menu"
          onClick={(e) => { e.stopPropagation(); setUserMenuOpen(o => !o); setEnvOpen(false); setNotifOpen(false); }}
        >
          <div
            style={{
              width: 26, height: 26, borderRadius: '50%',
              background: 'linear-gradient(135deg, var(--accent-dim), var(--surface-4))',
              border: '1px solid var(--accent-muted)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 11, fontWeight: 700, color: 'var(--accent)',
              fontFamily: 'var(--font-mono)',
            }}
          >
            RJ
          </div>
          <div style={{ textAlign: 'left', lineHeight: 1.3 }}>
            <div style={{ fontSize: 'var(--text-13)', fontWeight: 500, color: 'var(--gray-200)' }}>analyst_rj</div>
            <div style={{ fontSize: 'var(--text-11)', color: 'var(--gray-500)' }}>Risk Analyst</div>
          </div>
          <ChevronDown size={11} style={{ color: 'var(--gray-500)' }} />
        </button>
        {userMenuOpen && (
          <div
            style={{
              position: 'absolute', top: 'calc(100% + 6px)', right: 0,
              width: 200,
              background: 'var(--surface-3)', border: '1px solid var(--border-2)',
              borderRadius: 'var(--radius-md)', overflow: 'hidden', zIndex: 50,
              boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
            }}
          >
            {/* Profile info */}
            <div style={{ padding: '10px 12px', borderBottom: '1px solid var(--border-1)' }}>
              <div style={{ fontSize: 'var(--text-13)', fontWeight: 600, color: 'var(--gray-100)' }}>Rachel Johnson</div>
              <div style={{ fontSize: 'var(--text-12)', color: 'var(--gray-500)' }}>rj@aegisai.io</div>
            </div>
            <button
              className="btn btn-ghost"
              style={{ width: '100%', justifyContent: 'flex-start', borderRadius: 0, gap: 8, padding: '8px 12px' }}
              onClick={() => { navigate('/settings'); setUserMenuOpen(false); }}
            >
              <Settings size={13} /> Settings
            </button>
            <button
              className="btn btn-ghost"
              style={{ width: '100%', justifyContent: 'flex-start', borderRadius: 0, gap: 8, padding: '8px 12px' }}
              onClick={() => { navigate('/'); setUserMenuOpen(false); }}
            >
              <UserIcon size={13} /> Profile
            </button>
            <div style={{ borderTop: '1px solid var(--border-1)' }}>
              <button
                className="btn btn-ghost"
                style={{ width: '100%', justifyContent: 'flex-start', borderRadius: 0, gap: 8, padding: '8px 12px', color: 'var(--risk-critical-text)' }}
                onClick={() => { setUserMenuOpen(false); alert('Logged out (demo)'); }}
              >
                <LogOut size={13} /> Sign out
              </button>
            </div>
          </div>
        )}
      </div>
    </header>
  );
};
