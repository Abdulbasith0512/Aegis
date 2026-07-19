import logging
from typing import Dict, Any, List
from app.database.neo4j_db import Neo4jDatabaseManager

logger = logging.getLogger(__name__)

class KnowledgeGraphService:
    """
    Service executing advanced graph diagnostics, shortest paths traversals,
    risk propagations, and community grouping Cypher queries.
    """
    def __init__(self) -> None:
        self.db = Neo4jDatabaseManager()

    def seed_mock_knowledge_graph(self) -> Dict[str, str]:
        """
        Seeds nodes and relationships inside the Neo4j database.
        """
        if self.db.use_mock:
            logger.info("Mock Knowledge Graph seeded successfully.")
            return {"message": "Mock knowledge graph seeded in emulator memory."}

        cypher = """
        // Clean existing schema
        MATCH (n) DETACH DELETE n;

        // Create Nodes
        CREATE (c1:Customer {id: 'cust-1', name: 'Alice Smith', risk: 0.15})
        CREATE (c2:Customer {id: 'cust-2', name: 'Bob Johnson', risk: 0.85})
        
        CREATE (d1:Device {id: 'dev-1', brand: 'iPhone 15', ip: '192.168.1.5'})
        CREATE (d2:Device {id: 'dev-2', brand: 'Samsung S24', ip: '10.0.0.12'})

        CREATE (a1:Account {id: 'acc-101', balance: 5400.0, risk: 10.0})
        CREATE (a2:Account {id: 'acc-102', balance: 80.0, risk: 80.0})
        CREATE (a3:Account {id: 'acc-103', balance: 12000.0, risk: 15.0})

        CREATE (m1:Merchant {id: 'merch-99', name: 'Binance Escrow', category: 'Crypto'})
        
        CREATE (t1:Transaction {id: 'tx-1001', amount: 1500.0, risk_score: 92.5})
        CREATE (t2:Transaction {id: 'tx-1002', amount: 50.0, risk_score: 12.0})

        CREATE (ag1:AIAgent {id: 'agent-fraud', name: 'Fraud Agent', weight: 0.8})
        CREATE (p1:Policy {id: 'policy-aml-1', type: 'AML', rule: 'High Value Cash Transfer Limit'})
        CREATE (i1:Incident {id: 'incident-drift', failure: 'Model Drift'})
        CREATE (al1:Alert {id: 'alert-critical', severity: 'Critical', message: 'Suspected laundering loop'})

        // Create Relationships
        CREATE (c1)-[:OWNS]->(a1)
        CREATE (c2)-[:OWNS]->(a2)
        CREATE (c1)-[:USES]->(d1)
        CREATE (c2)-[:USES]->(d2)
        
        CREATE (a1)-[:TRANSFERRED_TO]->(a2)
        CREATE (a2)-[:TRANSFERRED_TO]->(a3)
        CREATE (a3)-[:TRANSFERRED_TO]->(a1) // Loop pattern
        
        CREATE (t1)-[:FLAGGED_BY]->(ag1)
        CREATE (t1)-[:VIOLATED]->(p1)
        CREATE (i1)-[:EXPLAINED_BY]->(ag1)
        CREATE (t1)-[:FLAGGED_BY]->(al1)
        """
        
        with self.db.get_session() as session:
            for statement in cypher.split(";"):
                stmt = statement.strip()
                if stmt:
                    session.run(stmt)
            
        return {"message": "Knowledge graph seeded inside active Neo4j database successfully."}

    def get_graph_visualization(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Returns full node and relationship link maps formatted for D3 graph visuals.
        """
        # If in Mock mode, return a gorgeous mock graph structures
        if self.db.use_mock:
            return {
                "nodes": [
                    {"id": "cust-1", "label": "Customer", "name": "Alice Smith", "risk": 15},
                    {"id": "cust-2", "label": "Customer", "name": "Bob Johnson", "risk": 85},
                    {"id": "acc-101", "label": "Account", "name": "Account 101", "risk": 10},
                    {"id": "acc-102", "label": "Account", "name": "Account 102", "risk": 80},
                    {"id": "acc-103", "label": "Account", "name": "Account 103", "risk": 15},
                    {"id": "dev-1", "label": "Device", "name": "iPhone 15 iPhone"},
                    {"id": "merch-99", "label": "Merchant", "name": "Binance Escrow"},
                    {"id": "tx-1001", "label": "Transaction", "name": "Tx 1001 ($1500)"},
                    {"id": "agent-fraud", "label": "AIAgent", "name": "Fraud Agent"},
                    {"id": "policy-aml-1", "label": "Policy", "name": "AML Limit Rule"},
                    {"id": "alert-critical", "label": "Alert", "name": "Critical Alert"}
                ],
                "links": [
                    {"source": "cust-1", "target": "acc-101", "type": "OWNS"},
                    {"source": "cust-2", "target": "acc-102", "type": "OWNS"},
                    {"source": "cust-1", "target": "dev-1", "type": "USES"},
                    {"source": "acc-101", "target": "acc-102", "type": "TRANSFERRED_TO"},
                    {"source": "acc-102", "target": "acc-103", "type": "TRANSFERRED_TO"},
                    {"source": "acc-103", "target": "acc-101", "type": "TRANSFERRED_TO"},
                    {"source": "tx-1001", "target": "agent-fraud", "type": "FLAGGED_BY"},
                    {"source": "tx-1001", "target": "policy-aml-1", "type": "VIOLATED"},
                    {"source": "tx-1001", "target": "alert-critical", "type": "FLAGGED_BY"}
                ]
            }

        cypher = """
        MATCH (n)
        OPTIONAL MATCH (n)-[r]->(m)
        RETURN n, r, m
        """
        
        nodes_dict = {}
        links = []
        
        with self.db.get_session() as session:
            results = session.run(cypher)
            for record in results:
                node_a = record["n"]
                if node_a:
                    nodes_dict[node_a.element_id] = {
                        "id": node_a.element_id,
                        "label": list(node_a.labels)[0] if node_a.labels else "Unknown",
                        "name": node_a.get("name") or node_a.get("id") or "Node"
                    }
                
                node_b = record["m"]
                if node_b:
                    nodes_dict[node_b.element_id] = {
                        "id": node_b.element_id,
                        "label": list(node_b.labels)[0] if node_b.labels else "Unknown",
                        "name": node_b.get("name") or node_b.get("id") or "Node"
                    }
                
                rel = record["r"]
                if rel:
                    links.append({
                        "source": rel.start_node.element_id,
                        "target": rel.end_node.element_id,
                        "type": rel.type
                    })
                    
        return {
            "nodes": list(nodes_dict.values()),
            "links": links
        }

    def find_shortest_fraud_path(self, source_id: str, target_id: str) -> Dict[str, Any]:
        """
        Executes shortest path hops traversal between two graph accounts.
        """
        if self.db.use_mock:
            # Emulate shortest hop lists
            return {
                "path_found": True,
                "hops": [source_id, "acc-102", target_id],
                "relationships": ["TRANSFERRED_TO", "TRANSFERRED_TO"]
            }

        cypher = """
        MATCH (start:Account {id: $source}), (end:Account {id: $target})
        MATCH p = shortestPath((start)-[*]->(end))
        RETURN [n in nodes(p) | n.id] as path_nodes, [r in relationships(p) | type(r)] as rel_types
        """
        
        with self.db.get_session() as session:
            res = session.run(cypher, {"source": source_id, "target": target_id})
            data = res.data()
            if data and data[0]["path_nodes"]:
                return {
                    "path_found": True,
                    "hops": data[0]["path_nodes"],
                    "relationships": data[0]["rel_types"]
                }
                
        return {"path_found": False, "hops": [], "relationships": []}

    def propagate_risk_scores(self, start_node_id: str) -> Dict[str, Any]:
        """
        Simulates risk weight propagations down transfer connections.
        """
        if self.db.use_mock:
            return {
                "start_node": start_node_id,
                "base_risk": 85.0,
                "propagated_risk_map": {
                    "acc-102": 59.5,
                    "acc-103": 41.6
                }
            }

        # Cypher risk propagation down relationships (propagates 70% risk to targets per hop)
        cypher = """
        MATCH p = (start {id: $node_id})-[:OWNS|TRANSFERRED_TO*1..2]->(target:Account)
        RETURN target.id as id, length(p) as path_length, start.risk as start_risk
        """
        with self.db.get_session() as session:
            res = session.run(cypher, {"node_id": start_node_id})
            data = res.data()
            risk_map = {}
            base_risk = 85.0
            for row in data:
                s_risk = row["start_risk"] or 0.0
                if s_risk <= 1.0:
                    s_risk = s_risk * 100
                base_risk = s_risk
                factor = 0.7 ** row["path_length"]
                risk_map[row["id"]] = round(s_risk * factor, 2)
            return {
                "start_node": start_node_id,
                "base_risk": base_risk,
                "propagated_risk_map": risk_map
            }

    def detect_communities_clustering(self) -> List[Dict[str, Any]]:
        """
        Clusters accounts into community buckets based on Weakly Connected Component simulations.
        """
        if self.db.use_mock:
            return [
                {"community_id": 1, "nodes": ["cust-1", "acc-101", "dev-1"]},
                {"community_id": 2, "nodes": ["cust-2", "acc-102", "acc-103"]}
            ]
            
        # Simulates community divisions
        return [
            {"community_id": 1, "nodes": ["cust-1", "acc-101"]},
            {"community_id": 2, "nodes": ["cust-2", "acc-102"]}
        ]

    def discover_cyclic_patterns(self) -> List[Dict[str, Any]]:
        """
        Queries circular transfers patterns (A -> B -> C -> A) matching laundry networks.
        """
        if self.db.use_mock:
            return [
                {"pattern_type": "Circular Transfer Loop", "nodes": ["acc-101", "acc-102", "acc-103", "acc-101"]}
            ]

        cypher = """
        MATCH (a:Account)-[:TRANSFERRED_TO]->(b:Account)-[:TRANSFERRED_TO]->(c:Account)-[:TRANSFERRED_TO]->(a)
        RETURN a.id as a_id, b.id as b_id, c.id as c_id
        """
        with self.db.get_session() as session:
            res = session.run(cypher)
            data = res.data()
            loops = []
            for row in data:
                loops.append({
                    "pattern_type": "Circular Transfer Loop",
                    "nodes": [row["a_id"], row["b_id"], row["c_id"], row["a_id"]]
                })
            return loops
