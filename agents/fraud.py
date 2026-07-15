from typing import Any, Dict, List
from agents.base import BaseGovernanceAgent

class FraudAgent(BaseGovernanceAgent):
    """
    Evaluates transaction payment parameters to detect immediate fraud anomalies.
    """
    def __init__(self) -> None:
        super().__init__(name="FraudAgent")

    async def _execute(self, state: Dict[str, Any], logs: List[str]) -> Dict[str, Any]:
        tx_data = state.get("transaction", {})
        amount = tx_data.get("amount", 0.0)
        
        # Check context from prior device and kyc evaluations if present
        device_result = state.get("device_result", {})
        device_confidence = device_result.confidence_score if hasattr(device_result, "confidence_score") else 1.0
        
        logs.append(f"Evaluating transaction amount {amount} USD for fraud anomalies.")
        
        if amount > 50000.0:
            logs.append("Warning: Transaction exceeds standard fraud thresholds.")
            return {
                "confidence_score": 0.50,
                "reasoning": "High risk: transaction amount exceeds baseline limit threshold."
            }
            
        if device_confidence < 0.50:
            logs.append("Warning: High risk context inherited from device agent.")
            return {
                "confidence_score": 0.60,
                "reasoning": "Medium risk: transaction is accompanied by unsafe device signals."
            }

        return {
            "confidence_score": 0.94,
            "reasoning": "Low risk: transaction matches expected behavior clusters."
        }
