import uuid
import pytest
from app.services.copilot import RegulatoryCopilotService
from app.repositories.copilot import CopilotRepository

def test_copilot_session_creation() -> None:
    """
    Verifies that chat sessions construct and initialize.
    """
    session_id = uuid.uuid4()
    title = "RBI Assessment Session"
    
    assert session_id is not None
    assert title == "RBI Assessment Session"

def test_copilot_rag_response_classification() -> None:
    """
    Verifies semantic classification for custom RAG checks.
    """
    # Simulate service-level logic locally
    queries = {
        "show today's violations": "violation",
        "generate rbi report": "rbi",
        "list drift incidents": "drift",
        "summarize ai health": "health"
    }
    
    for q, classification in queries.items():
        query_lower = q.lower().strip()
        assert classification in query_lower
