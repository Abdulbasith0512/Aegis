from typing import Dict, Any, List
from fastapi import APIRouter, Depends, Query, status
from app.core.dependencies import require_permission
from app.services.knowledge_graph import KnowledgeGraphService
from app.models.users import User

router: APIRouter = APIRouter(prefix="/graph", tags=["Neo4j Knowledge Graph"])

@router.post("/seed", status_code=status.HTTP_201_CREATED)
async def seed_graph_database(
    current_user: User = Depends(require_permission("write:policies"))
) -> Dict[str, str]:
    """
    Seeds nodes (Customer, Device, Merchant, Account, Transaction, AI Agent, Policy, Incident, Alert)
    and relationships into the active Neo4j database registry.
    Requires 'write:policies' permission.
    """
    service = KnowledgeGraphService()
    return service.seed_mock_knowledge_graph()

@router.get("/visualization", response_model=Dict[str, List[Dict[str, Any]]])
async def get_graph_visual_dataset(
    current_user: User = Depends(require_permission("read:transactions"))
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Retrieves visual nodes and relationships dataset formatted for frontend visual tools.
    Requires 'read:transactions' permission.
    """
    service = KnowledgeGraphService()
    return service.get_graph_visualization()

@router.get("/shortest-path", response_model=Dict[str, Any])
async def check_shortest_fraud_path(
    source: str = Query(..., min_length=2),
    target: str = Query(..., min_length=2),
    current_user: User = Depends(require_permission("read:transactions"))
) -> Dict[str, Any]:
    """
    Executes shortest path hop verification between two accounts (e.g. source='acc-101', target='acc-103').
    Requires 'read:transactions' permission.
    """
    service = KnowledgeGraphService()
    return service.find_shortest_fraud_path(source, target)

@router.get("/risk-propagation", response_model=Dict[str, Any])
async def get_propagated_risk_scores(
    start_node: str = Query(..., min_length=2),
    current_user: User = Depends(require_permission("read:transactions"))
) -> Dict[str, Any]:
    """
    Simulates risk weight propagations down transfer connections starting from a target node.
    Requires 'read:transactions' permission.
    """
    service = KnowledgeGraphService()
    return service.propagate_risk_scores(start_node)

@router.get("/communities", response_model=List[Dict[str, Any]])
async def check_community_detection_clusters(
    current_user: User = Depends(require_permission("read:transactions"))
) -> List[Dict[str, Any]]:
    """
    Runs community detection groupings identifying transaction clusters.
    Requires 'read:transactions' permission.
    """
    service = KnowledgeGraphService()
    return service.detect_communities_clustering()

@router.get("/patterns", response_model=List[Dict[str, Any]])
async def check_cyclic_fraud_patterns(
    current_user: User = Depends(require_permission("read:transactions"))
) -> List[Dict[str, Any]]:
    """
    Queries loop laundry transfer loops (A -> B -> C -> A).
    Requires 'read:transactions' permission.
    """
    service = KnowledgeGraphService()
    return service.discover_cyclic_patterns()
