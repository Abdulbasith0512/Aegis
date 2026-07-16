/**
 * Real-time event stream simulator — pub/sub engine driving live updates
 * across all dashboard pages that display current data.
 */

import type { Transaction, RiskLevel } from './mockData';
import { generateTransaction } from './mockData';

// ── Event Types ────────────────────────────────────────────────────────────

export type EventType =
  | 'new_transaction'
  | 'risk_alert'
  | 'agent_status_change'
  | 'incident_created'
  | 'incident_updated'
  | 'kpi_delta'
  | 'review_case_created'
  | 'connection_status';

export interface StreamEvent<T = unknown> {
  type: EventType;
  payload: T;
  ts: string;
}

export interface RiskAlertPayload {
  transactionId: string;
  customerName: string;
  amount: number;
  riskLevel: RiskLevel;
  reason: string;
}

export interface KpiDeltaPayload {
  field: 'txVolume' | 'fraudRate' | 'approvalRate' | 'agentAccuracy';
  value: number;
  delta: number;
}

export interface AgentStatusPayload {
  agentId: string;
  agentName: string;
  previousStatus: string;
  newStatus: string;
}

export interface ConnectionPayload {
  connected: boolean;
  lastUpdated: string;
}

type Listener = (event: StreamEvent) => void;

// ── Event Stream Class ─────────────────────────────────────────────────────

class EventStream {
  private listeners: Map<EventType | '*', Set<Listener>> = new Map();
  private intervals: ReturnType<typeof setInterval>[] = [];
  private _connected = true;

  get connected(): boolean {
    return this._connected;
  }

  on(type: EventType | '*', listener: Listener): () => void {
    if (!this.listeners.has(type)) {
      this.listeners.set(type, new Set());
    }
    this.listeners.get(type)!.add(listener);

    // Return unsubscribe function
    return () => {
      this.listeners.get(type)?.delete(listener);
    };
  }

  private emit<T>(type: EventType, payload: T): void {
    const event: StreamEvent<T> = { type, payload, ts: new Date().toISOString() };

    // Notify specific type listeners
    this.listeners.get(type)?.forEach(l => l(event as StreamEvent));

    // Notify wildcard listeners
    this.listeners.get('*')?.forEach(l => l(event as StreamEvent));
  }

  start(): void {
    this._connected = true;
    this.emit<ConnectionPayload>('connection_status', { connected: true, lastUpdated: new Date().toISOString() });

    // ── New transactions every 2–4 seconds ──────────────────────────────
    const txInterval = setInterval(() => {
      if (!this._connected) return;
      const tx: Transaction = generateTransaction({ isNew: true });
      this.emit<Transaction>('new_transaction', tx);

      // High-risk transactions also emit a risk alert
      if (tx.riskLevel === 'critical' || tx.riskLevel === 'high') {
        const reasons = [
          'Unusual transaction velocity',
          'Device fingerprint mismatch',
          'New payment instrument',
          'Geographic anomaly detected',
          'Pattern matches known fraud ring',
        ];
        this.emit<RiskAlertPayload>('risk_alert', {
          transactionId: tx.id,
          customerName: tx.customerName,
          amount: tx.amount,
          riskLevel: tx.riskLevel,
          reason: reasons[Math.floor(Math.random() * reasons.length)],
        });
      }
    }, 2500 + Math.random() * 1500);

    // ── KPI deltas every 8 seconds ──────────────────────────────────────
    const kpiInterval = setInterval(() => {
      if (!this._connected) return;
      const fields: KpiDeltaPayload['field'][] = ['txVolume', 'fraudRate', 'approvalRate', 'agentAccuracy'];
      const field = fields[Math.floor(Math.random() * fields.length)];
      const delta = (Math.random() - 0.5) * (field === 'txVolume' ? 200 : 0.5);
      this.emit<KpiDeltaPayload>('kpi_delta', {
        field,
        value: field === 'txVolume' ? 60000 + delta : field === 'fraudRate' ? 1.8 + delta : 96 + delta,
        delta: parseFloat(delta.toFixed(2)),
      });
    }, 8000);

    // ── Agent status changes every 30 seconds ───────────────────────────
    const agentInterval = setInterval(() => {
      if (!this._connected || Math.random() > 0.3) return;
      const agents = ['FraudShield-v2', 'AMLSensor-v1', 'VelocityGuard'];
      const statuses = ['healthy', 'degraded'];
      this.emit<AgentStatusPayload>('agent_status_change', {
        agentId: `AGT_${Math.random().toString(36).slice(2, 8).toUpperCase()}`,
        agentName: agents[Math.floor(Math.random() * agents.length)],
        previousStatus: 'healthy',
        newStatus: statuses[Math.floor(Math.random() * statuses.length)],
      });
    }, 30000);

    // ── Heartbeat / last-updated ticker every 5 seconds ─────────────────
    const heartbeatInterval = setInterval(() => {
      this.emit<ConnectionPayload>('connection_status', {
        connected: this._connected,
        lastUpdated: new Date().toISOString(),
      });
    }, 5000);

    this.intervals.push(txInterval, kpiInterval, agentInterval, heartbeatInterval);
  }

  stop(): void {
    this._connected = false;
    this.intervals.forEach(clearInterval);
    this.intervals = [];
    this.emit<ConnectionPayload>('connection_status', { connected: false, lastUpdated: new Date().toISOString() });
  }
}

// Singleton instance
export const eventStream = new EventStream();
