"use client";

import React, { useState } from "react";

interface RecoveryStep {
  step: string;
  label: string;
  status: "pending" | "running" | "completed" | "failed";
  details?: string;
}

interface IncidentLog {
  id: string;
  agent_name: string;
  failure_type: string;
  status: "detected" | "healing" | "resolved" | "failed";
  description: string;
  created_at: string;
  steps: RecoveryStep[];
}

// Pre-seeded incident cases to display when backend isn't actively running
const SIMULATED_INCIDENTS: IncidentLog[] = [
  {
    id: "inc-101",
    agent_name: "fraud-agent",
    failure_type: "kill_agent",
    status: "healing",
    description: "Agent outage detected during consensus voting phase.",
    created_at: "Jul 15, 21:05",
    steps: [
      { step: "detect", label: "Failure Detected", status: "completed", details: "Fraud Agent offline signal verified." },
      { step: "diagnose", label: "Root Cause Diagnosed", status: "completed", details: "Agent thread unresponsive." },
      { step: "switch_model", label: "Switch Backup Model", status: "completed", details: "Switched to fallback v1.9.0-stable." },
      { step: "rollback", label: "Rollback Configuration", status: "completed", details: "Restored config registry parameters." },
      { step: "restart", label: "Restart Agent Loop", status: "running", details: "Reallocating thread processes..." },
      { step: "notify", label: "Notify Auditor Queue", status: "pending" },
      { step: "audit", label: "Update Audit Ledger", status: "pending" },
      { step: "revalidate", label: "Sanity Revalidation", status: "pending" },
      { step: "resume", label: "Resume Traffic", status: "pending" }
    ]
  },
  {
    id: "inc-102",
    agent_name: "aml-agent",
    failure_type: "model_drift",
    status: "resolved",
    description: "Data distribution shift detected exceeding boundary limits.",
    created_at: "Jul 15, 18:30",
    steps: [
      { step: "detect", label: "Failure Detected", status: "completed", details: "Drift coefficient 0.045 > 0.03 threshold." },
      { step: "diagnose", label: "Root Cause Diagnosed", status: "completed", details: "Concept drift identified in feature embeddings." },
      { step: "switch_model", label: "Switch Backup Model", status: "completed", details: "Redirected to v1.1.5-stable base model." },
      { step: "rollback", label: "Rollback Configuration", status: "completed", details: "Reverted active proxy routing constraints." },
      { step: "restart", label: "Restart Agent Loop", status: "completed", details: "Re-initialized evaluator loop." },
      { step: "notify", label: "Notify Auditor Queue", status: "completed", details: "Audited human review ticket generated." },
      { step: "audit", label: "Update Audit Ledger", status: "completed", details: "Appended blockchain block #8812." },
      { step: "revalidate", label: "Sanity Revalidation", status: "completed", details: "Passed mock transactions assertion checks." },
      { step: "resume", label: "Resume Traffic", status: "completed", details: "Traffic routes normalized. Agent health = 1." }
    ]
  }
];

export default function SelfHealingDashboard() {
  const [incidents, setIncidents] = useState<IncidentLog[]>(SIMULATED_INCIDENTS);
  const [selectedIncident, setSelectedIncident] = useState<IncidentLog | null>(SIMULATED_INCIDENTS[0]);

  // Failover policies configuration
  const [latencyThreshold, setLatencyThreshold] = useState("500");
  const [driftThreshold, setDriftThreshold] = useState("0.03");
  const [errorRetries, setErrorRetries] = useState("3");

  const triggerMockHealing = () => {
    // Inject a new database failure incident and start a simulated tick interval
    const newInc: IncidentLog = {
      id: `inc-${Math.floor(100 + Math.random() * 900)}`,
      agent_name: "device-agent",
      failure_type: "database_failure",
      status: "detected",
      description: "Database connection pools exhausted. Switch to fallback required.",
      created_at: "Jul 15, 22:18",
      steps: [
        { step: "detect", label: "Failure Detected", status: "completed", details: "AsyncPG connection timeouts logged." },
        { step: "diagnose", label: "Root Cause Diagnosed", status: "pending" },
        { step: "switch_model", label: "Switch Backup Model", status: "pending" },
        { step: "rollback", label: "Rollback Configuration", status: "pending" },
        { step: "restart", label: "Restart Agent Loop", status: "pending" },
        { step: "notify", label: "Notify Auditor Queue", status: "pending" },
        { step: "audit", label: "Update Audit Ledger", status: "pending" },
        { step: "revalidate", label: "Sanity Revalidation", status: "pending" },
        { step: "resume", label: "Resume Traffic", status: "pending" }
      ]
    };

    setIncidents([newInc, ...incidents]);
    setSelectedIncident(newInc);
    alert("Mock failure injected! Initiating event-driven recovery workflow.");
  };

  return (
    <div className="min-h-screen bg-[#0d0f14] text-[#e2e8f0] font-sans antialiased p-6 md:p-12 selection:bg-emerald-500 selection:text-white">
      {/* Background glow effects */}
      <div className="absolute top-0 right-1/4 h-[350px] w-[350px] rounded-full bg-emerald-500/5 blur-3xl"></div>

      {/* Page Header */}
      <header className="mb-10 border-b border-slate-800 pb-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="h-2.5 w-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
            <span className="text-xs uppercase tracking-wider text-emerald-400 font-semibold font-mono">Self-Healing Engine</span>
          </div>
          <h1 className="text-4xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
            Recovery & Self-Healing Console
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Event-driven self-healing system monitoring failure detections, database switchovers, and automatic traffic resumptions.
          </p>
        </div>

        <div>
          <button
            onClick={triggerMockHealing}
            className="px-5 py-2.5 rounded text-xs font-black uppercase tracking-wider font-mono bg-rose-600 hover:bg-rose-500 text-white transition-all duration-300 shadow-[0_0_15px_rgba(244,63,94,0.3)]"
          >
            🔥 Inject Database Failure
          </button>
        </div>
      </header>

      {/* Grid Layout */}
      <section className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        
        {/* Left Column: Active Incidents List & Config policies */}
        <div className="xl:col-span-2 space-y-8">
          
          {/* Incidents Queue */}
          <div className="rounded-xl border border-slate-800 bg-[#121620]/40 p-6 backdrop-blur-md">
            <h2 className="text-lg font-bold text-white tracking-tight mb-6">Incident Queue</h2>
            
            <div className="space-y-4">
              {incidents.map((inc) => (
                <div
                  key={inc.id}
                  onClick={() => setSelectedIncident(inc)}
                  className={`p-5 rounded-lg border transition-all duration-300 cursor-pointer ${
                    selectedIncident?.id === inc.id
                      ? "bg-[#121620]/80 border-emerald-500 shadow-[0_0_15px_rgba(16,185,129,0.1)]"
                      : "bg-slate-900/40 border-slate-800 hover:border-slate-700"
                  }`}
                >
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <span className="text-[10px] text-slate-500 font-mono block uppercase">ID: {inc.id}</span>
                      <h4 className="text-sm font-bold text-white uppercase">{inc.failure_type.replace(/_/g, " ")}</h4>
                    </div>
                    <span className={`inline-flex px-2 py-0.5 rounded text-[10px] font-bold font-mono ${
                      inc.status === "resolved" ? "bg-emerald-500/10 text-emerald-400" : "bg-amber-500/10 text-amber-400 animate-pulse"
                    }`}>
                      {inc.status.toUpperCase()}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 font-mono leading-relaxed mb-4">{inc.description}</p>
                  
                  <div className="flex justify-between border-t border-slate-850 pt-3 text-[10px] font-mono text-slate-500">
                    <span>Target: {inc.agent_name}</span>
                    <span>Logged: {inc.created_at}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recovery Policies Configurations */}
          <div className="rounded-xl border border-slate-800 bg-[#121620]/40 p-6 backdrop-blur-md">
            <h2 className="text-lg font-bold text-white tracking-tight mb-6">Automated Recovery Policies</h2>
            
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
              <div>
                <label className="text-[10px] uppercase font-bold tracking-wider text-slate-400 block mb-2 font-mono">Max Latency (ms)</label>
                <input
                  type="number"
                  value={latencyThreshold}
                  onChange={(e) => setLatencyThreshold(e.target.value)}
                  className="w-full px-3 py-2 rounded bg-slate-900 border border-slate-800 text-xs text-white focus:outline-none focus:border-emerald-500 font-mono"
                />
              </div>

              <div>
                <label className="text-[10px] uppercase font-bold tracking-wider text-slate-400 block mb-2 font-mono">Drift Coefficient Limit</label>
                <input
                  type="text"
                  value={driftThreshold}
                  onChange={(e) => setDriftThreshold(e.target.value)}
                  className="w-full px-3 py-2 rounded bg-slate-900 border border-slate-800 text-xs text-white focus:outline-none focus:border-emerald-500 font-mono"
                />
              </div>

              <div>
                <label className="text-[10px] uppercase font-bold tracking-wider text-slate-400 block mb-2 font-mono">API Failover Retries</label>
                <input
                  type="number"
                  value={errorRetries}
                  onChange={(e) => setErrorRetries(e.target.value)}
                  className="w-full px-3 py-2 rounded bg-slate-900 border border-slate-800 text-xs text-white focus:outline-none focus:border-emerald-500 font-mono"
                />
              </div>
            </div>
          </div>

        </div>

        {/* Right Column: Visual Self-Healing flow timeline */}
        <div className="rounded-xl border border-slate-800 bg-[#121620]/40 p-6 backdrop-blur-md flex flex-col justify-between">
          <div>
            <h2 className="text-lg font-bold text-white tracking-tight mb-6 font-mono uppercase">Healing Flowchart</h2>
            
            {selectedIncident ? (
              <div className="space-y-6">
                
                <div className="flex items-center justify-between border-b border-slate-850 pb-3 font-mono text-xs">
                  <span className="text-slate-400">Incident Target</span>
                  <span className="text-emerald-400 font-bold uppercase">{selectedIncident.agent_name}</span>
                </div>

                {/* Vertical flowchart steps */}
                <div className="relative border-l-2 border-slate-800 ml-4 pl-6 space-y-4">
                  {selectedIncident.steps.map((s, idx) => {
                    let dotColor = "bg-slate-800";
                    if (s.status === "completed") dotColor = "bg-emerald-500";
                    else if (s.status === "running") dotColor = "bg-amber-500 animate-ping";
                    
                    return (
                      <div key={idx} className="relative text-xs font-mono">
                        <span className={`absolute -left-[31px] top-1.5 h-4.5 w-4.5 rounded-full border-4 border-[#0d0f14] ${dotColor}`}></span>
                        <div>
                          <div className="flex justify-between font-bold text-white">
                            <span>{s.label}</span>
                            <span className="text-[10px] uppercase text-slate-500">{s.status}</span>
                          </div>
                          {s.details && (
                            <p className="text-[10px] text-slate-400 leading-relaxed mt-1">{s.details}</p>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>

              </div>
            ) : (
              <div className="text-center py-24 text-slate-500">
                <p className="text-4xl mb-3">🛠️</p>
                <p className="text-xs">No active incident selected.</p>
                <p className="text-xs mt-1 font-mono">Choose an event from the queue to trace workflow execution nodes.</p>
              </div>
            )}
          </div>

          <div className="border-t border-slate-850 pt-4 mt-6 text-[10px] text-slate-500 font-mono">
            <span>AegisAI OS Event Broker v1.0.0</span>
            <span className="block">WORM transaction tracking logs active</span>
          </div>
        </div>

      </section>
    </div>
  );
}
