"use client";

import React, { useState } from "react";

interface CopilotMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: string[];
  hasReport?: boolean;
}

interface ChatSession {
  id: string;
  title: string;
  messages: CopilotMessage[];
}

const PRESEEDED_SESSIONS: ChatSession[] = [
  {
    id: "session-1",
    title: "RBI Compliance Audit",
    messages: [
      { id: "m1", role: "user", content: "Generate RBI report." },
      {
        id: "m2",
        role: "assistant",
        content: "### RBI Regulatory Assessment Report Compiled\n\nI have retrieved the necessary parameters from our active PostgreSQL WORM audit ledger:\n\n- **Policy checks passing**: 100% compliance verified.\n- **Hash signature chain checks**: verified green (signature sequence intact).\n\nBelow is the printable assessment copy ready for export.",
        sources: ["Policy check logs #A9812", "Audit blockchain signatures table"],
        hasReport: true
      }
    ]
  },
  {
    id: "session-2",
    title: "AI Quality Drift Review",
    messages: [
      { id: "m3", role: "user", content: "List drift incidents." },
      {
        id: "m4",
        role: "assistant",
        content: "### Dynamic Self-Healing Drift Incidents\n\nI have queried the `healing_incidents` database:\n\n- **Logged drift failures**: 1 event recorded on `aml-agent` (drift 0.045 > 0.03 limits).\n- **Healing response workflow**: Switched agent model mapping from `v2.0.0-drift` to backup registry version `v1.1.5-stable` successfully.\n\nAll current network evaluators are online.",
        sources: ["Healing Incidents queue logs", "Backup Model version mappings"]
      }
    ]
  }
];

export default function RegulatoryCopilot() {
  const [sessions, setSessions] = useState<ChatSession[]>(PRESEEDED_SESSIONS);
  const [activeSession, setActiveSession] = useState<ChatSession>(PRESEEDED_SESSIONS[0]);
  const [inputVal, setInputVal] = useState("");
  const [clickCount, setClickCount] = useState(0);

  const handleSend = (text: string) => {
    if (!text.trim()) return;

    const query = text.toLowerCase().trim();
    const nextCount = clickCount + 1;
    setClickCount(nextCount);
    
    // Create user message
    const userMsg: CopilotMessage = {
      id: `msg-usr-${nextCount}`,
      role: "user",
      content: text
    };

    // Formulate assistant response based on prompt
    let responseContent = "";
    let sources: string[] = [];
    let hasReport = false;

    if (query.includes("rbi")) {
      responseContent = "### RBI Compliance Report Draft Generated\n\nI have compiled the required compliance statistics from our active WORM ledger logs:\n- **Policy Conformity Rate**: 100% of analyzed inputs passed regulatory checks.\n- **Audit Hash Chain Integrity**: Confirmed cryptographic chaining checks verify zero alterations.\n\nA PDF-ready formatted copy has been compiled. You can export/download it using the button below.";
      sources = ["Compliance checks list table", "Cryptographic ledger hash index"];
      hasReport = true;
    } else if (query.includes("violation") || query.includes("policy")) {
      responseContent = "### Today's Policy Checks\n\nNo compliance check violations or AML failures have been recorded within the active ledger system today.\nAll dynamic consensus assessments returned clean green checkmarks.";
      sources = ["Policy check logs #A9812", "Audit blockchain signatures table"];
    } else if (query.includes("drift") || query.includes("incident")) {
      responseContent = "### Drift & Incident Status\n\nNo drift incidents or agent outages are logged in the active queue.\nThe Self-Healing Engine indicates 100% of agents are online.";
      sources = ["Healing Incidents queue logs", "Backup Model version mappings"];
    } else if (query.includes("health")) {
      responseContent = "### AI Agent Health Diagnostics\n\n- **Fraud Agent**: Healthy (Version v1.9.0-stable, Latency 18.2ms)\n- **AML Agent**: Healthy (Version v1.1.5-stable, Latency 22.4ms)\n- **Compliance Agent**: Healthy (Version v1.0.0-stable, Latency 12.2ms)\n\nTotal runtime consensus uptime is logged at **99.98%**.";
      sources = ["AI Observability Telemetry database"];
    } else if (query.includes("audit") || query.includes("report")) {
      responseContent = "### System Auditing Report Compiled\n\nI have compiled the system auditing history containing cryptographically chained hash block check logs:\n- **Chain Ledger Integrity**: Validated signature chains.\n- **Actor Actions Ledger**: All administrator interactions logged with valid tokens.\n\nYou can export/download the formatted report below.";
      sources = ["Cryptographic ledger hash index", "Audit Log Registry"];
      hasReport = true;
    } else {
      responseContent = "### Regulatory Copilot Advisor\n\nHello! I am your AI compliance companion. You can prompt me to:\n1. *Show today's policy violations*\n2. *Generate RBI report*\n3. *Explain transaction decisions*\n4. *List drift incidents*\n5. *Summarize AI health*\n6. *Generate audit report*";
    }

    const assistantMsg: CopilotMessage = {
      id: `msg-ast-${nextCount + 1}`,
      role: "assistant",
      content: responseContent,
      sources,
      hasReport
    };

    // Update session messages state
    const updatedSession = {
      ...activeSession,
      messages: [...activeSession.messages, userMsg, assistantMsg]
    };

    setActiveSession(updatedSession);
    setSessions(sessions.map(s => s.id === activeSession.id ? updatedSession : s));
    setInputVal("");
  };

  const startNewSession = () => {
    const nextCount = clickCount + 1;
    setClickCount(nextCount);
    
    const newSess: ChatSession = {
      id: `sess-${nextCount}`,
      title: `Audit Conversation #${sessions.length + 1}`,
      messages: [
        {
          id: `m-init-${nextCount}`,
          role: "assistant",
          content: "### Regulatory Copilot Advisor\n\nHello! I am your AI compliance companion. You can prompt me to:\n1. *Show today's policy violations*\n2. *Generate RBI report*\n3. *Explain transaction decisions*\n4. *List drift incidents*\n5. *Summarize AI health*\n6. *Generate audit report*"
        }
      ]
    };
    setSessions([newSess, ...sessions]);
    setActiveSession(newSess);
  };

  const downloadReportHTML = () => {
    // Generate and download a mock HTML report file representing the PDF-Ready output
    const reportContent = `
    <html>
    <body style="font-family: sans-serif; padding: 40px;">
      <h2>Regulatory Audit Assessment Report</h2>
      <hr/>
      <p>Report ID: EXP-REG-${activeSession.id.toUpperCase()}</p>
      <p>Compiled on: ${new Date().toISOString()}</p>
      <h3>Executive Summary</h3>
      <p>All core governance metrics passed evaluations with zero violations. Integrity checks verify WORM-ledger signature chains sequence intact.</p>
    </body>
    </html>
    `;
    const blob = new Blob([reportContent], { type: "text/html" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `AegisAI_Regulatory_Report_${activeSession.id}.html`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const quickPrompts = [
    "Show today's policy violations",
    "Generate RBI report",
    "Explain transaction decisions",
    "List drift incidents",
    "Summarize AI health",
    "Generate audit report"
  ];

  return (
    <div className="min-h-screen bg-[#0d0f14] text-[#e2e8f0] font-sans antialiased flex selection:bg-emerald-500 selection:text-white">
      {/* Sidebar: Sessions Threads list */}
      <aside className="w-80 border-r border-slate-800 bg-[#121620]/30 p-6 flex flex-col justify-between hidden md:flex backdrop-blur-md">
        <div className="space-y-6">
          <div className="flex items-center gap-2">
            <span className="h-2.5 w-2.5 rounded-full bg-emerald-500"></span>
            <span className="text-xs uppercase tracking-wider text-emerald-400 font-semibold font-mono">Copilot Advisor</span>
          </div>

          <button
            onClick={startNewSession}
            className="w-full py-2.5 rounded bg-slate-900 border border-slate-800 hover:border-emerald-500/50 hover:bg-slate-900/60 text-xs font-bold text-white uppercase tracking-wider font-mono transition-all duration-300"
          >
            + New Audit Chat
          </button>

          <div className="space-y-2 max-h-[450px] overflow-y-auto pr-1">
            {sessions.map((s) => (
              <div
                key={s.id}
                onClick={() => setActiveSession(s)}
                className={`p-3.5 rounded-lg border text-xs font-mono cursor-pointer transition-all duration-300 ${
                  activeSession.id === s.id
                    ? "bg-[#121620]/75 border-emerald-500 text-white shadow-[0_0_10px_rgba(16,185,129,0.05)]"
                    : "bg-slate-900/20 border-slate-800 text-slate-400 hover:text-slate-200"
                }`}
              >
                📝 {s.title}
              </div>
            ))}
          </div>
        </div>

        <div className="text-[10px] text-slate-500 font-mono">
          <span>AegisAI OS Copilot v1.0.0</span>
        </div>
      </aside>

      {/* Main chat viewport area */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden">
        
        {/* Top header stats bar */}
        <header className="border-b border-slate-800 bg-[#0d0f14]/80 p-6 backdrop-blur-md flex items-center justify-between">
          <div>
            <h1 className="text-xl font-black text-white">Regulatory Copilot</h1>
            <p className="text-xs text-slate-400 font-mono mt-0.5">Thread: {activeSession.title}</p>
          </div>
        </header>

        {/* Messages speech bubbles viewport */}
        <div className="flex-1 overflow-y-auto p-6 md:p-12 space-y-6">
          {activeSession.messages.map((m) => (
            <div
              key={m.id}
              className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-2xl p-5 rounded-xl border text-xs leading-relaxed ${
                  m.role === "user"
                    ? "bg-slate-900 border-slate-800 text-white font-mono"
                    : "bg-[#121620]/60 border-slate-850 text-slate-300"
                }`}
              >
                {/* Render response content */}
                <div className="prose prose-invert text-xs mb-4">
                  {m.content.split("\n\n").map((p, idx) => {
                    if (p.startsWith("###")) {
                      return <h4 key={idx} className="text-sm font-black text-white mb-2">{p.replace("###", "")}</h4>;
                    }
                    if (p.startsWith("-")) {
                      return (
                        <ul key={idx} className="list-disc pl-4 space-y-1 my-2">
                          {p.split("\n").map((li, lidx) => (
                            <li key={lidx}>{li.replace("-", "").trim()}</li>
                          ))}
                        </ul>
                      );
                    }
                    return <p key={idx} className="mb-2">{p}</p>;
                  })}
                </div>

                {/* Citations list sources */}
                {m.sources && m.sources.length > 0 && (
                  <div className="border-t border-slate-850 pt-3 mt-4 text-[10px] text-slate-500 font-mono">
                    <span className="font-bold text-slate-400 block mb-1">RETRIEVED RAG SOURCES:</span>
                    <ul className="list-decimal pl-4 space-y-1">
                      {m.sources.map((src, idx) => (
                        <li key={idx} className="hover:text-slate-400 transition-colors duration-200">{src}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Glowing PDF ready download button */}
                {m.hasReport && (
                  <button
                    onClick={downloadReportHTML}
                    className="mt-4 px-4 py-2 rounded bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20 border border-emerald-500/20 text-[10px] font-black uppercase tracking-wider font-mono transition-all duration-300 shadow-[0_0_10px_rgba(16,185,129,0.1)] block"
                  >
                    📥 Download PDF-Ready Report
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Input prompt area */}
        <footer className="p-6 border-t border-slate-800 bg-[#0d0f14]/80 backdrop-blur-md">
          {/* Quick prompts suggested tags */}
          <div className="flex gap-2 overflow-x-auto pb-4 scrollbar-none">
            {quickPrompts.map((qp, idx) => (
              <button
                key={idx}
                onClick={() => handleSend(qp)}
                className="px-3.5 py-1.5 rounded-full border border-slate-800 hover:border-emerald-500/50 bg-slate-900/40 text-[10px] text-slate-400 hover:text-slate-200 transition-all duration-300 whitespace-nowrap font-mono"
              >
                💡 {qp}
              </button>
            ))}
          </div>

          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend(inputVal);
            }}
            className="flex gap-4 items-center"
          >
            <input
              type="text"
              value={inputVal}
              onChange={(e) => setInputVal(e.target.value)}
              placeholder="Ask Regulatory Copilot (e.g. Generate RBI report, show violations)..."
              className="flex-1 px-4 py-3 rounded-lg bg-slate-900 border border-slate-800 text-xs text-white focus:outline-none focus:border-emerald-500 font-mono placeholder:text-slate-650"
            />
            <button
              type="submit"
              className="px-6 py-3 rounded bg-emerald-600 hover:bg-emerald-500 text-xs font-black uppercase tracking-wider font-mono text-white transition-all duration-300 shadow-[0_0_15px_rgba(16,185,129,0.2)]"
            >
              Ask Advisor
            </button>
          </form>
        </footer>

      </main>
    </div>
  );
}
