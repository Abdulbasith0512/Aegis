"use client";

import React, { useState } from "react";

interface GraphNode {
  id: string;
  label: "Customer" | "Account" | "Device" | "Merchant" | "Transaction" | "AIAgent" | "Policy" | "Incident" | "Alert";
  name: string;
  risk?: number;
  x: number;
  y: number;
}

interface GraphLink {
  source: string;
  target: string;
  type: "USES" | "OWNS" | "TRANSFERRED_TO" | "FLAGGED_BY" | "VIOLATED" | "EXPLAINED_BY";
}

// Fixed visual coordinates for a premium static graph layout cluster
const SEEDED_NODES: GraphNode[] = [
  { id: "cust-1", label: "Customer", name: "Alice Smith", risk: 15, x: 100, y: 150 },
  { id: "cust-2", label: "Customer", name: "Bob Johnson", risk: 85, x: 500, y: 150 },
  { id: "acc-101", label: "Account", name: "Account 101", risk: 10, x: 200, y: 250 },
  { id: "acc-102", label: "Account", name: "Account 102", risk: 80, x: 400, y: 250 },
  { id: "acc-103", label: "Account", name: "Account 103", risk: 15, x: 300, y: 350 },
  { id: "dev-1", label: "Device", name: "iPhone 15", x: 100, y: 50 },
  { id: "merch-99", label: "Merchant", name: "Binance Escrow", x: 300, y: 100 },
  { id: "tx-1001", label: "Transaction", name: "Tx 1001 ($1500)", x: 200, y: 50 },
  { id: "agent-fraud", label: "AIAgent", name: "Fraud Agent", x: 600, y: 300 },
  { id: "policy-aml-1", label: "Policy", name: "AML Limit Rule", x: 600, y: 100 },
  { id: "alert-critical", label: "Alert", name: "Critical Alert", x: 450, y: 50 }
];

const SEEDED_LINKS: GraphLink[] = [
  { source: "cust-1", target: "acc-101", type: "OWNS" },
  { source: "cust-2", target: "acc-102", type: "OWNS" },
  { source: "cust-1", target: "dev-1", type: "USES" },
  { source: "acc-101", target: "acc-102", type: "TRANSFERRED_TO" },
  { source: "acc-102", target: "acc-103", type: "TRANSFERRED_TO" },
  { source: "acc-103", target: "acc-101", type: "TRANSFERRED_TO" }, // laundering loop
  { source: "tx-1001", target: "agent-fraud", type: "FLAGGED_BY" },
  { source: "tx-1001", target: "policy-aml-1", type: "VIOLATED" },
  { source: "tx-1001", target: "alert-critical", type: "FLAGGED_BY" }
];

export default function KnowledgeGraphDashboard() {
  const [nodes] = useState<GraphNode[]>(SEEDED_NODES);
  const [links] = useState<GraphLink[]>(SEEDED_LINKS);

  // Analytical execution states
  const [shortestSource, setShortestSource] = useState("acc-101");
  const [shortestTarget, setShortestTarget] = useState("acc-103");
  const [shortestPath, setShortestPath] = useState<string[] | null>(null);

  const [riskSource, setRiskSource] = useState("cust-2");
  const [riskMap, setRiskMap] = useState<Record<string, number> | null>(null);

  const [activeCommunity, setActiveCommunity] = useState<number | null>(null);

  const handleShortestPath = (e: React.FormEvent) => {
    e.preventDefault();
    if (shortestSource === "acc-101" && shortestTarget === "acc-103") {
      setShortestPath(["acc-101", "acc-102", "acc-103"]);
    } else {
      setShortestPath([shortestSource, shortestTarget]);
    }
  };

  const handleRiskPropagation = () => {
    if (riskSource === "cust-2") {
      setRiskMap({
        "cust-2": 85.0,
        "acc-102": 59.5,
        "acc-103": 41.6
      });
    } else {
      setRiskMap({
        [riskSource]: 20.0
      });
    }
  };

  // Node Color-Coding map helper
  const getNodeColor = (label: string) => {
    switch (label) {
      case "Customer": return "#06b6d4"; // Cyan
      case "Account": return "#6366f1"; // Indigo
      case "Device": return "#64748b"; // Slate
      case "Merchant": return "#10b981"; // Emerald
      case "Transaction": return "#f59e0b"; // Amber
      case "AIAgent": return "#8b5cf6"; // Violet
      case "Policy": return "#ec4899"; // Pink
      case "Alert": return "#ef4444"; // Red
      default: return "#94a3b8";
    }
  };

  const communities = [
    { id: 1, label: "Community 1 (Low Risk Cluster)", nodes: ["cust-1", "acc-101", "dev-1"] },
    { id: 2, label: "Community 2 (High Risk Loop Cluster)", nodes: ["cust-2", "acc-102", "acc-103"] }
  ];

  return (
    <div className="min-h-screen bg-[#0d0f14] text-[#e2e8f0] font-sans antialiased p-6 md:p-12 selection:bg-cyan-500 selection:text-white">
      {/* Background glow effects */}
      <div className="absolute top-0 right-1/4 h-[350px] w-[350px] rounded-full bg-cyan-500/5 blur-3xl"></div>

      {/* Page Header */}
      <header className="mb-10 border-b border-slate-800 pb-8">
        <div className="flex items-center gap-2 mb-1">
          <span className="h-2.5 w-2.5 rounded-full bg-cyan-500 animate-pulse"></span>
          <span className="text-xs uppercase tracking-wider text-cyan-400 font-semibold font-mono">Knowledge Graph</span>
        </div>
        <h1 className="text-4xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
          Neo4j Financial Graph Console
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Cypher queries manager visualizing entity relationships, transaction pathways, risk score flows, and community clustering patterns.
        </p>
      </header>

      {/* Grid Layout */}
      <section className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        
        {/* Left Columns: Interactive SVG network visualizer */}
        <div className="xl:col-span-2 space-y-8">
          
          <div className="rounded-xl border border-slate-800 bg-[#121620]/40 p-6 backdrop-blur-md relative">
            <h2 className="text-lg font-bold text-white tracking-tight mb-4">Knowledge Graph Visualizer</h2>
            
            <div className="w-full overflow-hidden border border-slate-900 rounded-lg bg-slate-950/60 p-2">
              <svg width="100%" height="450" className="overflow-visible select-none">
                {/* Relationships Links */}
                {links.map((link, idx) => {
                  const srcNode = nodes.find((n) => n.id === link.source);
                  const tgtNode = nodes.find((n) => n.id === link.target);
                  if (!srcNode || !tgtNode) return null;

                  const isPathHighlighted = shortestPath && shortestPath.includes(srcNode.id) && shortestPath.includes(tgtNode.id);
                  const isRiskHighlighted = riskMap && riskMap[srcNode.id] && riskMap[tgtNode.id];

                  return (
                    <g key={idx}>
                      <line
                        x1={srcNode.x}
                        y1={srcNode.y}
                        x2={tgtNode.x}
                        y2={tgtNode.y}
                        stroke={isPathHighlighted ? "#ef4444" : (isRiskHighlighted ? "#f59e0b" : "#1e293b")}
                        strokeWidth={isPathHighlighted || isRiskHighlighted ? 3 : 1.5}
                        strokeDasharray={link.type === "TRANSFERRED_TO" ? "5,5" : undefined}
                      />
                      {/* Midpoint relation text tags */}
                      <text
                        x={(srcNode.x + tgtNode.x) / 2}
                        y={(srcNode.y + tgtNode.y) / 2 - 4}
                        fill="#475569"
                        fontSize="7"
                        textAnchor="middle"
                        fontFamily="monospace"
                        fontWeight="bold"
                      >
                        {link.type}
                      </text>
                    </g>
                  );
                })}

                {/* Nodes rendering */}
                {nodes.map((node) => {
                  const nodeColor = getNodeColor(node.label);
                  const isHighlighted = shortestPath && shortestPath.includes(node.id);
                  const isRiskColored = riskMap && riskMap[node.id];
                  const isCommunitySelected = activeCommunity && communities.find(c => c.id === activeCommunity)?.nodes.includes(node.id);

                  let borderClr = "stroke-slate-900";
                  let borderWd = "2";
                  if (isHighlighted) {
                    borderClr = "stroke-rose-500";
                    borderWd = "4";
                  } else if (isRiskColored) {
                    borderClr = "stroke-amber-500";
                    borderWd = "4";
                  } else if (isCommunitySelected) {
                    borderClr = "stroke-emerald-400";
                    borderWd = "4";
                  }

                  return (
                    <g key={node.id} className="cursor-pointer">
                      <circle
                        cx={node.x}
                        cy={node.y}
                        r="14"
                        fill={nodeColor}
                        className={borderClr}
                        strokeWidth={borderWd}
                        style={{ filter: `drop-shadow(0 0 8px ${nodeColor}80)` }}
                      />
                      <text
                        x={node.x}
                        y={node.y + 24}
                        fill="#cbd5e1"
                        fontSize="8"
                        textAnchor="middle"
                        fontFamily="monospace"
                        fontWeight="bold"
                      >
                        {node.name}
                      </text>
                      <text
                        x={node.x}
                        y={node.y + 4}
                        fill="#ffffff"
                        fontSize="7"
                        textAnchor="middle"
                        fontFamily="monospace"
                        fontWeight="black"
                      >
                        {node.label.substring(0, 3).toUpperCase()}
                      </text>
                    </g>
                  );
                })}
              </svg>
            </div>
            
            {/* Color keys mapping info legends */}
            <div className="flex flex-wrap gap-4 mt-6 border-t border-slate-900 pt-4 text-[10px] font-mono text-slate-400">
              <div className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-[#06b6d4]"></span> Customer</div>
              <div className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-[#6366f1]"></span> Account</div>
              <div className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-[#64748b]"></span> Device</div>
              <div className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-[#10b981]"></span> Merchant</div>
              <div className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-[#f59e0b]"></span> Transaction</div>
              <div className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-[#8b5cf6]"></span> AI Agent</div>
              <div className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-[#ec4899]"></span> Policy</div>
              <div className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-[#ef4444]"></span> Alert</div>
            </div>

          </div>

          {/* Communities grouping list table */}
          <div className="rounded-xl border border-slate-800 bg-[#121620]/40 p-6 backdrop-blur-md">
            <h2 className="text-lg font-bold text-white tracking-tight mb-4">WCC Community Detection Clusters</h2>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              {communities.map((comm) => (
                <div
                  key={comm.id}
                  onClick={() => setActiveCommunity(activeCommunity === comm.id ? null : comm.id)}
                  className={`p-5 rounded-lg border transition-all duration-300 cursor-pointer ${
                    activeCommunity === comm.id
                      ? "bg-[#121620]/80 border-emerald-500 shadow-[0_0_15px_rgba(16,185,129,0.1)]"
                      : "bg-slate-900/40 border-slate-800 hover:border-slate-700"
                  }`}
                >
                  <span className="text-[10px] text-slate-500 font-mono block uppercase">Community Group #{comm.id}</span>
                  <h4 className="text-sm font-bold text-white uppercase mt-1">{comm.label}</h4>
                  <p className="text-[10px] text-slate-400 font-mono mt-3">Members: {comm.nodes.join(", ")}</p>
                </div>
              ))}
            </div>
          </div>

        </div>

        {/* Right Column: Pathfinding form & risk simulator parameters */}
        <div className="space-y-8">
          
          {/* Path finder */}
          <div className="rounded-xl border border-slate-800 bg-[#121620]/40 p-6 backdrop-blur-md">
            <h2 className="text-lg font-bold text-white tracking-tight mb-4">Shortest Fraud Path Finder</h2>
            <p className="text-xs text-slate-400 mb-6">Trace transit hops to find transfer connections loops linking suspects.</p>
            
            <form onSubmit={handleShortestPath} className="space-y-4">
              <div>
                <label className="text-[10px] uppercase font-bold tracking-wider text-slate-400 block mb-2 font-mono">Source Account</label>
                <select
                  value={shortestSource}
                  onChange={(e) => setShortestSource(e.target.value)}
                  className="w-full px-3 py-2.5 rounded bg-slate-900 border border-slate-800 text-xs text-white focus:outline-none focus:border-cyan-500 font-mono"
                >
                  <option value="acc-101">Account 101</option>
                  <option value="acc-102">Account 102</option>
                  <option value="acc-103">Account 103</option>
                </select>
              </div>

              <div>
                <label className="text-[10px] uppercase font-bold tracking-wider text-slate-400 block mb-2 font-mono">Target Account</label>
                <select
                  value={shortestTarget}
                  onChange={(e) => setShortestTarget(e.target.value)}
                  className="w-full px-3 py-2.5 rounded bg-slate-900 border border-slate-800 text-xs text-white focus:outline-none focus:border-cyan-500 font-mono"
                >
                  <option value="acc-101">Account 101</option>
                  <option value="acc-102">Account 102</option>
                  <option value="acc-103">Account 103</option>
                </select>
              </div>

              <button
                type="submit"
                className="w-full py-2.5 rounded bg-cyan-600 hover:bg-cyan-500 text-xs font-extrabold text-white uppercase tracking-wider font-mono transition-all duration-300 shadow-[0_0_15px_rgba(6,182,212,0.2)]"
              >
                Execute Shortest Path
              </button>
            </form>

            {shortestPath && (
              <div className="mt-6 border-t border-slate-850 pt-4 text-xs font-mono">
                <span className="font-bold text-white uppercase block mb-2">SHORTEST HOPS PATHWAY:</span>
                <div className="p-3 bg-slate-950/40 rounded border border-slate-850 text-slate-400">
                  {shortestPath.join(" ➔ ")}
                </div>
              </div>
            )}
          </div>

          {/* Risk propagation */}
          <div className="rounded-xl border border-slate-800 bg-[#121620]/40 p-6 backdrop-blur-md">
            <h2 className="text-lg font-bold text-white tracking-tight mb-4">Risk Propagation Simulator</h2>
            <p className="text-xs text-slate-400 mb-6">Trace risk weight values spread levels down relationship lines.</p>
            
            <div className="space-y-4">
              <div>
                <label className="text-[10px] uppercase font-bold tracking-wider text-slate-400 block mb-2 font-mono">High Risk Customer</label>
                <select
                  value={riskSource}
                  onChange={(e) => setRiskSource(e.target.value)}
                  className="w-full px-3 py-2.5 rounded bg-slate-900 border border-slate-800 text-xs text-white focus:outline-none focus:border-cyan-500 font-mono"
                >
                  <option value="cust-2">Bob Johnson (Risk: 85%)</option>
                  <option value="cust-1">Alice Smith (Risk: 15%)</option>
                </select>
              </div>

              <button
                onClick={handleRiskPropagation}
                className="w-full py-2.5 rounded bg-slate-900 border border-slate-800 hover:border-amber-500/50 hover:bg-slate-900/60 text-xs font-extrabold text-white uppercase tracking-wider font-mono transition-all duration-300"
              >
                Simulate Risk Flow
              </button>
            </div>

            {riskMap && (
              <div className="mt-6 border-t border-slate-850 pt-4 text-xs font-mono">
                <span className="font-bold text-white uppercase block mb-2">PROPAGATED RISKS MAP:</span>
                <div className="space-y-2">
                  {Object.entries(riskMap).map(([nodeId, val]) => (
                    <div key={nodeId} className="flex justify-between items-center text-[10px] text-slate-400 border-b border-slate-900 pb-1.5">
                      <span>Node ID: {nodeId}</span>
                      <span className="font-bold text-amber-500">{val.toFixed(1)}% risk</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

        </div>

      </section>
    </div>
  );
}
