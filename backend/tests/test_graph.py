import pytest
from app.database.neo4j_db import Neo4jDatabaseManager
from app.services.knowledge_graph import KnowledgeGraphService

def test_neo4j_manager_initialization() -> None:
    """
    Verifies that the Neo4j manager correctly initializes and checks driver flags.
    """
    manager = Neo4jDatabaseManager()
    assert manager is not None
    # Verify that it instantiates sessions safely
    session = manager.get_session()
    assert session is not None
    session.close()

def test_knowledge_graph_service_mock_visuals() -> None:
    """
    Verifies visualization structures output under mock/real scenarios.
    """
    service = KnowledgeGraphService()
    res = service.get_graph_visualization()
    
    assert "nodes" in res
    assert "links" in res
    assert len(res["nodes"]) > 0

def test_knowledge_graph_shortest_path() -> None:
    """
    Verifies that pathfinding returns valid hop sequences.
    """
    service = KnowledgeGraphService()
    res = service.find_shortest_fraud_path("acc-101", "acc-103")
    
    assert res["path_found"] is True
    assert "acc-102" in res["hops"]

def test_knowledge_graph_risk_propagation() -> None:
    """
    Verifies that risk scores propagate.
    """
    service = KnowledgeGraphService()
    res = service.propagate_risk_scores("cust-2")
    
    assert res["start_node"] == "cust-2"
    assert "acc-102" in res["propagated_risk_map"]
    assert res["propagated_risk_map"]["acc-102"] == 59.5
