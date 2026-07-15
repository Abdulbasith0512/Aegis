"use client";

import React, { useState } from "react";

// Pre-seeded realistic explainability session history to display when backend isn't actively running
const SIMULATED_DECISIONS = [
  {
    id: "pred-101",
    tx_ref: "TX-99882",
    date: "Jul 15, 14:30:12",
    verdict: "approved",
    score: 0.98,
    human: "Transaction matches expected standard customer profiles. Checks passed.",
    timeline: [
      { event: "Transaction Ingested", duration_ms: 1.2, timestamp: "14:30:12.012", status: "success" },
      { event: "Device Evaluation Complete", duration_ms: 22.5, timestamp: "14:30:12.034", status: "success" },
      { event: "KYC Identity Check Complete", duration_ms: 15.1, timestamp: "14:30:12.049", status: "success" },
      { event: "Model Classifier Prediction Resolved", duration_ms: 48.6, timestamp: "14:30:12.098", status: "success" },
      { event: "Compliance Policies Verified", duration_ms: 2.4, timestamp: "14:30:12.100", status: "success" },
      { event: "Final Decision Output Rendered", duration_ms: 1.1, timestamp: "14:30:12.101", status: "success" }
    ],
    shap: {
      "amount_value": 0.15,
      "device_fingerprint": 0.05,
      "ip_velocity": 0.08,
      "kyc_risk_tier": 0.07,
      "policy_limits": 0.02
    },
    graph: {
      nodes: [
        { id: "acc", type: "account", label: "Client Checking Account", status: "active", x: 100, y: 150 },
        { id: "dev", type: "device", label: "Client iPhone 14", status: "passed", x: 280, y: 70 },
        { id: "pol", type: "policy", label: "PATRIOT Act Limit", status: "passed", x: 280, y: 230 },
        { id: "decision", type: "agent", label: "AegisAI Verdict", status: "passed", x: 480, y: 150 }
      ],
      edges: [
        { source: "acc", target: "decision", label: "initiates" },
        { source: "dev", target: "decision", label: "telemetry" },
        { source: "decision", target: "pol", label: "evaluates" }
      ]
    }
  },
  {
    id: "pred-102",
    tx_ref: "TX-99883",
    date: "Jul 15, 14:32:45",
    verdict: "under_review",
    score: 0.72,
    human: "Transaction flagged under caution: Anomaly trigger: latency exceeds 100ms standard and/or rule check compliance failures registered.",
    timeline: [
      { event: "Transaction Ingested", duration_ms: 1.5, timestamp: "14:32:45.002", status: "success" },
      { event: "Device Evaluation Complete", duration_ms: 210.2, timestamp: "14:32:45.212", status: "warning" },
      { event: "KYC Identity Check Complete", duration_ms: 14.8, timestamp: "14:32:45.227", status: "success" },
      { event: "Model Classifier Prediction Resolved", duration_ms: 45.1, timestamp: "14:32:45.272", status: "success" },
      { event: "Compliance Policies Verified", duration_ms: 2.1, timestamp: "14:32:45.274", status: "success" },
      { event: "Final Decision Output Rendered", duration_ms: 1.0, timestamp: "14:32:45.275", status: "success" }
    ],
    shap: {
      "amount_value": 0.18,
      "device_fingerprint": 0.55,
      "ip_velocity": 0.12,
      "kyc_risk_tier": 0.05,
      "latency_sla": 0.65
    },
    graph: {
      nodes: [
        { id: "acc", type: "account", label: "Client Checking Account", status: "active", x: 100, y: 150 },
        { id: "dev", type: "device", label: "Client iPad (Emulator)", status: "risk", x: 280, y: 70 },
        { id: "pol", type: "policy", label: "USD Base Policy", status: "passed", x: 280, y: 230 },
        { id: "decision", type: "agent", label: "AegisAI Verdict", status: "warning", x: 480, y: 150 }
      ],
      edges: [
        { source: "acc", target: "decision", label: "initiates" },
        { source: "dev", target: "decision", label: "telemetry" },
        { source: "decision", target: "pol", label: "evaluates" }
      ]
    }
  }
];

export default function ExplainabilityDashboard() {
  const [activeSession, setActiveSession] = useState(SIMULATED_DECISIONS[0]);

  return (
    <div className="min-h-screen bg-[#0d0f14] text-[#e2e8f0] font-sans antialiased p-6 md:p-12 selection:bg-indigo-500 selection:text-white">
      {/* Page Header */}
      <header className="mb-10 border-b border-slate-800 pb-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="h-2.5 w-2.5 rounded-full bg-indigo-500 animate-pulse"></span>
            <span className="text-xs uppercase tracking-wider text-indigo-400 font-semibold font-mono">Explainability Portal</span>
          </div>
          <h1 className="text-4xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
            Explainability Diagnostics
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Visual audit logs mapping timelines, topological evidence graphs, and Shapley attribution values.
          </p>
        </div>
        
        {/* Toggle Sessions */}
        <div className="flex gap-2">
          {SIMULATED_DECISIONS.map((session) => (
            <button
              key={session.id}
              onClick={() => setActiveSession(session)}
              className={`px-4 py-2 text-xs font-bold rounded font-mono border transition-all duration-300 ${
                activeSession.id === session.id
                  ? "bg-indigo-600 border-indigo-500 text-white shadow-[0_0_15px_rgba(99,102,241,0.3)]"
                  : "bg-[#121620]/60 border-slate-800 text-slate-400 hover:text-slate-200"
              }`}
            >
              {session.tx_ref} ({session.verdict.toUpperCase()})
            </button>
          ))}
        </div>
      </header>

      {/* Main Grid */}
      <section className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        
        {/* Graph & Timeline Columns */}
        <div className="xl:col-span-2 space-y-8">
          
          {/* Evidence Graph Container */}
          <div className="rounded-xl border border-slate-800 bg-[#121620]/40 p-6 backdrop-blur-md">
            <h2 className="text-lg font-bold text-white tracking-tight mb-6">Decision Evidence Graph</h2>
            
            {/* SVG Evidence Graph Visualizer */}
            <div className="w-full bg-slate-950/40 rounded-lg p-4 border border-slate-800/60 overflow-x-auto">
              <svg width="580" height="300" className="mx-auto overflow-visible">
                {/* Render Edges */}
                {activeSession.graph.edges.map((edge, i) => {
                  const srcNode = activeSession.graph.nodes.find(n => n.id === edge.source);
                  const tgtNode = activeSession.graph.nodes.find(n => n.id === edge.target);
                  if (!srcNode || !tgtNode) return null;
                  
                  return (
                    <g key={i}>
                      <line
                        x1={srcNode.x}
                        y1={srcNode.y}
                        x2={tgtNode.x}
                        y2={tgtNode.y}
                        stroke="#1e293b"
                        strokeWidth="3.5"
                        markerEnd="url(#arrow)"
                      />
                      <text
                        x={(srcNode.x + tgtNode.x) / 2}
                        y={(srcNode.y + tgtNode.y) / 2 - 8}
                        fill="#64748b"
                        fontSize="9"
                        textAnchor="middle"
                        className="font-mono"
                      >
                        {edge.label}
                      </text>
                    </g>
                  );
                })}

                {/* Render Nodes */}
                {activeSession.graph.nodes.map((node) => {
                  let fill = "rgba(18, 22, 32, 0.9)";
                  let border = "#1e293b";
                  let labelColor = "#ffffff";
                  
                  if (node.status === "passed" || node.status === "active") {
                    border = "#10b981"; // Emerald
                  } else if (node.status === "warning") {
                    border = "#f59e0b"; // Amber
                  } else if (node.status === "risk" || node.status === "failed") {
                    border = "#f43f5e"; // Rose
                  }

                  return (
                    <g key={node.id} className="transition-all duration-300">
                      <rect
                        x={node.x - 70}
                        y={node.y - 25}
                        width="140"
                        height="50"
                        rx="8"
                        fill={fill}
                        stroke={border}
                        strokeWidth="2"
                        className="shadow-lg"
                      />
                      <text
                        x={node.x}
                        y={node.y - 2}
                        fill={labelColor}
                        fontSize="11"
                        fontWeight="bold"
                        textAnchor="middle"
                      >
                        {node.label}
                      </text>
                      <text
                        x={node.x}
                        y={node.y + 12}
                        fill="#64748b"
                        fontSize="9"
                        textAnchor="middle"
                        className="font-mono uppercase tracking-wider"
                      >
                        {node.type}
                      </text>
                    </g>
                  );
                })}

                {/* Arrow Definition */}
                <defs>
                  <marker
                    id="arrow"
                    viewBox="0 0 10 10"
                    refX="48"
                    refY="5"
                    markerWidth="6"
                    markerHeight="6"
                    orient="auto-start-reverse"
                  >
                    <path d="M 0 0 L 10 5 L 0 10 z" fill="#1e293b" />
                  </marker>
                </defs>
              </svg>
            </div>
          </div>

          {/* Timeline Panel */}
          <div className="rounded-xl border border-slate-800 bg-[#121620]/40 p-6 backdrop-blur-md">
            <h2 className="text-lg font-bold text-white tracking-tight mb-6">Execution Decision Timeline</h2>
            
            {/* Timeline Stream */}
            <div className="relative border-l-2 border-slate-800 ml-4 pl-6 space-y-6">
              {activeSession.timeline.map((step, idx) => (
                <div key={idx} className="relative">
                  {/* Step Dot indicator */}
                  <span className={`absolute -left-[31px] top-1.5 h-4.5 w-4.5 rounded-full border-4 border-[#0d0f14] ${
                    step.status === "success" ? "bg-emerald-500" : "bg-amber-500"
                  }`}></span>
                  
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <h4 className="text-sm font-semibold text-white">{step.event}</h4>
                      <p className="text-[10px] font-mono text-slate-500">{step.timestamp}</p>
                    </div>
                    <span className="text-xs font-mono text-slate-400 font-semibold px-2 py-0.5 rounded bg-slate-900 border border-slate-800">
                      {step.duration_ms} ms
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Explainability side insights */}
        <div className="space-y-8">
          
          {/* Human Explanatory statement */}
          <div className="rounded-xl border border-slate-800 bg-[#121620]/40 p-6 backdrop-blur-md">
            <h2 className="text-lg font-bold text-white tracking-tight mb-4">Explanatory Narrative</h2>
            <div className="p-4 rounded-lg bg-indigo-500/5 border border-indigo-500/20 text-indigo-200 text-sm leading-relaxed">
              {activeSession.human}
            </div>
            
            <div className="flex items-center justify-between border-t border-slate-800 pt-4 mt-6">
              <span className="text-xs text-slate-400">Explainability score:</span>
              <span className="text-sm font-black font-mono text-indigo-400">{activeSession.score} / 1.00</span>
            </div>
          </div>

          {/* Feature Importance panel */}
          <div className="rounded-xl border border-slate-800 bg-[#121620]/40 p-6 backdrop-blur-md">
            <h2 className="text-lg font-bold text-white tracking-tight mb-6">SHAP Feature Attributions</h2>
            
            <div className="space-y-4">
              {Object.entries(activeSession.shap).map(([feature, val]) => (
                <div key={feature}>
                  <div className="flex items-center justify-between text-xs mb-1 font-mono">
                    <span className="text-slate-400">{feature}</span>
                    <span className="text-slate-200 font-semibold">{val.toFixed(2)}</span>
                  </div>
                  {/* Bar indicator */}
                  <div className="h-1.5 w-full bg-slate-900 rounded overflow-hidden">
                    <div
                      className={`h-full rounded ${
                        val > 0.50 ? "bg-rose-500" : (val > 0.20 ? "bg-amber-500" : "bg-indigo-500")
                      }`}
                      style={{ width: `${val * 100}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
            
            <div className="mt-6 border-t border-slate-800 pt-4 text-[10px] text-slate-500 font-mono">
              Attributions map feature contributions. Values above 0.50 indicate significant risk triggers.
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
