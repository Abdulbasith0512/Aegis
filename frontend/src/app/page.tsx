import React from "react";
import Link from "next/link";
import { 
  ShieldCheck, Search, FileText, Scale, UserCheck, 
  Terminal, ZapOff, HeartPulse, MessageSquareCode, Network, ArrowRight
} from "lucide-react";

/*
 * FLAGSHIP COMPONENT SELECTION RATIONALE:
 * We deliberately feature "Trust Score Telemetry" and "Human Review Center" as the two primary
 * flagship modules (spanning double columns with active data modules).
 * Together, they demonstrate the core loop of AegisAI OS:
 * 1. The automated real-time Trust Engine assessment (Trust Score Telemetry).
 * 2. The human-in-the-loop compliance override and final case resolution (Human Review Center).
 * This machine-intelligence-to-human-verification cycle represents the core product flow.
 */

export default function Home() {
  const gridBgStyle = {
    backgroundImage: "linear-gradient(to right, rgba(255,255,255,0.015) 1px, transparent 1px), linear-gradient(to bottom, rgba(255,255,255,0.015) 1px, transparent 1px)",
    backgroundSize: "40px 40px"
  };

  return (
    <div 
      className="min-h-screen bg-[#0a0c10] text-[#e2e8f0] font-sans antialiased p-6 md:p-12 flex flex-col justify-between selection:bg-emerald-500 selection:text-slate-950 relative border-t-4 border-emerald-500"
      style={gridBgStyle}
    >
      {/* Background glow effects - tightened and toned down */}
      <div className="absolute top-0 left-1/4 h-[300px] w-[300px] rounded-full bg-emerald-500/3 blur-[120px] pointer-events-none"></div>

      {/* Top Navbar Header */}
      <header className="relative flex items-center justify-between border-b border-slate-800/80 pb-6 mb-12">
        <div className="flex items-center gap-3">
          <span className="h-6 w-6 rounded bg-emerald-500 flex items-center justify-center font-mono font-bold text-xs text-slate-950">
            Æ
          </span>
          <span className="text-base font-black tracking-wider uppercase text-white font-mono">
            AegisAI OS
          </span>
        </div>
        <div className="flex items-center gap-2 font-mono">
          <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span className="text-[10px] uppercase font-bold tracking-widest text-emerald-400">
            SECURE LEDGER ONLINE
          </span>
        </div>
      </header>

      {/* Hero Welcome Panel */}
      <main className="relative flex-1 flex flex-col items-center justify-center text-center max-w-7xl mx-auto my-12 w-full">
        {/* Compliance Certification Status Line */}
        <div className="inline-flex items-center gap-2.5 px-4 py-1.5 rounded border border-slate-800 bg-slate-950/80 mb-8 font-mono text-[11px] uppercase tracking-wider text-slate-400">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-500"></span>
          SOC 2 Type II Certified &bull; RBI Circular G-20 Compliant
        </div>

        <h1 className="text-4xl sm:text-6xl font-black tracking-tight leading-[1.15] text-white mb-6 max-w-4xl">
          AI Governance Operating System
          <span className="block mt-2 text-white">
            Supervising <span className="font-mono font-extrabold text-slate-200">[Banking Agents]</span>.
          </span>
        </h1>

        <p className="text-sm sm:text-base text-slate-400 max-w-2xl mb-10 leading-relaxed">
          The unified control plane for RBI-regulated autonomous financial networks. Monitor weighted trust scores, audit SHAP feature attributions, enforce hard compliance parameters, and verify WORM log sequences.
        </p>

        {/* Action Button */}
        <div className="mb-10">
          <Link href="/dashboard" className="inline-flex items-center gap-2 px-8 py-3.5 rounded bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-mono font-bold text-xs uppercase tracking-wider transition-all duration-200 shadow-[0_4px_12px_rgba(16,185,129,0.25)] hover:shadow-[0_4px_20px_rgba(16,185,129,0.35)]">
            Launch Operations Dashboard Console
          </Link>
        </div>

        {/* Substantive Audit Performance Indicators */}
        <div className="flex flex-wrap justify-center items-center gap-x-8 gap-y-4 mb-16 text-slate-500 font-mono text-[10px] uppercase tracking-widest">
          <span>Active Ledgers: Pristine</span>
          <span className="text-slate-800">|</span>
          <span>4,200 DECISIONS / DAY</span>
          <span className="text-slate-800">|</span>
          <span>Consensus Uptime: 99.98%</span>
        </div>

        {/* Dashboards Access Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full">
          {/* Card 1: Trust Telemetry (Primary - Highlighted) - Indigo Theme */}
          <Link href="/trust-dashboard" className="group md:col-span-2">
            <div className="h-full rounded border border-slate-800 bg-slate-900/10 hover:border-slate-700 hover:bg-slate-900/20 p-6 backdrop-blur-md text-left transition-all duration-200 flex flex-col justify-between">
              <div>
                <div className="flex justify-between items-start mb-5">
                  <div className="h-9 w-9 rounded border border-indigo-500/20 bg-indigo-500/5 flex items-center justify-center text-indigo-400 group-hover:border-indigo-400/40 transition-all duration-300">
                    <ShieldCheck size={16} />
                  </div>
                  <div className="flex items-center gap-1.5 font-mono text-[9px] text-emerald-400 bg-emerald-950/40 border border-emerald-500/20 px-2 py-0.5 rounded">
                    <span className="h-1.5 w-1.5 rounded-full bg-emerald-500"></span>
                    ACTIVE FEED
                  </div>
                </div>
                <h3 className="text-lg font-bold text-white mb-2">Trust Score Telemetry</h3>
                <p className="text-xs text-slate-400 leading-relaxed mb-6">
                  Monitor the real-time weighted trust index mapping accuracy, consensus, and latency metrics across the banking network.
                </p>
                
                {/* Embedded Live Monospace Telemetry Block - High Contrast */}
                <div className="p-4 rounded bg-[#030712] border border-slate-700/80 font-mono text-xs space-y-2.5 mb-6">
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400 text-[10px] tracking-wider uppercase font-semibold">NETWORK WEIGHTED TRUST:</span>
                    <span className="text-emerald-400 font-bold text-sm">94.2 / 100</span>
                  </div>
                  <div className="w-full bg-slate-900 h-1.5 rounded overflow-hidden">
                    <div className="bg-emerald-500 h-full w-[94.2%]"></div>
                  </div>
                  <div className="flex justify-between text-[9px] text-slate-300 pt-1">
                    <span>SLA VERDICT: <strong className="text-emerald-400">APPROVED</strong></span>
                    <span>INFERENCE LATENCY: <strong className="text-white">12.5 MS</strong></span>
                  </div>
                </div>
              </div>
              <span className="text-[10px] font-mono font-bold text-slate-500 group-hover:text-emerald-400 transition-colors duration-200 inline-flex items-center gap-1.5 mt-auto uppercase tracking-wider">
                Enter Console <ArrowRight size={12} className="group-hover:translate-x-1 transition-transform duration-200" />
              </span>
            </div>
          </Link>

          {/* Card 2: Explainability Portal (Secondary) - Indigo Theme */}
          <Link href="/explainability" className="group">
            <div className="h-full rounded border border-slate-800 bg-slate-900/10 hover:border-slate-700 hover:bg-slate-900/20 p-6 backdrop-blur-md text-left transition-all duration-200 flex flex-col justify-between">
              <div>
                <div className="h-9 w-9 rounded border border-indigo-500/20 bg-indigo-500/5 flex items-center justify-center text-indigo-400 group-hover:border-indigo-400/40 transition-all duration-300 mb-5">
                  <Search size={16} />
                </div>
                <h3 className="text-lg font-bold text-white mb-2">Explainability Diagnostics</h3>
                <p className="text-xs text-slate-400 leading-relaxed mb-6">
                  Inspect SHAP attribution graphs, check rules compliance checks, and trace topological evidence timelines for decision audits.
                </p>
              </div>
              <span className="text-[10px] font-mono font-bold text-slate-500 group-hover:text-emerald-400 transition-colors duration-200 inline-flex items-center gap-1.5 mt-auto uppercase tracking-wider">
                Enter Console <ArrowRight size={12} className="group-hover:translate-x-1 transition-transform duration-200" />
              </span>
            </div>
          </Link>

          {/* Card 3: Policy Engine (Secondary) - Emerald Theme */}
          <Link href="/policy-dashboard" className="group">
            <div className="h-full rounded border border-slate-800 bg-slate-900/10 hover:border-slate-700 hover:bg-slate-900/20 p-6 backdrop-blur-md text-left transition-all duration-200 flex flex-col justify-between">
              <div>
                <div className="flex justify-between items-start mb-5">
                  <div className="h-9 w-9 rounded border border-emerald-500/20 bg-emerald-500/5 flex items-center justify-center text-emerald-400 group-hover:border-emerald-400/40 transition-all duration-300">
                    <FileText size={16} />
                  </div>
                  <span className="font-mono text-[9px] text-emerald-400 bg-slate-950/80 px-2 py-0.5 rounded border border-slate-800">
                    14 RULES ACTIVE
                  </span>
                </div>
                <h3 className="text-lg font-bold text-white mb-2">Policy Engine</h3>
                <p className="text-xs text-slate-400 leading-relaxed mb-6">
                  Enforce Reserve Bank guidelines (RBI), anti-money laundering (AML) checks, and register manual overrides.
                </p>
              </div>
              <span className="text-[10px] font-mono font-bold text-slate-500 group-hover:text-emerald-400 transition-colors duration-200 inline-flex items-center gap-1.5 mt-auto uppercase tracking-wider">
                Enter Console <ArrowRight size={12} className="group-hover:translate-x-1 transition-transform duration-200" />
              </span>
            </div>
          </Link>

          {/* Card 4: Human Review Center (Primary - Highlighted) - Emerald Theme */}
          <Link href="/reviews" className="group md:col-span-2">
            <div className="h-full rounded border border-slate-800 bg-slate-900/10 hover:border-slate-700 hover:bg-slate-900/20 p-6 backdrop-blur-md text-left transition-all duration-200 flex flex-col justify-between">
              <div>
                <div className="flex justify-between items-start mb-5">
                  <div className="h-9 w-9 rounded border border-emerald-500/20 bg-emerald-500/5 flex items-center justify-center text-emerald-400 group-hover:border-emerald-400/40 transition-all duration-300">
                    <UserCheck size={16} />
                  </div>
                  <div className="flex items-center gap-1.5 font-mono text-[9px] text-rose-400 bg-rose-950/40 border border-rose-500/20 px-2 py-0.5 rounded">
                    <span className="h-1.5 w-1.5 rounded-full bg-rose-500 animate-pulse"></span>
                    ACTION REQUIRED
                  </div>
                </div>
                <h3 className="text-lg font-bold text-white mb-2">Human Review Center</h3>
                <p className="text-xs text-slate-400 leading-relaxed mb-6">
                  Audit case queues, verify SHAP feature attributions and nested regulatory compliance rule checks, and submit verdicts.
                </p>

                {/* Embedded Live Monospace Telemetry Block - High Contrast */}
                <div className="p-4 rounded bg-[#030712] border border-slate-700/80 font-mono text-xs space-y-2.5 mb-6">
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400 text-[10px] tracking-wider uppercase font-semibold">ACTIVE AUDIT QUEUE:</span>
                    <span className="px-2 py-0.5 rounded bg-rose-950 text-rose-400 border border-rose-500/30 text-[9px] font-bold">3 PENDING</span>
                  </div>
                  <div className="text-[10px] text-slate-300 space-y-2 pt-1">
                    <div className="flex justify-between border-b border-slate-900 pb-1.5">
                      <span>&bull; TX-7A912 (Score: <strong className="text-rose-400">62.4</strong>)</span>
                      <span>SLA: <strong className="text-white">12 MINS</strong></span>
                    </div>
                    <div className="flex justify-between">
                      <span>&bull; TX-3E181 (AML flagged skews)</span>
                      <span>SLA: <strong className="text-white">48 MINS</strong></span>
                    </div>
                  </div>
                </div>
              </div>
              <span className="text-[10px] font-mono font-bold text-slate-500 group-hover:text-emerald-400 transition-colors duration-200 inline-flex items-center gap-1.5 mt-auto uppercase tracking-wider">
                Enter Console <ArrowRight size={12} className="group-hover:translate-x-1 transition-transform duration-200" />
              </span>
            </div>
          </Link>

          {/* Card 5: AI Consensus Engine (Secondary) - Emerald Theme */}
          <Link href="/consensus-dashboard" className="group">
            <div className="h-full rounded border border-slate-800 bg-slate-900/10 hover:border-slate-700 hover:bg-slate-900/20 p-6 backdrop-blur-md text-left transition-all duration-200 flex flex-col justify-between">
              <div>
                <div className="flex justify-between items-start mb-5">
                  <div className="h-9 w-9 rounded border border-emerald-500/20 bg-emerald-500/5 flex items-center justify-center text-emerald-400 group-hover:border-emerald-400/40 transition-all duration-300">
                    <Scale size={16} />
                  </div>
                  <div className="flex items-center gap-1 font-mono text-[9px] text-emerald-400">
                    <span className="h-1.5 w-1.5 rounded-full bg-emerald-500"></span>
                    ONLINE
                  </div>
                </div>
                <h3 className="text-lg font-bold text-white mb-2">AI Consensus Engine</h3>
                <p className="text-xs text-slate-400 leading-relaxed mb-6">
                  Verify multi-agent confidence aggregations, monitor node reputations, and audit regulatory compliance overrides.
                </p>
              </div>
              <span className="text-[10px] font-mono font-bold text-slate-500 group-hover:text-emerald-400 transition-colors duration-200 inline-flex items-center gap-1.5 mt-auto uppercase tracking-wider">
                Enter Console <ArrowRight size={12} className="group-hover:translate-x-1 transition-transform duration-200" />
              </span>
            </div>
          </Link>

          {/* Card 6: Observability Platform (Secondary) - Cyan Theme */}
          <Link href="/observability" className="group">
            <div className="h-full rounded border border-slate-800 bg-slate-900/10 hover:border-slate-700 hover:bg-slate-900/20 p-6 backdrop-blur-md text-left transition-all duration-200 flex flex-col justify-between">
              <div>
                <div className="flex justify-between items-start mb-5">
                  <div className="h-9 w-9 rounded border border-cyan-500/20 bg-cyan-500/5 flex items-center justify-center text-cyan-400 group-hover:border-cyan-400/40 transition-all duration-300">
                    <Terminal size={16} />
                  </div>
                  <span className="font-mono text-[9px] text-cyan-400 bg-slate-950/80 px-2 py-0.5 rounded border border-slate-800">
                    1.2M TOKENS
                  </span>
                </div>
                <h3 className="text-lg font-bold text-white mb-2">Observability Platform</h3>
                <p className="text-xs text-slate-400 leading-relaxed mb-6">
                  Track real-time hardware metrics, token spends, hallucination gauges, and query Grafana alerts.
                </p>
              </div>
              <span className="text-[10px] font-mono font-bold text-slate-500 group-hover:text-emerald-400 transition-colors duration-200 inline-flex items-center gap-1.5 mt-auto uppercase tracking-wider">
                Enter Console <ArrowRight size={12} className="group-hover:translate-x-1 transition-transform duration-200" />
              </span>
            </div>
          </Link>

          {/* Card 7: Chaos Engineering (Secondary) - Cyan Theme */}
          <Link href="/chaos-dashboard" className="group">
            <div className="h-full rounded border border-slate-800 bg-slate-900/10 hover:border-slate-700 hover:bg-slate-900/20 p-6 backdrop-blur-md text-left transition-all duration-200 flex flex-col justify-between">
              <div>
                <div className="flex justify-between items-start mb-5">
                  <div className="h-9 w-9 rounded border border-cyan-500/20 bg-cyan-500/5 flex items-center justify-center text-cyan-400 group-hover:border-cyan-400/40 transition-all duration-300">
                    <ZapOff size={16} />
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className="h-1.5 w-1.5 rounded-full bg-amber-500"></span>
                    <span className="font-mono text-[9px] text-amber-400">3 ACTIVE RUNS</span>
                  </div>
                </div>
                <h3 className="text-lg font-bold text-white mb-2">Chaos Engineering</h3>
                <p className="text-xs text-slate-400 leading-relaxed mb-6">
                  Inject database/Redis fails, target delays, and verify recovery times and trust score drop indexes.
                </p>
              </div>
              <span className="text-[10px] font-mono font-bold text-slate-500 group-hover:text-emerald-400 transition-colors duration-200 inline-flex items-center gap-1.5 mt-auto uppercase tracking-wider">
                Enter Console <ArrowRight size={12} className="group-hover:translate-x-1 transition-transform duration-200" />
              </span>
            </div>
          </Link>

          {/* Card 8: Self-Healing (Secondary) - Cyan Theme */}
          <Link href="/self-healing" className="group">
            <div className="h-full rounded border border-slate-800 bg-slate-900/10 hover:border-slate-700 hover:bg-slate-900/20 p-6 backdrop-blur-md text-left transition-all duration-200 flex flex-col justify-between">
              <div>
                <div className="flex justify-between items-start mb-5">
                  <div className="h-9 w-9 rounded border border-cyan-500/20 bg-cyan-500/5 flex items-center justify-center text-cyan-400 group-hover:border-cyan-400/40 transition-all duration-300">
                    <HeartPulse size={16} />
                  </div>
                  <span className="font-mono text-[9px] text-cyan-400 bg-slate-950/80 px-2 py-0.5 rounded border border-slate-800">
                    99.98% SLA
                  </span>
                </div>
                <h3 className="text-lg font-bold text-white mb-2">Self-Healing</h3>
                <p className="text-xs text-slate-400 leading-relaxed mb-6">
                  Track automated failover workflows, switch backup models, rollbacks, and recovery timeline flowchart states.
                </p>
              </div>
              <span className="text-[10px] font-mono font-bold text-slate-500 group-hover:text-emerald-400 transition-colors duration-200 inline-flex items-center gap-1.5 mt-auto uppercase tracking-wider">
                Enter Console <ArrowRight size={12} className="group-hover:translate-x-1 transition-transform duration-200" />
              </span>
            </div>
          </Link>

          {/* Card 9: Regulatory Copilot (Secondary) - Emerald Theme */}
          <Link href="/copilot" className="group">
            <div className="h-full rounded border border-slate-800 bg-slate-900/10 hover:border-slate-700 hover:bg-slate-900/20 p-6 backdrop-blur-md text-left transition-all duration-200 flex flex-col justify-between">
              <div>
                <div className="flex justify-between items-start mb-5">
                  <div className="h-9 w-9 rounded border border-emerald-500/20 bg-emerald-500/5 flex items-center justify-center text-emerald-400 group-hover:border-emerald-400/40 transition-all duration-300">
                    <MessageSquareCode size={16} />
                  </div>
                  <span className="font-mono text-[9px] text-emerald-400 bg-slate-950/80 px-2 py-0.5 rounded border border-slate-800">
                    12 FILINGS
                  </span>
                </div>
                <h3 className="text-lg font-bold text-white mb-2">Regulatory Copilot</h3>
                <p className="text-xs text-slate-400 leading-relaxed mb-6">
                  Ask compliance questions, analyze violations, drift events, and export printable RBI and audit reports.
                </p>
              </div>
              <span className="text-[10px] font-mono font-bold text-slate-500 group-hover:text-emerald-400 transition-colors duration-200 inline-flex items-center gap-1.5 mt-auto uppercase tracking-wider">
                Enter Console <ArrowRight size={12} className="group-hover:translate-x-1 transition-transform duration-200" />
              </span>
            </div>
          </Link>

          {/* Card 10: Neo4j Knowledge Graph (Secondary) - Indigo Theme */}
          <Link href="/knowledge-graph" className="group">
            <div className="h-full rounded border border-slate-800 bg-slate-900/10 hover:border-slate-700 hover:bg-slate-900/20 p-6 backdrop-blur-md text-left transition-all duration-200 flex flex-col justify-between">
              <div>
                <div className="flex justify-between items-start mb-5">
                  <div className="h-9 w-9 rounded border border-indigo-500/20 bg-indigo-500/5 flex items-center justify-center text-indigo-400 group-hover:border-indigo-400/40 transition-all duration-300">
                    <Network size={16} />
                  </div>
                  <span className="font-mono text-[9px] text-indigo-400 bg-slate-950/80 px-2 py-0.5 rounded border border-slate-800">
                    48K ENTITIES
                  </span>
                </div>
                <h3 className="text-lg font-bold text-white mb-2">Knowledge Graph</h3>
                <p className="text-xs text-slate-400 leading-relaxed mb-6">
                  Visualize accounts relationships, Circular circular transfer loops, and shortest path pathfindings.
                </p>
              </div>
              <span className="text-[10px] font-mono font-bold text-slate-500 group-hover:text-emerald-400 transition-colors duration-200 inline-flex items-center gap-1.5 mt-auto uppercase tracking-wider">
                Enter Console <ArrowRight size={12} className="group-hover:translate-x-1 transition-transform duration-200" />
              </span>
            </div>
          </Link>
        </div>
      </main>

      {/* Footer copyright */}
      <footer className="relative border-t border-slate-900 pt-6 mt-12 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-4">
        <p>&copy; 2026 AegisAI OS. WORM-compliant banking audit ledger active.</p>
        <div className="flex gap-4 font-mono text-[10px] tracking-widest uppercase">
          <span className="text-emerald-400">PostgreSQL: connected</span>
          <span className="text-emerald-400">Redis: connected</span>
        </div>
      </footer>
    </div>
  );
}
