"use client";

import React, { useState } from "react";

interface ChaosScenario {
  id: string;
  experiment_type: string;
  status: "scheduled" | "running" | "completed" | "failed";
  target_agent: string;
  scheduled_at: string;
  metrics?: {
    recovery_time_seconds: number;
    trust_drop_index: number;
    consensus_failure_triggered: boolean;
    policy_violations_triggered: number;
    recovery_success: boolean;
  };
}

// Pre-seeded chaos experiments to display when backend isn't actively running
const SIMULATED_SCHEDULED = [
  { id: "exp-101", experiment_type: "kill_agent", target_agent: "fraud-agent", status: "scheduled", scheduled_at: "Jul 15, 18:00" },
  { id: "exp-102", experiment_type: "prompt_injection", target_agent: "compliance-agent", status: "scheduled", scheduled_at: "Jul 15, 19:30" }
];

const SIMULATED_HISTORY: ChaosScenario[] = [
  {
    id: "exp-201",
    experiment_type: "kill_agent",
    target_agent: "device-agent",
    status: "completed",
    scheduled_at: "Jul 15, 12:00",
    metrics: { recovery_time_seconds: 4.85, trust_drop_index: 30.0, consensus_failure_triggered: true, policy_violations_triggered: 0, recovery_success: true }
  },
  {
    id: "exp-202",
    experiment_type: "network_delay",
    target_agent: "kyc-agent",
    status: "completed",
    scheduled_at: "Jul 15, 14:15",
    metrics: { recovery_time_seconds: 8.24, trust_drop_index: 20.0, consensus_failure_triggered: false, policy_violations_triggered: 0, recovery_success: true }
  },
  {
    id: "exp-203",
    experiment_type: "api_failure",
    target_agent: "aml-agent",
    status: "failed",
    scheduled_at: "Jul 14, 11:10",
    metrics: { recovery_time_seconds: 6.50, trust_drop_index: 25.0, consensus_failure_triggered: false, policy_violations_triggered: 0, recovery_success: false }
  }
];

export default function ChaosDashboard() {
  const [scheduled, setScheduled] = useState<ChaosScenario[]>(SIMULATED_SCHEDULED as ChaosScenario[]);
  const [history, setHistory] = useState<ChaosScenario[]>(SIMULATED_HISTORY);
  const [clickCount, setClickCount] = useState(0);

  // Form states
  const [newScenarioType, setNewScenarioType] = useState("kill_agent");
  const [newTargetAgent, setNewTargetAgent] = useState("fraud-agent");

  const handleSchedule = (e: React.FormEvent) => {
    e.preventDefault();
    const nextCount = clickCount + 1;
    setClickCount(nextCount);
    
    const ticketId = (nextCount * 13 + 7) % 900;
    const newExp: ChaosScenario = {
      id: `exp-${100 + ticketId}`,
      experiment_type: newScenarioType,
      target_agent: newTargetAgent,
      status: "scheduled",
      scheduled_at: "Jul 15, 22:00"
    };
    setScheduled([...scheduled, newExp]);
    alert(`Chaos experiment '${newScenarioType.toUpperCase()}' scheduled successfully.`);
  };

  const handleTrigger = (expId: string) => {
    const target = scheduled.find(s => s.id === expId);
    if (!target) return;

    // Simulate fault injection execution
    const isSuccess = target.experiment_type !== "api_failure";
    const nextCount = clickCount + 1;
    setClickCount(nextCount);
    const mockJitter = ((nextCount * 23 + 11) % 100) / 100.0;
    
    const resolvedMetrics = {
      recovery_time_seconds: parseFloat((3.0 + mockJitter * 8.0).toFixed(2)),
      trust_drop_index: target.experiment_type === "kill_agent" ? 30.0 : (target.experiment_type === "prompt_injection" ? 45.0 : 15.0),
      consensus_failure_triggered: target.experiment_type === "kill_agent" || target.experiment_type === "database_failure",
      policy_violations_triggered: target.experiment_type === "prompt_injection" ? 1 : 0,
      recovery_success: isSuccess
    };

    const completedScenario: ChaosScenario = {
      id: target.id,
      experiment_type: target.experiment_type,
      target_agent: target.target_agent,
      status: isSuccess ? "completed" : "failed",
      scheduled_at: target.scheduled_at,
      metrics: resolvedMetrics
    };

    // Remove from scheduled and push to history
    setScheduled(scheduled.filter(s => s.id !== expId));
    setHistory([completedScenario, ...history]);

    alert(`Fault Injection Complete. Status: ${isSuccess ? "RECOVERED" : "FAILURE"}\nRecovery Time: ${resolvedMetrics.recovery_time_seconds}s`);
  };

  return (
    <div className="min-h-screen bg-[#0d0f14] text-[#e2e8f0] font-sans antialiased p-6 md:p-12 selection:bg-amber-500 selection:text-white">
      {/* Background glow effects */}
      <div className="absolute top-0 right-1/4 h-[350px] w-[350px] rounded-full bg-amber-500/5 blur-3xl"></div>

      {/* Page Header */}
      <header className="mb-10 border-b border-slate-800 pb-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="h-2.5 w-2.5 rounded-full bg-amber-500 animate-pulse"></span>
            <span className="text-xs uppercase tracking-wider text-amber-400 font-semibold font-mono">Chaos Engineering</span>
          </div>
          <h1 className="text-4xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
            AI Chaos Console
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            AI Governance fault injections controller. Schedule experiments, execute target breaches, and evaluate recovery indexes.
          </p>
        </div>
      </header>

      {/* Grid Layout */}
      <section className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        
        {/* Left Column: Form & scheduled queues */}
        <div className="xl:col-span-2 space-y-8">
          
          {/* Scheduler configuration */}
          <div className="rounded-xl border border-slate-800 bg-[#121620]/40 p-6 backdrop-blur-md">
            <h2 className="text-lg font-bold text-white tracking-tight mb-6">Schedule Fault Scenario</h2>
            
            <form onSubmit={handleSchedule} className="grid grid-cols-1 sm:grid-cols-3 gap-6 items-end">
              <div>
                <label className="text-[10px] uppercase font-bold tracking-wider text-slate-400 block mb-2 font-mono">Scenario Type</label>
                <select
                  value={newScenarioType}
                  onChange={(e) => setNewScenarioType(e.target.value)}
                  className="w-full px-3 py-2.5 rounded bg-slate-900 border border-slate-800 text-xs text-white focus:outline-none focus:border-amber-500 font-mono"
                >
                  <option value="kill_agent">Kill AI Agent</option>
                  <option value="database_failure">Database Failure</option>
                  <option value="redis_failure">Redis Failure</option>
                  <option value="network_delay">Network Delay</option>
                  <option value="prompt_injection">Prompt Injection</option>
                  <option value="model_drift">Model Drift</option>
                  <option value="data_poisoning">Data Poisoning</option>
                  <option value="api_failure">API Failure</option>
                </select>
              </div>

              <div>
                <label className="text-[10px] uppercase font-bold tracking-wider text-slate-400 block mb-2 font-mono">Target Agent</label>
                <select
                  value={newTargetAgent}
                  onChange={(e) => setNewTargetAgent(e.target.value)}
                  className="w-full px-3 py-2.5 rounded bg-slate-900 border border-slate-800 text-xs text-white focus:outline-none focus:border-amber-500 font-mono"
                >
                  <option value="fraud-agent">Fraud Agent</option>
                  <option value="aml-agent">AML Agent</option>
                  <option value="kyc-agent">KYC Agent</option>
                  <option value="device-agent">Device Agent</option>
                  <option value="compliance-agent">Compliance Agent</option>
                  <option value="explainability-agent">Explainability Agent</option>
                </select>
              </div>

              <button
                type="submit"
                className="w-full py-2.5 rounded bg-gradient-to-r from-amber-500 to-orange-500 text-xs font-extrabold text-white uppercase tracking-wider font-mono hover:opacity-90 transition-all duration-300 shadow-[0_0_15px_rgba(245,158,11,0.2)]"
              >
                Schedule Experiment
              </button>
            </form>
          </div>

          {/* Active Experiments Queue */}
          <div className="rounded-xl border border-slate-800 bg-[#121620]/40 p-6 backdrop-blur-md">
            <h2 className="text-lg font-bold text-white tracking-tight mb-6">Planned Scenarios Queue</h2>
            
            <div className="space-y-4">
              {scheduled.map((s) => (
                <div key={s.id} className="p-5 rounded-lg border border-slate-800 bg-slate-900/40 flex items-center justify-between gap-6 text-xs font-mono">
                  <div>
                    <span className="text-[10px] text-slate-500 block mb-1">ID: {s.id.toUpperCase()}</span>
                    <h4 className="text-sm font-bold text-white uppercase">{s.experiment_type.replace(/_/g, " ")}</h4>
                    <p className="text-slate-400 mt-1">Target: <strong className="text-amber-400">{s.target_agent}</strong></p>
                  </div>
                  
                  <div className="flex items-center gap-4">
                    <span className="text-slate-500">Plan: {s.scheduled_at}</span>
                    <button
                      onClick={() => handleTrigger(s.id)}
                      className="px-4 py-2 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20 font-bold hover:bg-amber-500/20 transition-all duration-300"
                    >
                      Trigger Fault
                    </button>
                  </div>
                </div>
              ))}

              {scheduled.length === 0 && (
                <div className="text-center py-10 border border-dashed border-slate-800 rounded bg-[#121620]/10 text-slate-500 font-mono text-xs">
                  No scheduled experiments planned. Setup a fault injection above!
                </div>
              )}
            </div>
          </div>

        </div>

        {/* Right Column: Historical audits list metrics */}
        <div className="rounded-xl border border-slate-800 bg-[#121620]/40 p-6 backdrop-blur-md flex flex-col justify-between">
          <div>
            <h2 className="text-lg font-bold text-white tracking-tight mb-4">Injections Metrics & History</h2>
            
            <div className="space-y-4 max-h-[450px] overflow-y-auto pr-2">
              {history.map((h) => (
                <div key={h.id} className="p-4 bg-slate-950/40 rounded border border-slate-800 text-xs">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-bold text-white font-mono uppercase">{h.experiment_type.replace(/_/g, " ")}</span>
                    <span className={`inline-flex px-1.5 py-0.2 rounded text-[9px] font-bold font-mono ${
                      h.status === "completed" ? "bg-emerald-500/10 text-emerald-400" : "bg-rose-500/10 text-rose-400"
                    }`}>
                      {h.status.toUpperCase()}
                    </span>
                  </div>
                  <p className="text-[10px] text-slate-500 font-mono mb-3">Target: {h.target_agent} ({h.scheduled_at})</p>
                  
                  {h.metrics && (
                    <div className="grid grid-cols-2 gap-3 border-t border-slate-900 pt-3 text-[10px] font-mono text-slate-400">
                      <div>Recovery Time: <strong className="text-white">{h.metrics.recovery_time_seconds}s</strong></div>
                      <div>Trust Drop: <strong className="text-rose-400">-{h.metrics.trust_drop_index} pt</strong></div>
                      <div>Consensus fail: <strong className="text-white">{h.metrics.consensus_failure_triggered ? "Yes" : "No"}</strong></div>
                      <div>Violations: <strong className="text-white">{h.metrics.policy_violations_triggered}</strong></div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="border-t border-slate-850 pt-4 mt-6 text-[10px] text-slate-500 font-mono">
            <span>AegisAI OS Chaos Engine</span>
            <span className="block">WORM compliance integrity ledger active</span>
          </div>
        </div>

      </section>
    </div>
  );
}
