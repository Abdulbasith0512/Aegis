import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class CopilotQueryRequest(BaseModel):
    """Payload to query the AI Regulatory Copilot."""
    query: str = Field(..., min_length=2, description="The text prompt/query containing the question or command.")

class CopilotMessageResponse(BaseModel):
    """Speech turn response schema representing user prompts or assistant answers."""
    id: uuid.UUID
    session_id: uuid.UUID
    role: str = Field(..., description="Role value: 'user' or 'assistant'.")
    content: str = Field(..., description="The answer response in markdown syntax.")
    sources: Optional[Dict[str, Any]] = Field(default=None, description="Extracted citation documents lists.")
    report_html: Optional[str] = Field(default=None, description="HTML report content template (if generated).")
    created_at: datetime

class CopilotSessionCreate(BaseModel):
    """Payload to instantiate a chat thread session."""
    title: str = Field(..., min_length=1, max_length=200, description="Session subject title.")

class CopilotSessionResponse(BaseModel):
    """Session context overview schema."""
    id: uuid.UUID
    title: str
    created_at: datetime
    messages: List[CopilotMessageResponse] = []
