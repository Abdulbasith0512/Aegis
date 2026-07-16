import React, { useEffect, useRef } from 'react';
import { X } from 'lucide-react';

interface DrawerProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  subtitle?: string;
  children: React.ReactNode;
  width?: number | string;
}

export const Drawer: React.FC<DrawerProps> = ({
  open,
  onClose,
  title,
  subtitle,
  children,
  width = 580,
}) => {
  // Escape to close
  useEffect(() => {
    if (!open) return;
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <>
      {/* Overlay */}
      <div className="drawer-overlay" onClick={onClose} />

      {/* Panel */}
      <div
        className="drawer-panel"
        style={{ width: `min(${typeof width === 'number' ? `${width}px` : width}, 90vw)` }}
      >
        {/* Header */}
        {(title || subtitle) && (
          <div
            style={{
              display: 'flex',
              alignItems: 'flex-start',
              justifyContent: 'space-between',
              padding: '16px 20px',
              borderBottom: '1px solid var(--border-1)',
              flexShrink: 0,
            }}
          >
            <div>
              {title && (
                <div
                  style={{
                    fontSize: 'var(--text-16)',
                    fontWeight: 600,
                    color: 'var(--gray-50)',
                  }}
                >
                  {title}
                </div>
              )}
              {subtitle && (
                <div
                  style={{
                    fontSize: 'var(--text-12)',
                    color: 'var(--gray-500)',
                    marginTop: 2,
                    fontFamily: 'var(--font-mono)',
                  }}
                >
                  {subtitle}
                </div>
              )}
            </div>
            <button className="btn btn-ghost btn-icon" onClick={onClose}>
              <X size={15} />
            </button>
          </div>
        )}

        {/* Scrollable content */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '20px' }}>
          {children}
        </div>
      </div>
    </>
  );
};
