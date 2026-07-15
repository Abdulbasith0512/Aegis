from typing import Any, Dict, List
from agents.base import BaseGovernanceAgent

class KYCAgent(BaseGovernanceAgent):
    """
    Evaluates customer KYC registration profiles and bureau verification matches.
    """
    def __init__(self) -> None:
        super().__init__(name="KYCAgent")

    async def _execute(self, state: Dict[str, Any], logs: List[str]) -> Dict[str, Any]:
        tx_data = state.get("transaction", {})
        account = tx_data.get("account", {})
        customer = account.get("customer", {})
        
        logs.append(f"Checking KYC records for customer: {customer.get('email')}")
        
        status = customer.get("status", "unknown")
        risk_level = customer.get("risk_level", "low")
        
        if status != "active":
            logs.append(f"Warning: Customer account state is '{status}'.")
            return {
                "confidence_score": 0.20,
                "reasoning": f"Critical risk: customer account status is suspended/inactive."
            }
            
        if risk_level == "high":
            logs.append("Warning: Customer is flagged in AML/PEPs high-risk registries.")
            return {
                "confidence_score": 0.70,
                "reasoning": "Medium risk: customer matches high-risk profiling thresholds."
            }

        return {
            "confidence_score": 0.98,
            "reasoning": "Low risk: customer identity matches active registries."
        }
