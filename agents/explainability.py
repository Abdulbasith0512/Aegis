from typing import Any, Dict, List
from agents.base import BaseGovernanceAgent

class ExplainabilityAgent(BaseGovernanceAgent):
    """
    Formulates structured explanations detailing attributes contributing to agent risk scores.
    """
    def __init__(self) -> None:
        super().__init__(name="ExplainabilityAgent")

    async def _execute(self, state: Dict[str, Any], logs: List[str]) -> Dict[str, Any]:
        fraud_result = state.get("fraud_result")
        aml_result = state.get("aml_result")
        
        logs.append("Synthesizing decision explainability profiles...")
        
        reasons = []
        if fraud_result and getattr(fraud_result, "confidence_score", 1.0) < 0.60:
            reasons.append(f"Fraud model flags: {getattr(fraud_result, 'reasoning')}")
        if aml_result and getattr(aml_result, "confidence_score", 1.0) < 0.60:
            reasons.append(f"AML model flags: {getattr(aml_result, 'reasoning')}")
            
        if reasons:
            explanation_text = "Transaction flagged under caution: " + "; ".join(reasons)
        else:
            explanation_text = "Transaction clean: fits standard behavioral and profiling limits."

        return {
            "confidence_score": 1.00,
            "reasoning": f"Explanation: {explanation_text}"
        }
