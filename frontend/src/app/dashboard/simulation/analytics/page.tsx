"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { BarChart3, Download, ArrowLeft, ShieldAlert, CheckCircle, TrendingDown, Clock } from "lucide-react";

export default function SimulationAnalytics() {
  const router = useRouter();
  
  // Mock analytics data for the demo
  const [report, setReport] = useState<any>({
    id: "rep-001",
    scenario_name: "High Fraud Attack Vector",
    completed_at: new Date().toISOString(),
    metrics: {
      total_transactions: 100000,
      fraud_detected: 4850,
      false_negatives: 150, // missed fraud
      aml_alerts: 1200,
      false_positives: 850,
      avg_latency_ms: 124.5,
      peak_tps: 65.2,
      trust_score_impact: -2.4
    }
  });

  const handleExport = () => {
    alert("Exporting PDF Report...");
  };

  return (
    <div style={{ maxWidth: 1000, margin: "0 auto", paddingBottom: 60 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 32 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <button onClick={() => router.push("/dashboard/simulation")} style={{ background: "none", border: "1px solid var(--border-1)", color: "var(--text-1)", padding: 8, borderRadius: 8, cursor: "pointer" }}>
            <ArrowLeft size={18} />
          </button>
          <div>
            <h1 style={{ fontSize: 24, fontWeight: 800, color: "var(--text-1)" }}>Simulation Analytics</h1>
            <p style={{ fontSize: 13, color: "var(--text-2)", marginTop: 4 }}>Report for: <strong>{report.scenario_name}</strong> • Completed {new Date(report.completed_at).toLocaleString()}</p>
          </div>
        </div>
        
        <button onClick={handleExport} style={{
          background: "var(--surface-2)", color: "var(--text-1)", border: "1px solid var(--border-1)", borderRadius: "8px",
          padding: "8px 16px", fontSize: 13, fontWeight: 600, cursor: "pointer", display: "flex", alignItems: "center", gap: 8
        }}>
          <Download size={16} /> Export PDF
        </button>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>
        
        {/* Core KPI Panel */}
        <div style={{ background: "var(--surface-2)", border: "1px solid var(--border-1)", borderRadius: "12px", padding: 24, display: "flex", flexDirection: "column", gap: 20 }}>
          <h3 style={{ fontSize: 16, fontWeight: 700, color: "var(--text-1)", display: "flex", alignItems: "center", gap: 8 }}>
            <BarChart3 size={18} color="var(--accent-1)" /> Evaluation KPIs
          </h3>
          
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
            <KpiBox label="Total Evaluated" value={report.metrics.total_transactions.toLocaleString()} />
            <KpiBox label="Peak Throughput" value={`${report.metrics.peak_tps} TPS`} color="var(--accent-1)" />
            <KpiBox label="Fraud Blocked" value={report.metrics.fraud_detected.toLocaleString()} color="var(--success)" />
            <KpiBox label="Missed Fraud (FN)" value={report.metrics.false_negatives} color="#ef4444" />
          </div>
        </div>

        {/* Risk & Trust Impact Panel */}
        <div style={{ background: "var(--surface-2)", border: "1px solid var(--border-1)", borderRadius: "12px", padding: 24, display: "flex", flexDirection: "column", gap: 20 }}>
          <h3 style={{ fontSize: 16, fontWeight: 700, color: "var(--text-1)", display: "flex", alignItems: "center", gap: 8 }}>
            <ShieldAlert size={18} color="var(--warning)" /> Resilience Impact
          </h3>
          
          <div style={{ background: "var(--surface-1)", border: "1px solid var(--border-1)", borderRadius: "8px", padding: 16, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <div style={{ fontSize: 13, color: "var(--text-2)", fontWeight: 600 }}>Trust Score Impact</div>
              <div style={{ fontSize: 32, fontWeight: 800, color: "#ef4444", marginTop: 4 }}>
                {report.metrics.trust_score_impact}%
              </div>
            </div>
            <TrendingDown size={40} color="#ef4444" opacity={0.2} />
          </div>

          <div style={{ display: "flex", gap: 12 }}>
            <div style={{ flex: 1, background: "var(--surface-1)", border: "1px solid var(--border-1)", borderRadius: "8px", padding: 12 }}>
              <div style={{ fontSize: 11, color: "var(--text-3)", textTransform: "uppercase", fontWeight: 700 }}>Avg Latency</div>
              <div style={{ fontSize: 16, fontWeight: 700, color: "var(--text-1)", marginTop: 4 }}>{report.metrics.avg_latency_ms} ms</div>
            </div>
            <div style={{ flex: 1, background: "var(--surface-1)", border: "1px solid var(--border-1)", borderRadius: "8px", padding: 12 }}>
              <div style={{ fontSize: 11, color: "var(--text-3)", textTransform: "uppercase", fontWeight: 700 }}>False Positives</div>
              <div style={{ fontSize: 16, fontWeight: 700, color: "var(--warning)", marginTop: 4 }}>{report.metrics.false_positives} cases</div>
            </div>
          </div>
        </div>
        
        {/* Executive Summary */}
        <div style={{ gridColumn: "1 / -1", background: "var(--surface-2)", border: "1px solid var(--border-1)", borderRadius: "12px", padding: 24 }}>
          <h3 style={{ fontSize: 16, fontWeight: 700, color: "var(--text-1)", marginBottom: 16 }}>Executive Summary</h3>
          <p style={{ fontSize: 14, color: "var(--text-2)", lineHeight: 1.6 }}>
            The simulation <strong>{report.scenario_name}</strong> processed {report.metrics.total_transactions.toLocaleString()} synthetic transactions. 
            The system successfully intercepted {report.metrics.fraud_detected.toLocaleString()} fraudulent events. However, the injected failures caused a degradation in accuracy, resulting in {report.metrics.false_negatives} missed fraudulent transactions and {report.metrics.false_positives} false positives. 
            Overall trust score dropped by {Math.abs(report.metrics.trust_score_impact)}% due to SLA breaches and latency spikes.
          </p>
        </div>

      </div>
    </div>
  );
}

function KpiBox({ label, value, color = "var(--text-1)" }: any) {
  return (
    <div style={{ background: "var(--surface-1)", border: "1px solid var(--border-1)", padding: "16px", borderRadius: "8px" }}>
      <div style={{ fontSize: 12, color: "var(--text-2)", fontWeight: 600, marginBottom: 8 }}>{label}</div>
      <div style={{ fontSize: 24, fontWeight: 800, color }}>{value}</div>
    </div>
  );
}
