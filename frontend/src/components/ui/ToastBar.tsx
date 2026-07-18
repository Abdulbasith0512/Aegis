"use client";

import React, { useEffect } from "react";
import { CheckCircle, XCircle, X } from "lucide-react";

export interface Toast {
  id: string;
  type: "success" | "error" | "info" | string;
  message: string;
}

interface ToastBarProps {
  toasts: Toast[];
  onDismiss: (id: string) => void;
}

export function ToastBar({ toasts, onDismiss }: ToastBarProps) {
  useEffect(() => {
    if (toasts.length > 0) {
      const timer = setTimeout(() => {
        onDismiss(toasts[0].id);
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [toasts, onDismiss]);

  if (toasts.length === 0) return null;

  return (
    <div style={{
      position: "fixed",
      bottom: 24,
      right: 24,
      display: "flex",
      flexDirection: "column",
      gap: 12,
      zIndex: 9999,
    }}>
      {toasts.map((toast) => (
        <div key={toast.id} style={{
          background: "var(--surface-1)",
          border: "1px solid var(--border-1)",
          borderRadius: "var(--radius-md)",
          padding: "12px 16px",
          display: "flex",
          alignItems: "center",
          gap: 12,
          boxShadow: "0 4px 12px rgba(0,0,0,0.2)",
          minWidth: 300,
        }}>
          {toast.type === "success" && <CheckCircle size={18} color="#22c55e" />}
          {toast.type === "error" && <XCircle size={18} color="#ef4444" />}
          
          <span style={{ fontSize: 13, color: "var(--text-1)", flex: 1 }}>
            {toast.message}
          </span>
          
          <button 
            onClick={() => onDismiss(toast.id)}
            style={{
              background: "none",
              border: "none",
              color: "var(--text-3)",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <X size={14} />
          </button>
        </div>
      ))}
    </div>
  );
}
