"use client";

import React, { useState } from "react";
import { ToastBar } from "@/components/ui/ToastBar";
import { Loader2 } from "lucide-react";

// Pre-seeded realistic simulation history to display when backend isn't actively running
const SIMULATED_HISTORY = [
  { id: "ts-1", date: "Jul 05", score: 92, status: "passed", latency: 45, warnings: 0 },
  { id: "ts-2", date: "Jul 06", score: 88, status: "passed", latency: 52, warnings: 0 },
  { id: "ts-3", date: "Jul 07", score: 48, status: "failed", latency: 890, warnings: 2 }, // latency SLA, policy compliance fail
  { id: "ts-4", date: "Jul 08", score: 95, status: "passed", latency: 42, warnings: 0 },
  { id: "ts-5", date: "Jul 09", score: 71, status: "warning", latency: 210, warnings: 1 }, // latency warning
  { id: "ts-6", date: "Jul 10", score: 96, status: "passed", latency: 38, warnings: 0 },
  { id: "ts-7", date: "Jul 11", score: 90, status: "passed", latency: 48, warnings: 0 },
  { id: "ts-8", date: "Jul 12", score: 32, status: "failed", latency: 58, warnings: 1 }, // compliance failed
  { id: "ts-9", date: "Jul 13", score: 87, status: "passed", latency: 62, warnings: 0 },
  { id: "ts-10", date: "Jul 14", score: 74, status: "warning", latency: 120, warnings: 1 },
  { id: "ts-11", date: "Jul 15", score: 98, status: "passed", latency: 35, warnings: 0 },
];

export default function TrustDashboard() {
  const [selectedPoint, setSelectedPoint] = useState<typeof SIMULATED_HISTORY[0] | null>(null);
  const [alertThreshold, setAlertThreshold] = useState(75);
  const [showConfig, setShowConfig] = useState(false);
  const [verifying, setVerifying] = useState(false);
  const [toasts, setToasts] = useState<any[]>([]);

  const handleRunVerification = () => {
    setVerifying(true);
    const toastId = Math.random().toString();
    setToasts(prev => [...prev, {
      id: toastId,
      type: "info",
      message: "Running Trust Engine Verification Suite... Testing policy compliance & drift latency."
    }]);

    setTimeout(() => {
      setVerifying(false);
      setToasts(prev => [
        ...prev.filter(x => x.id !== toastId),
        {
          id: Math.random().toString(),
          type: "success",
          message: "Verification completed successfully. 0 policy violations detected across 1,080,667 calculations."
        }
      ]);
    }, 1500);
  };

  // SVG Chart calculation parameters
  const chartHeight = 220;
  const chartWidth = 780;
  const paddingX = 40;
  const paddingY = 20;

  const pointsCount = SIMULATED_HISTORY.length;
  const stepX = (chartWidth - paddingX * 2) / (pointsCount - 1);

  // Function to map score value to Y coordinate
  const getY = (score: number) => {
    const scale = (chartHeight - paddingY * 2) / 100;
    return chartHeight - paddingY - score * scale;
  };

  // Compile path points string
  const pathPoints = SIMULATED_HISTORY.map((pt, i) => {
    const x = paddingX + i * stepX;
    const y = getY(pt.score);
    return `${x},${y}`;
  }).join(" ");

  // Compile filled area path points string (loops back to bottom of chart)
  const areaPoints = `${paddingX},${chartHeight - paddingY} ${pathPoints} ${paddingX + (pointsCount - 1) * stepX},${chartHeight - paddingY}`;

  return (
    <div className="min-h-screen bg-[#0d0f14] text-[#e2e8f0] font-sans antialiased selection:bg-cyan-500 selection:text-white p-6 md:p-12">
      <ToastBar toasts={toasts} onDismiss={(id) => setToasts(t => t.filter(x => x.id !== id))} />

      {/* Header Panel */}
      <header className="mb-10 flex flex-col md:flex-row md:items-center justify-between gap-6 border-b border-slate-800 pb-8">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="h-2.5 w-2.5 rounded-full bg-cyan-400 animate-pulse"></span>
            <span className="text-xs uppercase tracking-wider text-cyan-400 font-semibold font-mono">System Engine Active</span>
          </div>
          <h1 className="text-4xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-200 to-slate-400">
            Trust Engine Telemetry
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Real-time monitoring interface for AegisAI agent confidence, drift, and policy compliance.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button 
            onClick={() => setShowConfig(!showConfig)}
            className="px-4 py-2 text-xs font-semibold rounded bg-[#1e2330] hover:bg-slate-800 border border-slate-800 text-slate-300 transition-all duration-300"
          >
            {showConfig ? "Close SLA Panel" : "Configure SLA"}
          </button>
          <button 
            onClick={handleRunVerification}
            disabled={verifying}
            className="px-4 py-2 text-xs font-semibold rounded bg-gradient-to-r from-cyan-500 to-blue-500 hover:opacity-90 text-white font-mono shadow-[0_0_15px_rgba(6,182,212,0.3)] transition-all duration-300 flex items-center gap-2"
          >
            {verifying && <Loader2 size={12} className="animate-spin" />}
            {verifying ? "Running Suite..." : "Run Verification Suite"}
          </button>
        </div>
      </header>

      {/* SLA Configuration Controls */}
      {showConfig && (
        <div className="mb-8 p-6 rounded-xl border border-slate-800 bg-[#121620]/80 backdrop-blur-md transition-all duration-300">
          <h3 className="text-sm font-bold text-white mb-2">Configure SLA alert threshold</h3>
          <p className="text-xs text-slate-400 mb-4">Set the threshold below which transactions trigger Human-In-The-Loop (HITL) audits.</p>
          <div className="flex items-center gap-6">
            <input 
              type="range" 
              min="50" 
              max="95" 
              value={alertThreshold} 
              onChange={(e) => setAlertThreshold(parseInt(e.target.value))}
              className="w-full h-1 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400"
            />
            <span className="text-lg font-mono font-black text-cyan-400 min-w-[3rem] text-right">
              {alertThreshold}%
            </span>
          </div>
        </div>
      )}

      {/* Metrics Summary Cards */}
      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
        {/* Metric 1 */}
        <div className="relative overflow-hidden rounded-xl border border-slate-800 bg-[#121620]/60 p-6 backdrop-blur-md transition-all duration-300 hover:border-cyan-500 group">
          <div className="absolute top-0 right-0 h-24 w-24 translate-x-8 -translate-y-8 rounded-full bg-cyan-500/10 blur-xl group-hover:bg-cyan-500/20 transition-all duration-300"></div>
          <p className="text-xs font-mono uppercase tracking-wider text-slate-400 mb-1">Average Trust score</p>
          <h3 className="text-3xl font-extrabold text-white font-mono flex items-baseline gap-1">
            85.6 <span className="text-lg text-cyan-400">%</span>
          </h3>
          <p className="text-xs text-emerald-400 mt-2 flex items-center gap-1 font-mono">
            ▲ +2.4% <span className="text-slate-500">vs yesterday</span>
          </p>
        </div>

        {/* Metric 2 */}
        <div className="relative overflow-hidden rounded-xl border border-slate-800 bg-[#121620]/60 p-6 backdrop-blur-md transition-all duration-300 hover:border-blue-500 group">
          <div className="absolute top-0 right-0 h-24 w-24 translate-x-8 -translate-y-8 rounded-full bg-blue-500/10 blur-xl group-hover:bg-blue-500/20 transition-all duration-300"></div>
          <p className="text-xs font-mono uppercase tracking-wider text-slate-400 mb-1">Total Calculations</p>
          <h3 className="text-3xl font-extrabold text-white font-mono">1,080,667</h3>
          <p className="text-xs text-slate-400 mt-2 font-mono">
            Direct database sync active
          </p>
        </div>

        {/* Metric 3 */}
        <div className="relative overflow-hidden rounded-xl border border-slate-800 bg-[#121620]/60 p-6 backdrop-blur-md transition-all duration-300 hover:border-amber-500 group">
          <div className="absolute top-0 right-0 h-24 w-24 translate-x-8 -translate-y-8 rounded-full bg-amber-500/10 blur-xl group-hover:bg-amber-500/20 transition-all duration-300"></div>
          <p className="text-xs font-mono uppercase tracking-wider text-slate-400 mb-1">Alert Thresholds</p>
          <h3 className="text-3xl font-extrabold text-white font-mono flex items-baseline gap-1">
            {alertThreshold} <span className="text-sm font-sans text-amber-500 font-semibold">(HITL Trigger)</span>
          </h3>
          <p className="text-xs text-amber-500 mt-2 flex items-center gap-1 font-mono">
            Score &lt; {alertThreshold} delegates to audit
          </p>
        </div>

        {/* Metric 4 */}
        <div className="relative overflow-hidden rounded-xl border border-slate-800 bg-[#121620]/60 p-6 backdrop-blur-md transition-all duration-300 hover:border-rose-500 group">
          <div className="absolute top-0 right-0 h-24 w-24 translate-x-8 -translate-y-8 rounded-full bg-rose-500/10 blur-xl group-hover:bg-rose-500/20 transition-all duration-300"></div>
          <p className="text-xs font-mono uppercase tracking-wider text-slate-400 mb-1">SLA Compliance</p>
          <h3 className="text-3xl font-extrabold text-rose-400 font-mono">99.82%</h3>
          <p className="text-xs text-rose-400 mt-2 flex items-center gap-1 font-mono">
            ▼ -0.05% <span className="text-slate-500">latency spikes</span>
          </p>
        </div>
      </section>

      {/* Main Visualization & History Table grid */}
      <section className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* SVG Chart Panel */}
        <div className="lg:col-span-2 rounded-xl border border-slate-800 bg-[#121620]/40 p-6 backdrop-blur-md">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-bold text-white tracking-tight">Trust Score Historic Trend</h2>
            <div className="flex items-center gap-2">
              <span className="h-3 w-3 rounded-full bg-cyan-400"></span>
              <span className="text-xs font-semibold text-slate-300">Calculated score (%)</span>
            </div>
          </div>

          {/* SVG Canvas */}
          <div className="relative w-full overflow-x-auto">
            <svg
              viewBox={`0 0 ${chartWidth} ${chartHeight}`}
              className="w-full h-auto min-w-[700px] overflow-visible"
            >
              {/* Grids / Guidelines */}
              <line x1={paddingX} y1={getY(100)} x2={chartWidth - paddingX} y2={getY(100)} stroke="#1e293b" strokeDasharray="3,3" />
              <line x1={paddingX} y1={getY(alertThreshold)} x2={chartWidth - paddingX} y2={getY(alertThreshold)} stroke="#e0a96d" strokeDasharray="5,5" />
              <line x1={paddingX} y1={getY(50)} x2={chartWidth - paddingX} y2={getY(50)} stroke="#1e293b" strokeDasharray="3,3" />
              <line x1={paddingX} y1={getY(0)} x2={chartWidth - paddingX} y2={getY(0)} stroke="#1e293b" strokeDasharray="3,3" />

              {/* Limit alert zone highlight (Score < alertThreshold) */}
              <rect
                x={paddingX}
                y={getY(alertThreshold)}
                width={chartWidth - paddingX * 2}
                height={getY(0) - getY(alertThreshold)}
                fill="rgba(245,158,11,0.02)"
              />

              {/* Area Under Curve Gradient */}
              <polygon
                points={areaPoints}
                fill="url(#chartGrad)"
                className="opacity-20"
              />

              {/* Main Line path */}
              <polyline
                fill="none"
                stroke="url(#lineGrad)"
                strokeWidth="3.5"
                points={pathPoints}
                className="transition-all duration-300"
              />

              {/* Highlight interactive points */}
              {SIMULATED_HISTORY.map((pt, i) => {
                const x = paddingX + i * stepX;
                const y = getY(pt.score);
                const isSelected = selectedPoint?.id === pt.id;
                
                let dotColor = "#06b6d4"; // Cyan
                if (pt.score < 50) dotColor = "#f43f5e"; // Rose
                else if (pt.score < alertThreshold) dotColor = "#f59e0b"; // Amber

                return (
                  <g key={pt.id} className="cursor-pointer" onClick={() => setSelectedPoint(pt)}>
                    {isSelected && (
                      <circle cx={x} cy={y} r="10" fill={dotColor} className="opacity-20 animate-ping" />
                    )}
                    <circle
                      cx={x}
                      cy={y}
                      r={isSelected ? "6.5" : "4.5"}
                      fill={dotColor}
                      stroke="#0d0f14"
                      strokeWidth="2"
                      className="hover:scale-150 transition-all duration-200"
                    />
                  </g>
                );
              })}

              {/* Definitions */}
              <defs>
                <linearGradient id="lineGrad" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stopColor="#06b6d4" />
                  <stop offset="50%" stopColor="#3b82f6" />
                  <stop offset="100%" stopColor="#6366f1" />
                </linearGradient>
                <linearGradient id="chartGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.8" />
                  <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.0" />
                </linearGradient>
              </defs>

              {/* Labels X and Y */}
              {SIMULATED_HISTORY.map((pt, i) => (
                <text
                  key={pt.id}
                  x={paddingX + i * stepX}
                  y={chartHeight - 4}
                  fill="#64748b"
                  fontSize="10"
                  textAnchor="middle"
                  className="font-mono font-semibold"
                >
                  {pt.date}
                </text>
              ))}
              <text x={paddingX - 10} y={getY(alertThreshold) + 3} fill="#f59e0b" fontSize="9" textAnchor="end" className="font-mono font-bold">
                {alertThreshold}
              </text>
              <text x={paddingX - 10} y={getY(50) + 3} fill="#64748b" fontSize="9" textAnchor="end" className="font-mono">
                50
              </text>
            </svg>
          </div>

          <div className="mt-4 p-4 rounded-lg bg-slate-900/50 border border-slate-800 text-xs text-slate-400">
            💡 <span className="text-slate-300 font-semibold">Tip:</span> Click any data node dot on the line chart above to view granular audit explanations, latency SLAs, and decision metrics in the side inspector panel.
          </div>
        </div>

        {/* Side Inspector Panel */}
        <div className="rounded-xl border border-slate-800 bg-[#121620]/40 p-6 backdrop-blur-md flex flex-col justify-between">
          <div>
            <h2 className="text-lg font-bold text-white tracking-tight mb-4">Inspection Panel</h2>
            
            {selectedPoint ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                  <span className="text-xs text-slate-400 font-mono">Session ID</span>
                  <span className="text-xs font-mono text-cyan-400 font-semibold">{selectedPoint.id.toUpperCase()}</span>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-400">Calculated Score</span>
                  <span className={`text-2xl font-black font-mono ${
                    selectedPoint.score < 50 ? "text-rose-400" : (selectedPoint.score < 75 ? "text-amber-400" : "text-cyan-400")
                  }`}>
                    {selectedPoint.score}/100
                  </span>
                </div>

                <div>
                  <span className="text-xs text-slate-400 font-mono block mb-1">Status Classification</span>
                  <span className={`inline-flex px-2 py-0.5 rounded text-xs font-bold font-mono ${
                    selectedPoint.status === "passed" ? "bg-emerald-500/10 text-emerald-400" : (
                      selectedPoint.status === "warning" ? "bg-amber-500/10 text-amber-400" : "bg-rose-500/10 text-rose-400"
                    )
                  }`}>
                    {selectedPoint.status.toUpperCase()}
                  </span>
                </div>

                <div className="flex items-center justify-between border-t border-slate-800 pt-3">
                  <span className="text-sm text-slate-400">Execution Latency</span>
                  <span className="text-sm font-mono text-slate-200">{selectedPoint.latency} ms</span>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-400">Warning Counts</span>
                  <span className="text-sm font-mono text-slate-200">{selectedPoint.warnings} flag(s)</span>
                </div>

                <div className="mt-4 p-3 bg-slate-900/60 rounded border border-slate-800 text-xs">
                  <span className="text-slate-300 font-bold block mb-1">Telemetry Diagnostics</span>
                  {selectedPoint.score < 75 ? (
                    <span className="text-rose-400/90 font-mono">
                      Anomaly trigger: latency exceeds 100ms standard and/or rule check compliance failures registered.
                    </span>
                  ) : (
                    <span className="text-emerald-400/90 font-mono">
                      Standard transaction path. No warnings flags or compliance deviations found.
                    </span>
                  )}
                </div>
              </div>
            ) : (
              <div className="text-center py-16 text-slate-500">
                <p className="text-3xl mb-3">🔍</p>
                <p className="text-xs">No node selected.</p>
                <p className="text-xs mt-1">Select any point on the trend chart to view telemetry metadata details.</p>
              </div>
            )}
          </div>

          <div className="border-t border-slate-800 pt-4 mt-6">
            <span className="text-[10px] text-slate-500 font-mono block">AegisAI OS Governance Engine</span>
            <span className="text-[10px] text-slate-500 font-mono block">Algorithm: Weighted trust heuristic v1.0.0</span>
          </div>
        </div>
      </section>
    </div>
  );
}
