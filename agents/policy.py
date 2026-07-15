from typing import Any, Dict, List
from agents.base import BaseGovernanceAgent

class PolicyAgent(BaseGovernanceAgent):
    """
    Validates proposed transaction metadata against strict banking constraints.
    """
    def __init__(self) -> None:
        super().__init__(name="PolicyAgent")

    async def _execute(self, state: Dict[str, Any], logs: List[str]) -> Dict[str, Any]:
        tx_data = state.get("transaction", {})
        amount = tx_data.get("amount", 0.0)
        currency = tx_data.get("currency", "USD")
        
        logs.append(f"Checking transaction policies against currency: {currency}")
        
        # Enforce strict policy: Block unapproved currencies
        if currency != "USD":
            logs.append("Warning: Cross-border transaction currency is not USD.")
            return {
                "confidence_score": 0.00,
                "reasoning": "Policy violation: only USD transactions are permitted under current settings."
            }
            
        if amount > 100000.0:
            logs.append("Warning: Transaction exceeds standard limit of 100,000 USD.")
            return {
                "confidence_score": 0.00,
                "reasoning": "Policy violation: transaction exceeds maximum allowed limit."
            }

        return {
            "confidence_score": 1.00,
            "reasoning": "Policy checks passed successfully."
        }
