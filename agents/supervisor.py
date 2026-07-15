import logging
from typing import Any, Dict, List
from agents.base import BaseGovernanceAgent, AgentResponse

logger = logging.getLogger("aegisai.agents.SupervisorAgent")

class SupervisorAgent(BaseGovernanceAgent):
    """
    Coordinates agent outputs, calculates trust index scores, and resolves transaction verdicts.
    """
    def __init__(self) -> None:
        super().__init__(name="SupervisorAgent")

    async def _execute(self, state: Dict[str, Any], logs: List[str]) -> Dict[str, Any]:
        logs.append("Evaluating multi-agent outcomes to determine transaction governance verdict.")
        
        # 1. Fetch outputs from preceding nodes
        device_result: AgentResponse = state.get("device_result")
        kyc_result: AgentResponse = state.get("kyc_result")
        fraud_result: AgentResponse = state.get("fraud_result")
        aml_result: AgentResponse = state.get("aml_result")
        policy_result: AgentResponse = state.get("policy_result")
        explain_result: AgentResponse = state.get("explainability_result")

        # Fallback scores if any agent failed or is missing
        dev_conf = device_result.confidence_score if device_result and device_result.status == "success" else 1.0
        kyc_conf = kyc_result.confidence_score if kyc_result and kyc_result.status == "success" else 1.0
        fraud_conf = fraud_result.confidence_score if fraud_result and fraud_result.status == "success" else 1.0
        policy_conf = policy_result.confidence_score if policy_result and policy_result.status == "success" else 1.0
        aml_conf = aml_result.confidence_score if aml_result and aml_result.status == "success" else 1.0

        # 2. Trust Score Formula: Weighted combination of security and compliance indicators (0 to 100)
        # Weights: 35% Fraud, 25% Device, 20% Policy Compliance, 20% KYC Verification Alignment
        trust_score = int(
            (0.35 * fraud_conf + 0.25 * dev_conf + 0.20 * policy_conf + 0.20 * kyc_conf) * 100
        )
        logs.append(f"Dynamic Trust Score calculated: {trust_score}/100")

        # 3. Determine final transaction verdict
        # Rule exceptions: Hard compliance policy block or severe fraud score
        if policy_conf == 0.0 or aml_conf < 0.30 or trust_score < 50:
            verdict = "declined"
            reasoning = "Transaction declined: failed strict security and compliance policy limits."
        elif trust_score < 75:
            verdict = "under_review"
            reasoning = "Transaction pending: low trust score requires Human-in-the-Loop review."
        else:
            verdict = "approved"
            reasoning = "Transaction approved: complies with all risk parameters."

        logs.append(f"Final verdict resolved: {verdict}")

        explanation = explain_result.reasoning if explain_result else "No explanation generated."

        return {
            "confidence_score": float(trust_score / 100),
            "reasoning": (
                f"verdict: {verdict} | trust_score: {trust_score} | "
                f"reasoning: {reasoning} | {explanation}"
            )
        }
