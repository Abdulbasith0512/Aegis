/**
 * Realistic mock data generators for the AegisAI enterprise dashboard.
 * Generates 1000+ rows of convincing transactions, customers, agents, incidents, etc.
 */

// ── Helpers ────────────────────────────────────────────────────────────────

function randomBetween(min: number, max: number): number {
  return Math.random() * (max - min) + min;
}

function randomInt(min: number, max: number): number {
  return Math.floor(randomBetween(min, max));
}

function pick<T>(arr: T[]): T {
  return arr[randomInt(0, arr.length)];
}

function generateId(prefix: string): string {
  return `${prefix}_${Math.random().toString(36).slice(2, 10).toUpperCase()}`;
}

function pastDate(maxDaysAgo: number): Date {
  const d = new Date();
  d.setTime(d.getTime() - randomBetween(0, maxDaysAgo * 86400000));
  return d;
}

function formatTs(d: Date): string {
  return d.toISOString();
}

// ── Types ──────────────────────────────────────────────────────────────────

export type RiskLevel = 'critical' | 'high' | 'medium' | 'low' | 'safe';
export type TxStatus = 'approved' | 'declined' | 'review' | 'flagged';
export type AgentStatus = 'healthy' | 'degraded' | 'offline';

export interface Transaction {
  id: string;
  customerId: string;
  customerName: string;
  merchantName: string;
  merchantCategory: string;
  amount: number;
  currency: string;
  riskScore: number;
  riskLevel: RiskLevel;
  status: TxStatus;
  agentVerdict: string;
  rulesFireCount: number;
  modelScore: number;
  deviceId: string;
  country: string;
  timestamp: string;
  isNew?: boolean;
}

export interface Customer {
  id: string;
  name: string;
  email: string;
  country: string;
  riskLevel: RiskLevel;
  riskScore: number;
  txCount: number;
  lifetimeValue: number;
  flaggedCount: number;
  joinedAt: string;
  lastSeenAt: string;
  devices: number;
  paymentMethods: number;
}

export interface Agent {
  id: string;
  name: string;
  version: string;
  status: AgentStatus;
  accuracy: number;
  precision: number;
  recall: number;
  trafficPct: number;
  requestsPerMin: number;
  latencyMs: number;
  driftScore: number;
  deployedAt: string;
  lastUpdatedAt: string;
  accuracyHistory: { ts: string; value: number }[];
}

export interface Incident {
  id: string;
  title: string;
  severity: RiskLevel;
  status: 'open' | 'investigating' | 'resolved' | 'postmortem';
  affectedServices: string[];
  startedAt: string;
  resolvedAt?: string;
  mttrMinutes?: number;
  updates: { ts: string; message: string }[];
}

export interface ReviewCase {
  id: string;
  transactionId: string;
  customerId: string;
  customerName: string;
  amount: number;
  riskScore: number;
  riskLevel: RiskLevel;
  reason: string;
  assignedTo: string;
  status: 'pending' | 'in_review' | 'approved' | 'rejected' | 'escalated';
  slaDeadline: string;
  createdAt: string;
}

export interface KpiSnapshot {
  txVolume: number;
  txVolumeDelta: number;
  fraudRate: number;
  fraudRateDelta: number;
  approvalRate: number;
  approvalRateDelta: number;
  activeIncidents: number;
  agentAccuracy: number;
  agentAccuracyDelta: number;
}

export interface ChartPoint {
  ts: string;
  value: number;
  label?: string;
}

// ── Constants ─────────────────────────────────────────────────────────────

const FIRST_NAMES = ['Alice', 'Bob', 'Carol', 'David', 'Elena', 'Frank', 'Grace', 'Henry', 'Isabel', 'James', 'Kate', 'Liam', 'Maria', 'Noah', 'Olivia', 'Peter', 'Quinn', 'Rachel', 'Sam', 'Tara', 'Uma', 'Victor', 'Wendy', 'Xander', 'Yara', 'Zoe'];
const LAST_NAMES = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Wilson', 'Moore', 'Taylor', 'Anderson', 'Thomas', 'Jackson', 'White', 'Harris', 'Martin', 'Thompson', 'Lee', 'Patel'];
const MERCHANTS = ['Amazon', 'Stripe', 'PayPal', 'Binance', 'Coinbase', 'Shopify', 'Uber', 'Airbnb', 'Netflix', 'DoorDash', 'Venmo', 'Cash App', 'Revolut', 'Wise', 'Klarna', 'Rapyd', 'Checkout.com', 'Adyen'];
const MERCHANT_CATS = ['E-Commerce', 'Crypto', 'Travel', 'Food & Beverage', 'Entertainment', 'Financial Services', 'Retail', 'SaaS'];
const COUNTRIES = ['US', 'GB', 'DE', 'IN', 'SG', 'BR', 'NG', 'AU', 'CA', 'FR', 'JP', 'KR', 'ZA', 'AE'];
const CURRENCIES = ['USD', 'EUR', 'GBP', 'INR', 'SGD', 'BRL'];
const AGENT_NAMES = ['FraudShield-v2', 'AMLSensor-v1', 'VelocityGuard', 'DeviceTrust', 'BehaviorAI', 'IdentityVerify'];
const REVIEW_REASONS = ['Unusual location', 'High velocity', 'New device', 'Large amount', 'Pattern match: structuring', 'Card testing detected', 'Account takeover signal', 'Synthetic identity flag'];
const REVIEWER_NAMES = ['analyst_rj', 'analyst_pk', 'senior_ml', 'analyst_tt', 'lead_compliance'];
const SERVICES = ['transaction-processor', 'fraud-engine', 'ml-inference', 'rule-eval', 'identity-svc', 'payment-gateway', 'audit-ledger', 'notification-svc'];
const INCIDENT_TITLES = ['ML Inference Latency Spike', 'Rule Engine Timeout Loop', 'Identity Service 502s', 'Payment Gateway Degraded', 'Fraud Model Drift Detected', 'Database Connection Pool Exhausted'];

function getRiskLevel(score: number): RiskLevel {
  if (score >= 85) return 'critical';
  if (score >= 65) return 'high';
  if (score >= 40) return 'medium';
  if (score >= 20) return 'low';
  return 'safe';
}

function randomName(): string {
  return `${pick(FIRST_NAMES)} ${pick(LAST_NAMES)}`;
}

// ── Generators ────────────────────────────────────────────────────────────

export function generateTransaction(overrides: Partial<Transaction> = {}): Transaction {
  const riskScore = Math.round(randomBetween(2, 99));
  const riskLevel = getRiskLevel(riskScore);
  const statuses: TxStatus[] = riskLevel === 'critical' ? ['flagged', 'declined', 'review'] :
    riskLevel === 'high' ? ['flagged', 'review', 'approved'] :
    ['approved', 'approved', 'approved', 'review'];

  return {
    id: generateId('TX'),
    customerId: generateId('CUST'),
    customerName: randomName(),
    merchantName: pick(MERCHANTS),
    merchantCategory: pick(MERCHANT_CATS),
    amount: parseFloat(randomBetween(1.5, 24000).toFixed(2)),
    currency: pick(CURRENCIES),
    riskScore,
    riskLevel,
    status: pick(statuses),
    agentVerdict: riskLevel === 'critical' ? 'BLOCK' : riskLevel === 'high' ? 'REVIEW' : 'APPROVE',
    rulesFireCount: randomInt(0, 12),
    modelScore: parseFloat((riskScore / 100 * randomBetween(0.85, 1.05)).toFixed(4)),
    deviceId: generateId('DEV'),
    country: pick(COUNTRIES),
    timestamp: formatTs(pastDate(30)),
    ...overrides,
  };
}

export function generateTransactions(count: number = 1000): Transaction[] {
  return Array.from({ length: count }, () => generateTransaction());
}

export function generateCustomer(): Customer {
  const riskScore = randomInt(2, 98);
  return {
    id: generateId('CUST'),
    name: randomName(),
    email: `user${randomInt(100, 9999)}@${pick(['gmail.com', 'yahoo.com', 'proton.me', 'outlook.com'])}`,
    country: pick(COUNTRIES),
    riskLevel: getRiskLevel(riskScore),
    riskScore,
    txCount: randomInt(1, 850),
    lifetimeValue: parseFloat(randomBetween(50, 280000).toFixed(2)),
    flaggedCount: randomInt(0, 15),
    joinedAt: formatTs(pastDate(720)),
    lastSeenAt: formatTs(pastDate(7)),
    devices: randomInt(1, 6),
    paymentMethods: randomInt(1, 5),
  };
}

export function generateCustomers(count: number = 500): Customer[] {
  return Array.from({ length: count }, () => generateCustomer());
}

export function generateAgent(): Agent {
  const name = pick(AGENT_NAMES);
  const accuracy = randomBetween(0.78, 0.99);
  const now = new Date();
  return {
    id: generateId('AGT'),
    name,
    version: `v${randomInt(1, 4)}.${randomInt(0, 9)}.${randomInt(0, 9)}`,
    status: pick(['healthy', 'healthy', 'healthy', 'degraded', 'offline'] as AgentStatus[]),
    accuracy: parseFloat(accuracy.toFixed(4)),
    precision: parseFloat((accuracy * randomBetween(0.97, 1.02)).toFixed(4)),
    recall: parseFloat((accuracy * randomBetween(0.94, 1.01)).toFixed(4)),
    trafficPct: randomInt(5, 100),
    requestsPerMin: randomInt(50, 8000),
    latencyMs: parseFloat(randomBetween(4, 120).toFixed(1)),
    driftScore: parseFloat(randomBetween(0, 0.08).toFixed(4)),
    deployedAt: formatTs(pastDate(90)),
    lastUpdatedAt: formatTs(pastDate(14)),
    accuracyHistory: Array.from({ length: 30 }, (_, i) => ({
      ts: formatTs(new Date(now.getTime() - (29 - i) * 86400000)),
      value: parseFloat((accuracy + randomBetween(-0.03, 0.03)).toFixed(4)),
    })),
  };
}

export function generateAgents(): Agent[] {
  return AGENT_NAMES.map(() => generateAgent());
}

export function generateIncident(): Incident {
  const severity: RiskLevel = pick(['critical', 'high', 'medium', 'low']);
  const startedAt = pastDate(14);
  const resolved = Math.random() > 0.35;
  const resolvedAt = resolved ? new Date(startedAt.getTime() + randomBetween(600000, 14400000)) : undefined;
  return {
    id: generateId('INC'),
    title: pick(INCIDENT_TITLES),
    severity,
    status: resolved ? pick(['resolved', 'postmortem']) : pick(['open', 'investigating']),
    affectedServices: Array.from(new Set([pick(SERVICES), pick(SERVICES), pick(SERVICES)])),
    startedAt: formatTs(startedAt),
    resolvedAt: resolvedAt ? formatTs(resolvedAt) : undefined,
    mttrMinutes: resolvedAt ? Math.round((resolvedAt.getTime() - startedAt.getTime()) / 60000) : undefined,
    updates: Array.from({ length: randomInt(2, 6) }, (_, i) => ({
      ts: formatTs(new Date(startedAt.getTime() + i * randomBetween(300000, 900000))),
      message: pick([
        'Initial investigation started. Team paged.',
        'Root cause identified: elevated error rate on service pods.',
        'Mitigation deployed. Monitoring for stabilization.',
        'Traffic shifted to healthy replicas.',
        'Rollback initiated to previous stable version.',
        'Incident resolved. Post-mortem scheduled.',
      ]),
    })),
  };
}

export function generateIncidents(count: number = 40): Incident[] {
  return Array.from({ length: count }, () => generateIncident());
}

export function generateReviewCase(): ReviewCase {
  const tx = generateTransaction();
  const hoursToSla = randomBetween(0.5, 24);
  const slaDeadline = new Date(Date.now() + hoursToSla * 3600000);
  return {
    id: generateId('CASE'),
    transactionId: tx.id,
    customerId: tx.customerId,
    customerName: tx.customerName,
    amount: tx.amount,
    riskScore: tx.riskScore,
    riskLevel: tx.riskLevel,
    reason: pick(REVIEW_REASONS),
    assignedTo: pick(REVIEWER_NAMES),
    status: pick(['pending', 'pending', 'in_review', 'approved', 'rejected', 'escalated']),
    slaDeadline: formatTs(slaDeadline),
    createdAt: formatTs(pastDate(2)),
  };
}

export function generateReviewCases(count: number = 80): ReviewCase[] {
  return Array.from({ length: count }, () => generateReviewCase());
}

export function generateKpiSnapshot(): KpiSnapshot {
  return {
    txVolume: randomInt(42000, 98000),
    txVolumeDelta: parseFloat(randomBetween(-8, 12).toFixed(1)),
    fraudRate: parseFloat(randomBetween(0.8, 3.2).toFixed(2)),
    fraudRateDelta: parseFloat(randomBetween(-0.5, 0.5).toFixed(2)),
    approvalRate: parseFloat(randomBetween(94, 98.5).toFixed(1)),
    approvalRateDelta: parseFloat(randomBetween(-1, 1).toFixed(1)),
    activeIncidents: randomInt(0, 4),
    agentAccuracy: parseFloat(randomBetween(0.92, 0.99).toFixed(4)),
    agentAccuracyDelta: parseFloat(randomBetween(-0.01, 0.01).toFixed(4)),
  };
}

export function generateSparkline(points: number = 12, baseValue: number = 50, variance: number = 15): ChartPoint[] {
  const now = Date.now();
  let current = baseValue;
  return Array.from({ length: points }, (_, i) => {
    current += randomBetween(-variance / 2, variance / 2);
    current = Math.max(0, current);
    return {
      ts: new Date(now - (points - i) * 3600000).toISOString(),
      value: parseFloat(current.toFixed(2)),
    };
  });
}

export function generateTimeSeriesData(days: number = 30, baseValue: number = 100, variance: number = 20): ChartPoint[] {
  const now = Date.now();
  let current = baseValue;
  return Array.from({ length: days }, (_, i) => {
    current += randomBetween(-variance, variance);
    current = Math.max(0, current);
    return {
      ts: new Date(now - (days - i) * 86400000).toISOString(),
      value: parseFloat(current.toFixed(2)),
    };
  });
}

// Pre-generated datasets for instant use
export const MOCK_TRANSACTIONS = generateTransactions(1200);
export const MOCK_CUSTOMERS = generateCustomers(500);
export const MOCK_AGENTS = generateAgents();
export const MOCK_INCIDENTS = generateIncidents(40);
export const MOCK_REVIEW_CASES = generateReviewCases(80);
export const MOCK_KPI = generateKpiSnapshot();
