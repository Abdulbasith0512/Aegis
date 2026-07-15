import uuid
from datetime import datetime
from typing import Dict, Any, List
from pydantic import BaseModel, Field, field_validator

class AgentVoteInput(BaseModel):
    """
    Input schema defining a single agent's evaluation decision vote.
    """
    agent_name: str = Field(..., description="Evaluating agent name identifier.")
    vote: str = Field(..., description="Verdict recommendation: 'approve', 'decline', or 'abstain'.")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Decision confidence probability.")

    @field_validator("vote")
    @classmethod
    def check_valid_verdict(cls, v: str) -> str:
        if v.lower() not in ["approve", "decline", "abstain"]:
            raise ValueError("Agent vote verdict must be 'approve', 'decline', or 'abstain'")
        return v.lower()

class ConsensusRequest(BaseModel):
    """
    Payload containing agent votes context.
    """
    transaction_id: uuid.UUID = Field(..., description="Target transaction UUID.")
    votes: List[AgentVoteInput] = Field(..., description="List of votes from evaluating agents.")

class ConsensusResponse(BaseModel):
    """
    Aggregated consensus engine response.
    """
    id: uuid.UUID
    transaction_id: uuid.UUID
    decision_verdict: str = Field(..., description="Final resolved transaction decision verdict.")
    consensus_score: float = Field(..., description="Weighted agreement consensus percentage.")
    vote_details: Dict[str, Any] = Field(..., description="Detailed dynamic weights, reputations, and conflict logs.")
    created_at: datetime
