import uuid
import pytest
from app.schemas.consensus import AgentVoteInput
from app.services.consensus_engine import DynamicConsensusEngine

def test_consensus_engine_unanimity_approve() -> None:
    """
    Verifies that unanimous approval yields approve verdict and high consensus score.
    """
    votes = [
        AgentVoteInput(agent_name="fraud-agent", vote="approve", confidence=0.90),
        AgentVoteInput(agent_name="aml-agent", vote="approve", confidence=0.85),
        AgentVoteInput(agent_name="compliance-agent", vote="approve", confidence=0.95)
    ]
    
    engine = DynamicConsensusEngine()
    verdict, score, details = engine.evaluate_consensus(votes, past_votes=[])
    
    assert verdict == "approve"
    assert score == 1.00 # Perfect approval consensus
    assert len(details["disagreed_agents"]) == 0
    assert details["compliance_override_triggered"] is False

def test_consensus_engine_compliance_veto() -> None:
    """
    Verifies that a high confidence decline by ComplianceAgent vetoes weighted approvals.
    """
    votes = [
        AgentVoteInput(agent_name="fraud-agent", vote="approve", confidence=0.95),
        AgentVoteInput(agent_name="aml-agent", vote="approve", confidence=0.90),
        AgentVoteInput(agent_name="compliance-agent", vote="decline", confidence=0.85) # High confidence veto
    ]
    
    engine = DynamicConsensusEngine()
    verdict, score, details = engine.evaluate_consensus(votes, past_votes=[])
    
    assert verdict == "decline"
    assert details["compliance_override_triggered"] is True

def test_consensus_engine_reputation_scaling() -> None:
    """
    Verifies that past evaluations scale agent reputations and weights dynamically.
    """
    votes = [
        AgentVoteInput(agent_name="fraud-agent", vote="approve", confidence=0.95),
        AgentVoteInput(agent_name="aml-agent", vote="decline", confidence=0.90),
        AgentVoteInput(agent_name="compliance-agent", vote="approve", confidence=0.90)
    ]
    
    # AML agent diverged from the final approved verdict in the past 3 sessions
    past_history = [
        {
            "decision_verdict": "approve",
            "vote_details": {
                "agent_votes": {
                    "fraud-agent": "approve",
                    "aml-agent": "decline",
                    "compliance-agent": "approve"
                }
            }
        }
    ] * 3
    
    engine = DynamicConsensusEngine()
    verdict, score, details = engine.evaluate_consensus(votes, past_history)
    
    # AML reputation should drop: 1.0 - 0.02 * 3 = 0.94
    assert details["reputations"]["aml-agent"] == 0.94
    
    # AML weight should drop correspondingly below base weight (0.15)
    assert details["normalized_weights"]["aml-agent"] < 0.15
