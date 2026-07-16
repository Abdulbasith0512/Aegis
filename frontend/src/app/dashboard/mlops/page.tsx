"use client";

import React, { useState, useEffect, useCallback } from "react";
import { 
  Cpu, GitBranch, Shield, Zap, RefreshCw, Plus, ArrowLeftRight, 
  Settings2, Activity, Play, CheckCircle, BarChart3, RotateCcw,
  Sliders, AlertTriangle
} from "lucide-react";

interface ModelVersion {
  id: string;
  version_string: string;
  parameters_hash: string;
  accuracy_benchmark: number;
  deployed_at: string;
  hyperparameters: Record<string, any>;
  metrics: Record<string, any>;
}

interface AgentProfile {
  id: string;
  name: string;
  description: string;
  status: string;
  version_count: number;
  latest_version: string;
  deployment_type: "production" | "canary" | "shadow" | "ab_testing";
  active_version_id: string | null;
  canary_version_id: string | null;
  canary_split: number;
  shadow_version_id: string | null;
  ab_version_a_id: string | null;
  ab_version_b_id: string | null;
  ab_split: number;
}

interface MLflowRun {
  id: string;
  run_name: string;
  parameters: Record<string, any>;
  metrics: Record<string, any>;
  status: string;
  created_at: string;
}

interface TelemetryPoint {
  timestamp: string;
  production_accuracy: number;
  production_latency: number;
  shadow_accuracy: number;
  shadow_latency: number;
  canary_accuracy: number;
  canary_latency: number;
}

interface DeploymentHistory {
  id: string;
  action: string;
  details: string;
  performed_by: string;
  timestamp: string;
}

export default function MLOpsPlatform() {
  const [agents, setAgents] = useState<AgentProfile[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<AgentProfile | null>(null);
  const [versions, setVersions] = useState<ModelVersion[]>([]);
  const [mlflowRuns, setMlflowRuns] = useState<MLflowRun[]>([]);
  const [telemetry, setTelemetry] = useState<TelemetryPoint[]>([]);
  const [history, setHistory] = useState<DeploymentHistory[]>([]);
  const [loading, setLoading] = useState(true);

  // Modals / Inputs
  const [newVersionOpen, setNewVersionOpen] = useState(false);
  const [versionString, setVersionString] = useState("");
  const [paramHash, setParamHash] = useState("");
  const [accBenchmark, setAccBenchmark] = useState(0.95);
  const [lr, setLr] = useState(0.001);
  const [batchSize, setBatchSize] = useState(32);
  const [f1Score, setF1Score] = useState(0.94);

  // Deployment configuration form state
  const [depType, setDepType] = useState<"production" | "canary" | "shadow" | "ab_testing">("production");
  const [activeVerId, setActiveVerId] = useState<string>("");
  const [canaryVerId, setCanaryVerId] = useState<string>("");
  const [canarySplit, setCanarySplit] = useState<number>(10);
  const [shadowVerId, setShadowVerId] = useState<string>("");
  const [abVerAId, setAbVerAId] = useState<string>("");
  const [abVerBId, setAbVerBId] = useState<string>("");
  const [abSplit, setAbSplit] = useState<number>(50);

  // 1. Fetch main profiles
  const loadPlatformData = useCallback(async () => {
    try {
      const res = await fetch("http://localhost:8000/api/v1/agents");
      if (!res.ok) throw new Error("Failed to load agents");
      const data = await res.json();
      setAgents(data);
      if (data.length > 0 && !selectedAgent) {
        setSelectedAgent(data[0]);
      } else if (selectedAgent) {
        // Refresh currently selected agent reference
        const updated = data.find((a: AgentProfile) => a.id === selectedAgent.id);
        if (updated) setSelectedAgent(updated);
      }
    } catch (err) {
      console.error(err);
      // Mock fallback data for sandbox representation
      const mock: AgentProfile[] = [
        {
          id: "agent-1",
          name: "fraud-agent",
          description: "Supervised AegisAI FRAUD evaluation node.",
          status: "active",
          version_count: 2,
          latest_version: "v1.1.0",
          deployment_type: "production",
          active_version_id: "v-1",
          canary_version_id: null,
          canary_split: 100,
          shadow_version_id: null,
          ab_version_a_id: null,
          ab_version_b_id: null,
          ab_split: 50
        },
        {
          id: "agent-2",
          name: "aml-agent",
          description: "Supervised AegisAI AML transaction checker.",
          status: "active",
          version_count: 1,
          latest_version: "v1.0.0",
          deployment_type: "canary",
          active_version_id: "v-2",
          canary_version_id: "v-3",
          canary_split: 15,
          shadow_version_id: null,
          ab_version_a_id: null,
          ab_version_b_id: null,
          ab_split: 50
        }
      ];
      setAgents(mock);
      if (!selectedAgent) setSelectedAgent(mock[0]);
    } finally {
      setLoading(false);
    }
  }, [selectedAgent]);

  // 2. Fetch specific model details
  useEffect(() => {
    loadPlatformData();
  }, []);

  const loadAgentDetails = useCallback(async (agent: AgentProfile) => {
    try {
      // Parallel fetches for versions, runs, telemetry, and log history
      const [vRes, runRes, telRes, histRes] = await Promise.all([
        fetch(`http://localhost:8000/api/v1/agents/${agent.id}/versions`),
        fetch(`http://localhost:8000/api/v1/agents/mlflow/runs?agent_id=${agent.id}`),
        fetch(`http://localhost:8000/api/v1/agents/performance/${agent.id}`),
        fetch(`http://localhost:8000/api/v1/agents/history/${agent.id}`)
      ]);

      if (vRes.ok) setVersions(await vRes.json());
      if (runRes.ok) setMlflowRuns(await runRes.json());
      if (telRes.ok) setTelemetry(await telRes.json());
      if (histRes.ok) setHistory(await histRes.json());

      // Sync form parameters
      setDepType(agent.deployment_type);
      setActiveVerId(agent.active_version_id || "");
      setCanaryVerId(agent.canary_version_id || "");
      setCanarySplit(agent.canary_split);
      setShadowVerId(agent.shadow_version_id || "");
      setAbVerAId(agent.ab_version_a_id || "");
      setAbVerBId(agent.ab_version_b_id || "");
      setAbSplit(agent.ab_split);

    } catch (err) {
      console.error("Error fetching details, loading mock fallbacks", err);
      // Fallback mocks
      const mockVers: ModelVersion[] = [
        {
          id: "v-1",
          version_string: "v1.1.0",
          parameters_hash: "sha256_d1e2f3g4",
          accuracy_benchmark: 0.962,
          deployed_at: new Date().toISOString(),
          hyperparameters: { lr: 0.001, batch_size: 32 },
          metrics: { f1: 0.954, precision: 0.96 }
        },
        {
          id: "v-2",
          version_string: "v1.0.0",
          parameters_hash: "sha256_c7a8b9e0",
          accuracy_benchmark: 0.941,
          deployed_at: new Date(Date.now() - 86400000).toISOString(),
          hyperparameters: { lr: 0.002, batch_size: 64 },
          metrics: { f1: 0.928, precision: 0.932 }
        }
      ];
      setVersions(mockVers);
      setMlflowRuns([
        {
          id: "run-1",
          run_name: "grid_search_adam_v1.1",
          parameters: { lr: 0.001, batch_size: 32 },
          metrics: { accuracy: 0.962, loss: 0.042 },
          status: "FINISHED",
          created_at: new Date().toISOString()
        }
      ]);
      setHistory([
        {
          id: "h-1",
          action: "promote",
          details: "Promoted version v1.1.0 to production active route",
          performed_by: "Administrator",
          timestamp: new Date().toISOString()
        }
      ]);
    }
  }, []);

  useEffect(() => {
    if (selectedAgent) {
      loadAgentDetails(selectedAgent);
    }
  }, [selectedAgent, loadAgentDetails]);

  // Handlers
  const handleDeployConfig = async () => {
    if (!selectedAgent) return;
    try {
      const res = await fetch("http://localhost:8000/api/v1/agents/deployments/configure", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          agent_id: selectedAgent.id,
          deployment_type: depType,
          active_version_id: activeVerId || null,
          canary_version_id: canaryVerId || null,
          canary_split: canarySplit,
          shadow_version_id: shadowVerId || null,
          ab_version_a_id: abVerAId || null,
          ab_version_b_id: abVerBId || null,
          ab_split: abSplit
        })
      });
      if (!res.ok) throw new Error("Failed to configure");
      alert("Deployment configuration updated successfully!");
      loadPlatformData();
    } catch (err) {
      alert("Mock sandbox updated locally.");
    }
  };

  const handleRollback = async (targetVerId: string) => {
    if (!selectedAgent) return;
    try {
      const res = await fetch("http://localhost:8000/api/v1/agents/deployments/rollback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          agent_id: selectedAgent.id,
          target_version_id: targetVerId
        })
      });
      if (!res.ok) throw new Error("Rollback failed");
      alert("Rollback initiated successfully!");
      loadPlatformData();
    } catch (err) {
      alert("Rollback simulated locally.");
    }
  };

  const handleRegisterVersion = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAgent || !versionString.trim() || !paramHash.trim()) return;

    try {
      const res = await fetch(`http://localhost:8000/api/v1/agents/${selectedAgent.id}/versions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          version_string: versionString,
          parameters_hash: paramHash,
          accuracy_benchmark: accBenchmark,
          hyperparameters: { learning_rate: lr, batch_size: batchSize },
          metrics: { f1_score: f1Score }
        })
      });
      if (!res.ok) throw new Error("Failed to register version");
      alert("New version checkpoint successfully registered!");
      setVersionString("");
      setParamHash("");
      setNewVersionOpen(false);
      loadAgentDetails(selectedAgent);
    } catch (err) {
      // Local addition
      setVersions(prev => [
        {
          id: `v-new-${Date.now()}`,
          version_string: versionString,
          parameters_hash: paramHash,
          accuracy_benchmark: accBenchmark,
          deployed_at: new Date().toISOString(),
          hyperparameters: { lr, batch_size: batchSize },
          metrics: { f1: f1Score }
        },
        ...prev
      ]);
      setNewVersionOpen(false);
      alert("Registered locally in Sandbox.");
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      {/* ── Top Header Bar ── */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h1 style={{ fontSize: 24, fontWeight: 800, color: "white", display: "flex", alignItems: "center", gap: 10, fontFamily: "Outfit, sans-serif" }}>
            <Cpu size={24} style={{ color: "#00d4ff" }} /> MLOps Registry & Platform
          </h1>
          <p style={{ fontSize: 13, color: "#71717a", marginTop: 4 }}>
            Control model promotions, canary releases, shadow deployments, A/B experiments, and MLflow run parameters.
          </p>
        </div>
        <button
          onClick={() => setNewVersionOpen(true)}
          style={{
            background: "linear-gradient(135deg, #6366f1, #00d4ff)",
            border: "none",
            color: "white",
            padding: "8px 16px",
            borderRadius: 6,
            fontWeight: 600,
            fontSize: 13,
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            gap: 6
          }}
        >
          <Plus size={15} /> Register Version
        </button>
      </div>

      {loading ? (
        <div style={{ padding: 40, textAlign: "center", color: "#52525e" }}>
          <RefreshCw size={24} className="animate-spin" /> Loading model registry profiles...
        </div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "300px 1fr", gap: 20 }}>
          {/* ── Sidebar: Model Profiles ── */}
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            <div style={{ background: "#0c0c12", border: "1px solid #1c1c24", borderRadius: 8, padding: 16 }}>
              <h3 style={{ fontSize: 12, fontWeight: 700, textTransform: "uppercase", color: "#71717a", letterSpacing: "0.06em", marginBottom: 12 }}>
                Active Registry Profiles
              </h3>
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {agents.map((a) => {
                  const isSelected = selectedAgent?.id === a.id;
                  return (
                    <div
                      key={a.id}
                      onClick={() => setSelectedAgent(a)}
                      style={{
                        padding: 12,
                        borderRadius: 6,
                        background: isSelected ? "#1c1c28" : "#0d0d14",
                        border: "1px solid",
                        borderColor: isSelected ? "#00d4ff" : "#1c1c24",
                        cursor: "pointer",
                        transition: "all 150ms"
                      }}
                    >
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                        <span style={{ fontWeight: 700, fontSize: 13, color: isSelected ? "#00d4ff" : "white" }}>
                          {a.name}
                        </span>
                        <span style={{
                          fontSize: 10,
                          padding: "2px 6px",
                          borderRadius: 10,
                          background: a.status === "active" ? "rgba(16, 185, 129, 0.1)" : "rgba(113, 113, 122, 0.1)",
                          color: a.status === "active" ? "#10b981" : "#71717a"
                        }}>
                          {a.status}
                        </span>
                      </div>
                      <p style={{ fontSize: 11, color: "#71717a", marginTop: 4, lineBreak: "anywhere" }}>
                        {a.description}
                      </p>
                      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, color: "#52525e", marginTop: 8 }}>
                        <span>Versions: {a.version_count}</span>
                        <span>Latest: {a.latest_version}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* ── Main Panel details ── */}
          {selectedAgent && (
            <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
              {/* Row 1: Deployment & Promotion Configurator */}
              <div style={{ background: "#0c0c12", border: "1px solid #1c1c24", borderRadius: 8, padding: 20 }}>
                <h3 style={{ fontSize: 14, fontWeight: 700, color: "white", marginBottom: 16, display: "flex", alignItems: "center", gap: 8 }}>
                  <Sliders size={16} style={{ color: "#00d4ff" }} /> Live Deployment Control Node
                </h3>

                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
                  <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                    <div>
                      <label style={{ fontSize: 11, color: "#71717a", fontWeight: 600 }}>Routing Strategy</label>
                      <select
                        value={depType}
                        onChange={(e) => setDepType(e.target.value as any)}
                        style={{
                          width: "100%",
                          background: "#0d0d14",
                          border: "1px solid #1c1c24",
                          color: "white",
                          padding: 8,
                          borderRadius: 6,
                          fontSize: 12,
                          marginTop: 4
                        }}
                      >
                        <option value="production">Production-Only (100% standard route)</option>
                        <option value="canary">Canary Release (Splits to experimental branch)</option>
                        <option value="shadow">Shadow Deployment (Silent runs in background)</option>
                        <option value="ab_testing">A/B Traffic Testing</option>
                      </select>
                    </div>

                    {depType === "production" && (
                      <div>
                        <label style={{ fontSize: 11, color: "#71717a", fontWeight: 600 }}>Active Production Version</label>
                        <select
                          value={activeVerId}
                          onChange={(e) => setActiveVerId(e.target.value)}
                          style={{
                            width: "100%",
                            background: "#0d0d14",
                            border: "1px solid #1c1c24",
                            color: "white",
                            padding: 8,
                            borderRadius: 6,
                            fontSize: 12,
                            marginTop: 4
                          }}
                        >
                          <option value="">-- Choose active version --</option>
                          {versions.map((v) => (
                            <option key={v.id} value={v.id}>{v.version_string} (Benchmark: {v.accuracy_benchmark * 100}%)</option>
                          ))}
                        </select>
                      </div>
                    )}

                    {depType === "canary" && (
                      <>
                        <div>
                          <label style={{ fontSize: 11, color: "#71717a", fontWeight: 600 }}>Base Production Version</label>
                          <select
                            value={activeVerId}
                            onChange={(e) => setActiveVerId(e.target.value)}
                            style={{
                              width: "100%",
                              background: "#0d0d14",
                              border: "1px solid #1c1c24",
                              color: "white",
                              padding: 8,
                              borderRadius: 6,
                              fontSize: 12,
                              marginTop: 4
                            }}
                          >
                            <option value="">-- Choose production base --</option>
                            {versions.map((v) => (
                              <option key={v.id} value={v.id}>{v.version_string}</option>
                            ))}
                          </select>
                        </div>
                        <div>
                          <label style={{ fontSize: 11, color: "#71717a", fontWeight: 600 }}>Target Canary Version</label>
                          <select
                            value={canaryVerId}
                            onChange={(e) => setCanaryVerId(e.target.value)}
                            style={{
                              width: "100%",
                              background: "#0d0d14",
                              border: "1px solid #1c1c24",
                              color: "white",
                              padding: 8,
                              borderRadius: 6,
                              fontSize: 12,
                              marginTop: 4
                            }}
                          >
                            <option value="">-- Choose canary version --</option>
                            {versions.map((v) => (
                              <option key={v.id} value={v.id}>{v.version_string}</option>
                            ))}
                          </select>
                        </div>
                        <div>
                          <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, color: "#71717a" }}>
                            <span>Canary Traffic split</span>
                            <span style={{ color: "#00d4ff", fontWeight: 700 }}>{canarySplit}% Canary</span>
                          </div>
                          <input
                            type="range"
                            min="1"
                            max="99"
                            value={canarySplit}
                            onChange={(e) => setCanarySplit(parseInt(e.target.value))}
                            style={{ width: "100%", accentColor: "#00d4ff", marginTop: 4 }}
                          />
                        </div>
                      </>
                    )}

                    {depType === "shadow" && (
                      <>
                        <div>
                          <label style={{ fontSize: 11, color: "#71717a", fontWeight: 600 }}>Base Production Version</label>
                          <select
                            value={activeVerId}
                            onChange={(e) => setActiveVerId(e.target.value)}
                            style={{
                              width: "100%",
                              background: "#0d0d14",
                              border: "1px solid #1c1c24",
                              color: "white",
                              padding: 8,
                              borderRadius: 6,
                              fontSize: 12,
                              marginTop: 4
                            }}
                          >
                            <option value="">-- Choose production base --</option>
                            {versions.map((v) => (
                              <option key={v.id} value={v.id}>{v.version_string}</option>
                            ))}
                          </select>
                        </div>
                        <div>
                          <label style={{ fontSize: 11, color: "#71717a", fontWeight: 600 }}>Active Shadow Version (Silent Logs)</label>
                          <select
                            value={shadowVerId}
                            onChange={(e) => setShadowVerId(e.target.value)}
                            style={{
                              width: "100%",
                              background: "#0d0d14",
                              border: "1px solid #1c1c24",
                              color: "white",
                              padding: 8,
                              borderRadius: 6,
                              fontSize: 12,
                              marginTop: 4
                            }}
                          >
                            <option value="">-- Choose shadow version --</option>
                            {versions.map((v) => (
                              <option key={v.id} value={v.id}>{v.version_string}</option>
                            ))}
                          </select>
                        </div>
                      </>
                    )}

                    {depType === "ab_testing" && (
                      <>
                        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
                          <div>
                            <label style={{ fontSize: 11, color: "#71717a", fontWeight: 600 }}>Version A</label>
                            <select
                              value={abVerAId}
                              onChange={(e) => setAbVerAId(e.target.value)}
                              style={{
                                width: "100%",
                                background: "#0d0d14",
                                border: "1px solid #1c1c24",
                                color: "white",
                                padding: 8,
                                borderRadius: 6,
                                fontSize: 12,
                                marginTop: 4
                              }}
                            >
                              <option value="">-- Choose A --</option>
                              {versions.map((v) => (
                                <option key={v.id} value={v.id}>{v.version_string}</option>
                              ))}
                            </select>
                          </div>
                          <div>
                            <label style={{ fontSize: 11, color: "#71717a", fontWeight: 600 }}>Version B</label>
                            <select
                              value={abVerBId}
                              onChange={(e) => setAbVerBId(e.target.value)}
                              style={{
                                width: "100%",
                                background: "#0d0d14",
                                border: "1px solid #1c1c24",
                                color: "white",
                                padding: 8,
                                borderRadius: 6,
                                fontSize: 12,
                                marginTop: 4
                              }}
                            >
                              <option value="">-- Choose B --</option>
                              {versions.map((v) => (
                                <option key={v.id} value={v.id}>{v.version_string}</option>
                              ))}
                            </select>
                          </div>
                        </div>
                        <div>
                          <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, color: "#71717a" }}>
                            <span>A/B Split Ratio</span>
                            <span style={{ color: "#6366f1", fontWeight: 700 }}>{abSplit}% A / {100-abSplit}% B</span>
                          </div>
                          <input
                            type="range"
                            min="1"
                            max="99"
                            value={abSplit}
                            onChange={(e) => setAbSplit(parseInt(e.target.value))}
                            style={{ width: "100%", accentColor: "#6366f1", marginTop: 4 }}
                          />
                        </div>
                      </>
                    )}
                  </div>

                  <div style={{ display: "flex", flexDirection: "column", justifyContent: "space-between", borderLeft: "1px solid #1c1c24", paddingLeft: 20 }}>
                    <div style={{ fontSize: 12, color: "#a1a1aa", lineHeight: "1.6" }}>
                      <div style={{ fontWeight: 700, color: "white", marginBottom: 6 }}>Deployment Strategy Helper</div>
                      {depType === "production" && "Standard deployment route directs 100% of API transaction loads straight to the active version."}
                      {depType === "canary" && "Canary route lets you bleed a small subset of incoming traffic to your new experimental version to watch for memory drops or accuracy drifts."}
                      {depType === "shadow" && "Shadow route runs predictions on BOTH models in parallel. It serves the production output to customers but stores the shadow output silently in background logs for offline evaluation."}
                      {depType === "ab_testing" && "Directs a randomized percentage split of customer traffic to Model A and Model B respectively to compare live performance outcomes."}
                    </div>

                    <button
                      onClick={handleDeployConfig}
                      style={{
                        background: "#27272a",
                        border: "1px solid #3f3f46",
                        color: "white",
                        padding: "8px 14px",
                        borderRadius: 6,
                        fontWeight: 600,
                        fontSize: 12,
                        cursor: "pointer",
                        marginTop: 12,
                        alignSelf: "flex-end",
                        transition: "background 150ms"
                      }}
                      onMouseEnter={(e) => e.currentTarget.style.background = "#3f3f46"}
                      onMouseLeave={(e) => e.currentTarget.style.background = "#27272a"}
                    >
                      Update Traffic Configuration
                    </button>
                  </div>
                </div>
              </div>

              {/* Row 2: Performance Telemetry comparison and History */}
              <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: 20 }}>
                {/* Registry Registry Table */}
                <div style={{ background: "#0c0c12", border: "1px solid #1c1c24", borderRadius: 8, padding: 20 }}>
                  <h3 style={{ fontSize: 14, fontWeight: 700, color: "white", marginBottom: 12, display: "flex", alignItems: "center", gap: 8 }}>
                    <GitBranch size={16} style={{ color: "#00d4ff" }} /> Model Registry Versions
                  </h3>

                  <div style={{ overflowX: "auto" }}>
                    <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
                      <thead>
                        <tr style={{ borderBottom: "1px solid #1c1c24", color: "#71717a", textAlign: "left" }}>
                          <th style={{ padding: "8px 4px" }}>Version String</th>
                          <th style={{ padding: "8px 4px" }}>Benchmark Acc</th>
                          <th style={{ padding: "8px 4px" }}>F1 Score</th>
                          <th style={{ padding: "8px 4px" }}>Checksum</th>
                          <th style={{ padding: "8px 4px", textAlign: "right" }}>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {versions.map((v) => (
                          <tr key={v.id} style={{ borderBottom: "1px solid #0d0d14", color: "#e2e8f0" }}>
                            <td style={{ padding: "10px 4px", fontWeight: 700, color: "white" }}>
                              {v.version_string}
                            </td>
                            <td style={{ padding: "10px 4px" }}>{(v.accuracy_benchmark * 100).toFixed(1)}%</td>
                            <td style={{ padding: "10px 4px" }}>
                              {v.metrics?.f1_score || v.metrics?.f1 || "0.941"}
                            </td>
                            <td style={{ padding: "10px 4px", fontFamily: "monospace", color: "#71717a" }}>
                              {v.parameters_hash.slice(0, 10)}...
                            </td>
                            <td style={{ padding: "10px 4px", textAlign: "right" }}>
                              <button
                                onClick={() => handleRollback(v.id)}
                                style={{
                                  background: "none",
                                  border: "none",
                                  color: "#00d4ff",
                                  cursor: "pointer",
                                  fontSize: 11,
                                  fontWeight: 600,
                                  display: "inline-flex",
                                  alignItems: "center",
                                  gap: 4
                                }}
                              >
                                <RotateCcw size={11} /> Rollback Here
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Audit promotion history */}
                <div style={{ background: "#0c0c12", border: "1px solid #1c1c24", borderRadius: 8, padding: 20 }}>
                  <h3 style={{ fontSize: 14, fontWeight: 700, color: "white", marginBottom: 12, display: "flex", alignItems: "center", gap: 8 }}>
                    <Activity size={16} style={{ color: "#6366f1" }} /> Promotion Log History
                  </h3>
                  <div style={{ display: "flex", flexDirection: "column", gap: 10, maxHeight: 180, overflowY: "auto", paddingRight: 4 }}>
                    {history.map((h) => (
                      <div key={h.id} style={{ fontSize: 11, borderLeft: "2px solid #3f3f46", paddingLeft: 10, paddingBottom: 6 }}>
                        <div style={{ display: "flex", justifyContent: "space-between", color: "#71717a" }}>
                          <span style={{ fontWeight: 700, textTransform: "uppercase", color: h.action === "rollback" ? "#f43f5e" : "#00d4ff" }}>
                            {h.action}
                          </span>
                          <span>{new Date(h.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                        </div>
                        <p style={{ color: "#e2e8f0", marginTop: 2 }}>{h.details}</p>
                        <span style={{ color: "#52525e", fontSize: 10 }}>Actor: {h.performed_by}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Row 3: MLflow Run logs */}
              <div style={{ background: "#0c0c12", border: "1px solid #1c1c24", borderRadius: 8, padding: 20 }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                  <h3 style={{ fontSize: 14, fontWeight: 700, color: "white", display: "flex", alignItems: "center", gap: 8 }}>
                    <BarChart3 size={16} style={{ color: "#00d4ff" }} /> MLflow Experiments Tracking Runs
                  </h3>
                  <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                    <span style={{ width: 8, height: 8, borderRadius: "50%", background: "#10b981" }}></span>
                    <span style={{ fontSize: 11, color: "#71717a" }}>MLflow Integration active</span>
                  </div>
                </div>

                <div style={{ overflowX: "auto" }}>
                  <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
                    <thead>
                      <tr style={{ borderBottom: "1px solid #1c1c24", color: "#71717a", textAlign: "left" }}>
                        <th style={{ padding: "8px 4px" }}>Run ID</th>
                        <th style={{ padding: "8px 4px" }}>Run Name</th>
                        <th style={{ padding: "8px 4px" }}>Hyperparameters</th>
                        <th style={{ padding: "8px 4px" }}>Metrics Logs</th>
                        <th style={{ padding: "8px 4px" }}>Execution status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {mlflowRuns.map((r) => (
                        <tr key={r.id} style={{ borderBottom: "1px solid #0d0d14", color: "#e2e8f0" }}>
                          <td style={{ padding: "10px 4px", fontFamily: "monospace", color: "#71717a" }}>
                            {r.id.slice(0, 8)}...
                          </td>
                          <td style={{ padding: "10px 4px", fontWeight: 700 }}>
                            {r.run_name}
                          </td>
                          <td style={{ padding: "10px 4px", color: "#a1a1aa" }}>
                            {Object.entries(r.parameters || {}).map(([k, v]) => `${k}=${v}`).join(", ") || "lr=0.001"}
                          </td>
                          <td style={{ padding: "10px 4px", color: "#10b981", fontWeight: 600 }}>
                            {Object.entries(r.metrics || {}).map(([k, v]) => `${k}:${v}`).join(", ") || "acc:0.962"}
                          </td>
                          <td style={{ padding: "10px 4px" }}>
                            <span style={{
                              fontSize: 10,
                              background: "rgba(16, 185, 129, 0.1)",
                              color: "#10b981",
                              padding: "2px 8px",
                              borderRadius: 4
                            }}>
                              {r.status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Row 4: Performance Telemetry comparison charts */}
              <div style={{ background: "#0c0c12", border: "1px solid #1c1c24", borderRadius: 8, padding: 20 }}>
                <h3 style={{ fontSize: 14, fontWeight: 700, color: "white", marginBottom: 16 }}>
                  Accuracies & Latencies Comparisons Timeseries
                </h3>

                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
                  <div style={{ padding: 12, background: "#0d0d14", borderRadius: 6, border: "1px solid #1c1c24" }}>
                    <span style={{ fontSize: 12, color: "#a1a1aa", fontWeight: 600 }}>Model accuracy Attributions</span>
                    <div style={{ display: "flex", flexDirection: "column", gap: 10, marginTop: 12 }}>
                      {telemetry.slice(-4).map((pt, idx) => (
                        <div key={idx} style={{ fontSize: 12, display: "flex", justifyContent: "space-between", borderBottom: "1px solid #1c1c24", paddingBottom: 4 }}>
                          <span style={{ color: "#71717a" }}>{new Date(pt.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                          <span style={{ color: "#10b981" }}>Prod: {pt.production_accuracy * 100}%</span>
                          <span style={{ color: "#6366f1" }}>Shadow: {pt.shadow_accuracy * 100}%</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div style={{ padding: 12, background: "#0d0d14", borderRadius: 6, border: "1px solid #1c1c24" }}>
                    <span style={{ fontSize: 12, color: "#a1a1aa", fontWeight: 600 }}>Model latency telemetries (ms)</span>
                    <div style={{ display: "flex", flexDirection: "column", gap: 10, marginTop: 12 }}>
                      {telemetry.slice(-4).map((pt, idx) => (
                        <div key={idx} style={{ fontSize: 12, display: "flex", justifyContent: "space-between", borderBottom: "1px solid #1c1c24", paddingBottom: 4 }}>
                          <span style={{ color: "#71717a" }}>{new Date(pt.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                          <span style={{ color: "#f59e0b" }}>Prod: {pt.production_latency}ms</span>
                          <span style={{ color: "#00d4ff" }}>Shadow: {pt.shadow_latency}ms</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ── Modal: Register New Version Checkpoint ── */}
      {newVersionOpen && selectedAgent && (
        <div style={{ position: "fixed", top: 0, left: 0, right: 0, bottom: 0, background: "rgba(0, 0, 0, 0.8)", display: "flex", justifyContent: "center", alignItems: "center", zIndex: 1000 }}>
          <div style={{ background: "#0c0c12", border: "1px solid #1c1c24", padding: 24, borderRadius: 8, width: 450 }}>
            <h3 style={{ fontSize: 16, fontWeight: 800, color: "white", marginBottom: 16 }}>Register Version for {selectedAgent.name}</h3>
            
            <form onSubmit={handleRegisterVersion} style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              <div>
                <label style={{ fontSize: 11, color: "#71717a", fontWeight: 600 }}>Version String</label>
                <input
                  type="text"
                  required
                  placeholder="E.g., v1.2.0"
                  value={versionString}
                  onChange={(e) => setVersionString(e.target.value)}
                  style={{ width: "100%", background: "#0d0d14", border: "1px solid #1c1c24", color: "white", padding: 8, borderRadius: 6, fontSize: 12, marginTop: 4 }}
                />
              </div>

              <div>
                <label style={{ fontSize: 11, color: "#71717a", fontWeight: 600 }}>Parameters Checksum Hash</label>
                <input
                  type="text"
                  required
                  placeholder="sha256_checksum..."
                  value={paramHash}
                  onChange={(e) => setParamHash(e.target.value)}
                  style={{ width: "100%", background: "#0d0d14", border: "1px solid #1c1c24", color: "white", padding: 8, borderRadius: 6, fontSize: 12, marginTop: 4 }}
                />
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
                <div>
                  <label style={{ fontSize: 11, color: "#71717a", fontWeight: 600 }}>Baseline Accuracy</label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    max="1"
                    value={accBenchmark}
                    onChange={(e) => setAccBenchmark(parseFloat(e.target.value))}
                    style={{ width: "100%", background: "#0d0d14", border: "1px solid #1c1c24", color: "white", padding: 8, borderRadius: 6, fontSize: 12, marginTop: 4 }}
                  />
                </div>
                <div>
                  <label style={{ fontSize: 11, color: "#71717a", fontWeight: 600 }}>F1-Score Baseline</label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    max="1"
                    value={f1Score}
                    onChange={(e) => setF1Score(parseFloat(e.target.value))}
                    style={{ width: "100%", background: "#0d0d14", border: "1px solid #1c1c24", color: "white", padding: 8, borderRadius: 6, fontSize: 12, marginTop: 4 }}
                  />
                </div>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
                <div>
                  <label style={{ fontSize: 11, color: "#71717a", fontWeight: 600 }}>Learning Rate</label>
                  <input
                    type="number"
                    step="0.0001"
                    value={lr}
                    onChange={(e) => setLr(parseFloat(e.target.value))}
                    style={{ width: "100%", background: "#0d0d14", border: "1px solid #1c1c24", color: "white", padding: 8, borderRadius: 6, fontSize: 12, marginTop: 4 }}
                  />
                </div>
                <div>
                  <label style={{ fontSize: 11, color: "#71717a", fontWeight: 600 }}>Batch Size</label>
                  <input
                    type="number"
                    value={batchSize}
                    onChange={(e) => setBatchSize(parseInt(e.target.value))}
                    style={{ width: "100%", background: "#0d0d14", border: "1px solid #1c1c24", color: "white", padding: 8, borderRadius: 6, fontSize: 12, marginTop: 4 }}
                  />
                </div>
              </div>

              <div style={{ display: "flex", justifyContent: "flex-end", gap: 10, marginTop: 12 }}>
                <button
                  type="button"
                  onClick={() => setNewVersionOpen(false)}
                  style={{ background: "#27272a", border: "none", color: "white", padding: "8px 14px", borderRadius: 6, fontSize: 12, cursor: "pointer" }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  style={{ background: "linear-gradient(135deg, #6366f1, #00d4ff)", border: "none", color: "white", padding: "8px 14px", borderRadius: 6, fontSize: 12, cursor: "pointer", fontWeight: 600 }}
                >
                  Register
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
