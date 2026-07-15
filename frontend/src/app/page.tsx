import React from "react";
import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-[#0d0f14] text-[#e2e8f0] font-sans antialiased p-6 md:p-12 flex flex-col justify-between selection:bg-indigo-500 selection:text-white">
      {/* Background glow effects */}
      <div className="absolute top-0 left-1/4 h-[350px] w-[350px] rounded-full bg-indigo-500/5 blur-3xl"></div>
      <div className="absolute bottom-10 right-1/4 h-[350px] w-[350px] rounded-full bg-cyan-500/5 blur-3xl"></div>

      {/* Top Navbar Header */}
      <header className="relative flex items-center justify-between border-b border-slate-800/80 pb-6 mb-12">
        <div className="flex items-center gap-3">
          <span className="h-6 w-6 rounded bg-gradient-to-tr from-indigo-500 to-cyan-400 flex items-center justify-center font-mono font-bold text-xs text-white">
            Æ
          </span>
          <span className="text-lg font-black tracking-wider uppercase text-white font-mono">
            AegisAI OS
          </span>
        </div>
        <div className="flex items-center gap-1">
          <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span className="text-[10px] uppercase font-bold tracking-widest text-slate-400 font-mono">
            System Online
          </span>
        </div>
      </header>

      {/* Hero Welcome Panel */}
      <main className="relative flex-1 flex flex-col items-center justify-center text-center max-w-4xl mx-auto my-12">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-slate-800 bg-[#121620]/80 mb-6">
          <span className="text-[10px] uppercase font-bold tracking-widest text-indigo-400 font-mono">
            Release v1.0.0 Stable
          </span>
        </div>

        <h1 className="text-4xl sm:text-6xl font-black tracking-tight leading-none text-white mb-6">
          AI Governance Operating System
          <span className="block mt-2 text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-cyan-400 to-emerald-400">
            Supervising Banking Agents.
          </span>
        </h1>

        <p className="text-base sm:text-lg text-slate-400 max-w-2xl mb-12 leading-relaxed">
          Supervises, validates, explains, and secures machine learning decisions inside financial banking infrastructures. Built on Clean Architecture and LangGraph workflows.
        </p>

        {/* Dashboards Access Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 w-full max-w-7xl">
          {/* Card 1: Trust Telemetry */}
          <Link href="/trust-dashboard" className="group">
            <div className="h-full rounded-2xl border border-slate-800 bg-[#121620]/40 p-8 backdrop-blur-md text-left transition-all duration-300 hover:border-cyan-500 hover:bg-[#121620]/60 hover:shadow-[0_0_20px_rgba(6,182,212,0.15)] flex flex-col justify-between">
              <div>
                <div className="h-10 w-10 rounded-lg bg-cyan-500/10 flex items-center justify-center text-cyan-400 mb-6 font-mono text-lg group-hover:scale-110 transition-all duration-300">
                  📊
                </div>
                <h3 className="text-xl font-bold text-white mb-2">Trust Score Telemetry</h3>
                <p className="text-xs text-slate-400 leading-relaxed mb-6">
                  Monitor the real-time weighted trust index mapping accuracy, consensus, and latency metrics across the banking network.
                </p>
              </div>
              <span className="text-xs font-mono font-bold text-cyan-400 group-hover:translate-x-2 transition-all duration-300 inline-flex items-center gap-1">
                Enter Console →
              </span>
            </div>
          </Link>

          {/* Card 2: Explainability Portal */}
          <Link href="/explainability" className="group">
            <div className="h-full rounded-2xl border border-slate-800 bg-[#121620]/40 p-8 backdrop-blur-md text-left transition-all duration-300 hover:border-indigo-500 hover:bg-[#121620]/60 hover:shadow-[0_0_20px_rgba(99,102,241,0.15)] flex flex-col justify-between">
              <div>
                <div className="h-10 w-10 rounded-lg bg-indigo-500/10 flex items-center justify-center text-indigo-400 mb-6 font-mono text-lg group-hover:scale-110 transition-all duration-300">
                  🔍
                </div>
                <h3 className="text-xl font-bold text-white mb-2">Explainability Diagnostics</h3>
                <p className="text-xs text-slate-400 leading-relaxed mb-6">
                  Inspect SHAP attribution graphs, check rules compliance checks, and trace topological evidence timelines for decision audits.
                </p>
              </div>
              <span className="text-xs font-mono font-bold text-indigo-400 group-hover:translate-x-2 transition-all duration-300 inline-flex items-center gap-1">
                Enter Console →
              </span>
            </div>
          </Link>

          {/* Card 3: Compliance Portal */}
          <Link href="/policy-dashboard" className="group">
            <div className="h-full rounded-2xl border border-slate-800 bg-[#121620]/40 p-8 backdrop-blur-md text-left transition-all duration-300 hover:border-emerald-500 hover:bg-[#121620]/60 hover:shadow-[0_0_20px_rgba(16,185,129,0.15)] flex flex-col justify-between">
              <div>
                <div className="h-10 w-10 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-400 mb-6 font-mono text-lg group-hover:scale-110 transition-all duration-300">
                  🛡️
                </div>
                <h3 className="text-xl font-bold text-white mb-2">Policy Engine</h3>
                <p className="text-xs text-slate-400 leading-relaxed mb-6">
                  Enforce Reserve Bank guidelines (RBI), anti-money laundering (AML) checks, and register manual overrides.
                </p>
              </div>
              <span className="text-xs font-mono font-bold text-emerald-400 group-hover:translate-x-2 transition-all duration-300 inline-flex items-center gap-1">
                Enter Console →
              </span>
            </div>
          </Link>

          {/* Card 4: Consensus Engine */}
          <Link href="/consensus-dashboard" className="group">
            <div className="h-full rounded-2xl border border-slate-800 bg-[#121620]/40 p-8 backdrop-blur-md text-left transition-all duration-300 hover:border-violet-500 hover:bg-[#121620]/60 hover:shadow-[0_0_20px_rgba(139,92,246,0.15)] flex flex-col justify-between">
              <div>
                <div className="h-10 w-10 rounded-lg bg-violet-500/10 flex items-center justify-center text-violet-400 mb-6 font-mono text-lg group-hover:scale-110 transition-all duration-300">
                  ⚖️
                </div>
                <h3 className="text-xl font-bold text-white mb-2">AI Consensus Engine</h3>
                <p className="text-xs text-slate-400 leading-relaxed mb-6">
                  Verify multi-agent confidence aggregations, monitor node reputations, and audit regulatory compliance overrides.
                </p>
              </div>
              <span className="text-xs font-mono font-bold text-violet-400 group-hover:translate-x-2 transition-all duration-300 inline-flex items-center gap-1">
                Enter Console →
              </span>
            </div>
          </Link>

          {/* Card 5: Human Review Center */}
          <Link href="/reviews" className="group">
            <div className="h-full rounded-2xl border border-slate-800 bg-[#121620]/40 p-8 backdrop-blur-md text-left transition-all duration-300 hover:border-rose-500 hover:bg-[#121620]/60 hover:shadow-[0_0_20px_rgba(244,63,94,0.15)] flex flex-col justify-between">
              <div>
                <div className="h-10 w-10 rounded-lg bg-rose-500/10 flex items-center justify-center text-rose-400 mb-6 font-mono text-lg group-hover:scale-110 transition-all duration-300">
                  🛡️
                </div>
                <h3 className="text-xl font-bold text-white mb-2">Human Review Center</h3>
                <p className="text-xs text-slate-400 leading-relaxed mb-6">
                  Audit case queues, verify SHAP feature attributions and nested regulatory compliance rule checks, and submit verdicts.
                </p>
              </div>
              <span className="text-xs font-mono font-bold text-rose-400 group-hover:translate-x-2 transition-all duration-300 inline-flex items-center gap-1">
                Enter Console →
              </span>
            </div>
          </Link>

          {/* Card 6: Observability Platform */}
          <Link href="/observability" className="group">
            <div className="h-full rounded-2xl border border-slate-800 bg-[#121620]/40 p-8 backdrop-blur-md text-left transition-all duration-300 hover:border-cyan-500 hover:bg-[#121620]/60 hover:shadow-[0_0_20px_rgba(6,182,212,0.15)] flex flex-col justify-between">
              <div>
                <div className="h-10 w-10 rounded-lg bg-cyan-500/10 flex items-center justify-center text-cyan-400 mb-6 font-mono text-lg group-hover:scale-110 transition-all duration-300">
                  ⚡
                </div>
                <h3 className="text-xl font-bold text-white mb-2">Observability Platform</h3>
                <p className="text-xs text-slate-400 leading-relaxed mb-6">
                  Track real-time hardware metrics, token spends, hallucination gauges, and query Grafana alerts.
                </p>
              </div>
              <span className="text-xs font-mono font-bold text-cyan-400 group-hover:translate-x-2 transition-all duration-300 inline-flex items-center gap-1">
                Enter Console →
              </span>
            </div>
          </Link>

          {/* Card 7: Chaos Engineering Engine */}
          <Link href="/chaos-dashboard" className="group">
            <div className="h-full rounded-2xl border border-slate-800 bg-[#121620]/40 p-8 backdrop-blur-md text-left transition-all duration-300 hover:border-amber-500 hover:bg-[#121620]/60 hover:shadow-[0_0_20px_rgba(245,158,11,0.15)] flex flex-col justify-between">
              <div>
                <div className="h-10 w-10 rounded-lg bg-amber-500/10 flex items-center justify-center text-amber-400 mb-6 font-mono text-lg group-hover:scale-110 transition-all duration-300">
                  💥
                </div>
                <h3 className="text-xl font-bold text-white mb-2">Chaos Engineering</h3>
                <p className="text-xs text-slate-400 leading-relaxed mb-6">
                  Inject database/Redis fails, target delays, and verify recovery times and trust score drop indexes.
                </p>
              </div>
              <span className="text-xs font-mono font-bold text-amber-400 group-hover:translate-x-2 transition-all duration-300 inline-flex items-center gap-1">
                Enter Console →
              </span>
            </div>
          </Link>

          {/* Card 8: Self-Healing Engine */}
          <Link href="/self-healing" className="group">
            <div className="h-full rounded-2xl border border-slate-800 bg-[#121620]/40 p-8 backdrop-blur-md text-left transition-all duration-300 hover:border-emerald-500 hover:bg-[#121620]/60 hover:shadow-[0_0_20px_rgba(16,185,129,0.15)] flex flex-col justify-between">
              <div>
                <div className="h-10 w-10 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-400 mb-6 font-mono text-lg group-hover:scale-110 transition-all duration-300">
                  🩹
                </div>
                <h3 className="text-xl font-bold text-white mb-2">Self-Healing</h3>
                <p className="text-xs text-slate-400 leading-relaxed mb-6">
                  Track automated failover workflows, switch backup models, rollbacks, and recovery timeline flowchart states.
                </p>
              </div>
              <span className="text-xs font-mono font-bold text-emerald-400 group-hover:translate-x-2 transition-all duration-300 inline-flex items-center gap-1">
                Enter Console →
              </span>
            </div>
          </Link>
        </div>
      </main>

      {/* Footer copyright */}
      <footer className="relative border-t border-slate-900 pt-6 mt-12 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-4">
        <p>© 2026 AegisAI OS. WORM-compliant banking audit ledger active.</p>
        <div className="flex gap-4 font-mono">
          <span className="text-[#10b981]">PostgreSQL: connected</span>
          <span className="text-[#10b981]">Redis: connected</span>
        </div>
      </footer>
    </div>
  );
}
