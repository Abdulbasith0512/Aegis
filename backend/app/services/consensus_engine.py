import abc
from typing import Dict, Any, List, Tuple
from app.schemas.consensus import ConsensusRequest, AgentVoteInput

class BaseConsensusEngine(abc.ABC):
    """
    Abstract Base Class for AI Consensus Engines.
    Enforces interface compliance for confidence-weighted voting pipelines.
    """
    @abc.abstractmethod
    def evaluate_consensus(
        self,
        votes: List[AgentVoteInput],
        past_votes: List[Dict[str, Any]]
    ) -> Tuple[str, float, Dict[str, Any]]:
        """
        Processes active votes and historical results.
        Returns: (verdict, consensus_score, vote_details)
        """
        pass

class DynamicConsensusEngine(BaseConsensusEngine):
    """
    Production consensus model evaluating agent outputs, adjusting reputations,
    applying regulatory Compliance overrides, and compiling disagreement metrics.
    """
    def __init__(self) -> None:
        self.base_weights = {
            "compliance-agent": 0.25,
            "fraud-agent": 0.20,
            "aml-agent": 0.15,
            "kyc-agent": 0.15,
            "device-agent": 0.10,
            "behavior-agent": 0.10,
            "explainability-agent": 0.05
        }

    def evaluate_consensus(
        self,
        votes: List[AgentVoteInput],
        past_votes: List[Dict[str, Any]]
    ) -> Tuple[str, float, Dict[str, Any]]:
        
        # 1. Initialize reputations baseline
        reputations = {agent: 1.0 for agent in self.base_weights.keys()}

        # 2. Iterate backwards over past votes history to scale reputations
        # If agent matched resolved verdict -> rep += 0.01; if diverged -> rep -= 0.02
        for pv in reversed(past_votes):
            verdict = pv.get("decision_verdict")
            details = pv.get("vote_details", {})
            agent_history = details.get("agent_votes", {}) # map of name: vote
            
            for agent, vote_str in agent_history.items():
                if agent in reputations:
                    if vote_str == verdict:
                        reputations[agent] = min(1.0, reputations[agent] + 0.01)
                    else:
                        reputations[agent] = max(0.0, reputations[agent] - 0.02)

        # 3. Calculate dynamic normalized weights
        raw_weights = {
            agent: self.base_weights[agent] * reputations[agent]
            for agent in self.base_weights.keys()
        }
        total_weight = sum(raw_weights.values())
        if total_weight == 0:
            normalized_weights = {agent: 1.0 / len(self.base_weights) for agent in self.base_weights.keys()}
        else:
            normalized_weights = {agent: raw_weights[agent] / total_weight for agent in self.base_weights.keys()}

        # 4. Sum confidence-weighted votes
        # Vote value maps: approve = 1.0, decline = 0.0, abstain = 0.5
        vote_sums = 0.0
        confidence_sums = 0.0
        votes_map = {}
        compliance_override = False

        for v in votes:
            agent_name = v.agent_name.lower()
            vote_str = v.vote.lower()
            conf = v.confidence
            
            votes_map[agent_name] = vote_str
            
            # Map standard base weights if agent isn't configured in base_weights
            weight = normalized_weights.get(agent_name, 0.05)
            
            if vote_str == "approve":
                vote_val = 1.0
            elif vote_str == "decline":
                vote_val = 0.0
            else:
                vote_val = 0.5
                
            vote_sums += vote_val * conf * weight
            confidence_sums += conf * weight

            # Compliance veto rule:
            # If compliance agent decline transaction with high confidence (>= 0.80), override
            if agent_name == "compliance-agent" and vote_str == "decline" and conf >= 0.80:
                compliance_override = True

        # Resolved raw verdict from weighted vote sum
        weighted_score = (vote_sums / confidence_sums) if confidence_sums > 0 else 0.50
        resolved_verdict = "approve" if weighted_score >= 0.50 else "decline"

        # Apply override if triggered
        if compliance_override:
            resolved_verdict = "decline"

        # 5. Conduct Disagreement Analysis ( সংখ্যালঘু / Minority voting lists)
        disagreed_agents = []
        for v in votes:
            if v.vote.lower() != resolved_verdict:
                disagreed_agents.append(v.agent_name)

        # 6. Consensus score (percentage agreement among active weights)
        consensus_score = weighted_score if resolved_verdict == "approve" else (1.0 - weighted_score)

        vote_details = {
            "agent_votes": votes_map,
            "reputations": reputations,
            "normalized_weights": normalized_weights,
            "disagreed_agents": disagreed_agents,
            "compliance_override_triggered": compliance_override,
            "weighted_score": weighted_score
        }

        return resolved_verdict, round(consensus_score, 4), vote_details
