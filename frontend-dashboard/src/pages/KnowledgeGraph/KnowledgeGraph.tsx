import React, { useState, useMemo, useCallback, useRef, useEffect } from 'react';
import ReactFlow, {
  Background, Controls, MiniMap,
  useNodesState, useEdgesState,
  Node, Edge, MarkerType,
  BackgroundVariant,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Search, Maximize2, GitBranch, Layers } from 'lucide-react';
import { Drawer, RiskBadge } from '@/components/ui';

// ── Mock entity data ────────────────────────────────────────────────────────
const ENTITY_COLORS: Record<string, string> = {
  Customer:    '#06b6d4',
  Account:     '#6366f1',
  Device:      '#64748b',
  Merchant:    '#10b981',
  Transaction: '#f59e0b',
};

function makeNode(id: string, label: string, type: string, x: number, y: number, data?: Record<string, unknown>): Node {
  return {
    id,
    position: { x, y },
    data: { label, entityType: type, ...data },
    type: 'default',
    style: {
      background: `${ENTITY_COLORS[type] || '#52525e'}22`,
      border: `1.5px solid ${ENTITY_COLORS[type] || '#52525e'}88`,
      borderRadius: 8,
      color: ENTITY_COLORS[type] || '#c4c4cc',
      fontSize: 11,
      fontFamily: 'var(--font-mono)',
      fontWeight: 600,
      padding: '6px 12px',
      minWidth: 120,
      textAlign: 'center',
    },
  };
}

function makeEdge(id: string, source: string, target: string, label: string, strength: number = 1): Edge {
  return {
    id,
    source,
    target,
    label,
    animated: label === 'TRANSFERRED_TO',
    markerEnd: { type: MarkerType.ArrowClosed, color: '#35353f' },
    style: { stroke: '#35353f', strokeWidth: strength * 1.2 },
    labelStyle: { fill: '#52525e', fontSize: 9, fontFamily: 'var(--font-mono)' },
    labelBgStyle: { fill: '#09090b', fillOpacity: 0.8 },
  };
}

const INITIAL_NODES: Node[] = [
  makeNode('cust-1', '👤 Alice Smith', 'Customer', 50, 180, { risk: 15, riskLevel: 'low' }),
  makeNode('cust-2', '👤 Bob Johnson', 'Customer', 50, 320, { risk: 85, riskLevel: 'critical' }),
  makeNode('cust-3', '👤 Carol White', 'Customer', 50, 460, { risk: 42, riskLevel: 'medium' }),
  makeNode('acc-101', '💳 Account 101', 'Account', 280, 120, { balance: 5400, risk: 10, riskLevel: 'safe' }),
  makeNode('acc-102', '💳 Account 102', 'Account', 280, 280, { balance: 80, risk: 80, riskLevel: 'high' }),
  makeNode('acc-103', '💳 Account 103', 'Account', 280, 420, { balance: 12000, risk: 15, riskLevel: 'low' }),
  makeNode('dev-1', '📱 iPhone 15', 'Device', 120, 60, {}),
  makeNode('dev-2', '📱 Samsung S24', 'Device', 500, 60, {}),
  makeNode('merch-1', '🏪 Binance Escrow', 'Merchant', 500, 220, { category: 'Crypto' }),
  makeNode('merch-2', '🏪 Amazon', 'Merchant', 500, 380, { category: 'E-Commerce' }),
  makeNode('tx-1001', '₿ Tx #1001 ($1500)', 'Transaction', 720, 180, { amount: 1500, risk: 92, riskLevel: 'critical' }),
  makeNode('tx-1002', '₿ Tx #1002 ($50)', 'Transaction', 720, 340, { amount: 50, risk: 12, riskLevel: 'safe' }),
];

const INITIAL_EDGES: Edge[] = [
  makeEdge('e1', 'cust-1', 'acc-101', 'OWNS', 2),
  makeEdge('e2', 'cust-2', 'acc-102', 'OWNS', 2),
  makeEdge('e3', 'cust-3', 'acc-103', 'OWNS', 2),
  makeEdge('e4', 'cust-1', 'dev-1', 'USES', 1),
  makeEdge('e5', 'cust-2', 'dev-2', 'USES', 1),
  makeEdge('e6', 'acc-101', 'acc-102', 'TRANSFERRED_TO', 3),
  makeEdge('e7', 'acc-102', 'acc-103', 'TRANSFERRED_TO', 3),
  makeEdge('e8', 'acc-103', 'acc-101', 'TRANSFERRED_TO', 3),   // fraud loop
  makeEdge('e9', 'acc-102', 'merch-1', 'TRANSFERRED_TO', 2),
  makeEdge('e10', 'acc-103', 'merch-2', 'TRANSFERRED_TO', 1),
  makeEdge('e11', 'tx-1001', 'acc-102', 'FLAGGED_BY', 1.5),
  makeEdge('e12', 'tx-1002', 'acc-103', 'FLAGGED_BY', 1),
  makeEdge('e13', 'cust-2', 'tx-1001', 'EXPLAINED_BY', 1),
];

// ── Knowledge Graph Page ───────────────────────────────────────────────────
export default function KnowledgeGraph() {
  const [nodes, setNodes, onNodesChange] = useNodesState(INITIAL_NODES);
  const [edges, setEdges, onEdgesChange] = useEdgesState(INITIAL_EDGES);
  const [search, setSearch] = useState('');
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [layout, setLayout] = useState<'force' | 'hierarchical'>('force');

  // Search highlight
  useEffect(() => {
    if (!search) {
      setNodes(nds => nds.map(n => ({
        ...n,
        style: { ...n.style, opacity: 1 },
      })));
      return;
    }
    const q = search.toLowerCase();
    setNodes(nds => nds.map(n => {
      const matches = (n.data.label as string).toLowerCase().includes(q);
      return {
        ...n,
        style: {
          ...n.style,
          opacity: matches ? 1 : 0.2,
          boxShadow: matches ? '0 0 0 2px var(--accent)' : 'none',
        },
      };
    }));
  }, [search, setNodes]);

  // Hierarchical layout toggle
  const applyHierarchicalLayout = useCallback(() => {
    setNodes(nds => nds.map((n, i) => ({
      ...n,
      position: {
        x: (i % 4) * 250 + 50,
        y: Math.floor(i / 4) * 150 + 50,
      },
    })));
  }, [setNodes]);

  const handleLayoutToggle = () => {
    const next = layout === 'force' ? 'hierarchical' : 'force';
    setLayout(next);
    if (next === 'hierarchical') applyHierarchicalLayout();
    else {
      // Restore original positions
      setNodes(INITIAL_NODES);
    }
  };

  const entityTypes = Object.keys(ENTITY_COLORS);

  return (
    <div style={{ maxWidth: 1600 }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', marginBottom: 16 }}>
        <div>
          <h1 style={{ fontSize: 'var(--text-20)', fontWeight: 700, color: 'var(--gray-50)', lineHeight: 1 }}>Knowledge Graph</h1>
          <p style={{ fontSize: 'var(--text-13)', color: 'var(--gray-500)', marginTop: 4 }}>
            Entity relationship graph — {INITIAL_NODES.length} nodes · {INITIAL_EDGES.length} edges
          </p>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button className="btn btn-outline" onClick={handleLayoutToggle}>
            {layout === 'force' ? <Layers size={13} /> : <GitBranch size={13} />}
            {layout === 'force' ? 'Hierarchical' : 'Force'} layout
          </button>
        </div>
      </div>

      {/* Search + Legend bar */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12, flexWrap: 'wrap' }}>
        <div style={{ position: 'relative', width: 240 }}>
          <Search size={13} style={{ position: 'absolute', left: 9, top: '50%', transform: 'translateY(-50%)', color: 'var(--gray-500)', pointerEvents: 'none' }} />
          <input
            className="input"
            style={{ paddingLeft: 30 }}
            placeholder="Search entities…"
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          {entityTypes.map(type => (
            <div key={type} style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 'var(--text-12)', color: 'var(--gray-400)' }}>
              <span style={{ width: 8, height: 8, borderRadius: 2, background: ENTITY_COLORS[type] }} />
              {type}
            </div>
          ))}
        </div>
      </div>

      {/* Graph canvas */}
      <div
        className="card"
        style={{ padding: 0, overflow: 'hidden', height: 580, position: 'relative' }}
      >
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onNodeClick={(_, node) => setSelectedNode(node)}
          fitView
          style={{ background: 'var(--surface-0)' }}
          minZoom={0.3}
          maxZoom={2}
        >
          <Background
            variant={BackgroundVariant.Dots}
            gap={20}
            size={1}
            color="var(--gray-800)"
          />
          <Controls
            style={{
              background: 'var(--surface-2)',
              border: '1px solid var(--border-2)',
              borderRadius: 'var(--radius-md)',
            }}
          />
          <MiniMap
            style={{
              background: 'var(--surface-1)',
              border: '1px solid var(--border-2)',
              borderRadius: 'var(--radius-md)',
            }}
            nodeColor={node => ENTITY_COLORS[node.data?.entityType as string] || '#52525e'}
            maskColor="rgba(0,0,0,0.6)"
          />
        </ReactFlow>
      </div>

      {/* Node detail drawer */}
      <Drawer
        open={!!selectedNode}
        onClose={() => setSelectedNode(null)}
        title={selectedNode?.data?.label as string}
        subtitle={selectedNode?.data?.entityType as string}
        width={400}
      >
        {selectedNode && <NodeDetail node={selectedNode} edges={INITIAL_EDGES} nodes={INITIAL_NODES} />}
      </Drawer>
    </div>
  );
}

// ── Node Detail Content ────────────────────────────────────────────────────
function NodeDetail({ node, edges, nodes }: { node: Node; edges: Edge[]; nodes: Node[] }) {
  const relatedEdges = edges.filter(e => e.source === node.id || e.target === node.id);
  const data = node.data as Record<string, unknown>;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
      {Boolean(data.riskLevel) && (
        <div>
          <RiskBadge level={data.riskLevel as never} score={data.risk as number} />
        </div>
      )}

      {/* Properties */}
      <div>
        <div className="text-label" style={{ marginBottom: 8 }}>Properties</div>
        {Object.entries(data).filter(([k]) => k !== 'label' && k !== 'entityType' && k !== 'riskLevel').map(([k, v]) => (
          <div key={k} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '5px 0', borderBottom: '1px solid var(--border-0)', fontSize: 'var(--text-13)' }}>
            <span style={{ color: 'var(--gray-500)', textTransform: 'capitalize' }}>{k}</span>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--gray-200)' }}>{String(v)}</span>
          </div>
        ))}
      </div>

      {/* Relationships */}
      <div>
        <div className="text-label" style={{ marginBottom: 8 }}>Relationships ({relatedEdges.length})</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
          {relatedEdges.map(e => {
            const isSource = e.source === node.id;
            const otherId = isSource ? e.target : e.source;
            const other = nodes.find(n => n.id === otherId);
            return (
              <div key={e.id} style={{
                display: 'flex', alignItems: 'center', gap: 8,
                padding: '6px 8px', borderRadius: 'var(--radius-sm)',
                background: 'var(--surface-3)', fontSize: 'var(--text-12)',
              }}>
                <span style={{ fontSize: 10, fontFamily: 'var(--font-mono)', color: 'var(--accent)', fontWeight: 600 }}>
                  {isSource ? '→' : '←'}
                </span>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--gray-500)', background: 'var(--surface-4)', padding: '1px 5px', borderRadius: 3 }}>{e.label as string}</span>
                <span style={{ color: 'var(--gray-300)' }}>{String(other?.data?.label ?? otherId)}</span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
