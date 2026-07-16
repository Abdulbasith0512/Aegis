import React, { useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { TopBar } from './TopBar';
import { CommandPalette } from './CommandPalette';
import { useUiStore } from '@/store/uiStore';
import { eventStream } from '@/lib/eventStream';
import type { StreamEvent, ConnectionPayload, RiskAlertPayload } from '@/lib/eventStream';
import { ToastManager } from '@/components/ui/ToastManager';

export const AppLayout: React.FC = () => {
  const { setConnectionStatus, incrementNotifications } = useUiStore();

  useEffect(() => {
    // Start the event stream
    eventStream.start();

    // Track connection status
    const unsubConn = eventStream.on('connection_status', (e: StreamEvent) => {
      const p = e.payload as ConnectionPayload;
      setConnectionStatus(p.connected, p.lastUpdated);
    });

    // Increment notification badge on risk alerts
    const unsubAlert = eventStream.on('risk_alert', (_e: StreamEvent) => {
      incrementNotifications();
    });

    return () => {
      unsubConn();
      unsubAlert();
      eventStream.stop();
    };
  }, [setConnectionStatus, incrementNotifications]);

  return (
    <div className="app-shell">
      <Sidebar />
      <div className="app-main">
        <TopBar />
        <main className="page-content">
          <Outlet />
        </main>
      </div>
      <CommandPalette />
      <ToastManager />
    </div>
  );
};
