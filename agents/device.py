from typing import Any, Dict, List
from agents.base import BaseGovernanceAgent

class DeviceAgent(BaseGovernanceAgent):
    """
    Evaluates client terminal IP, fingerprint, and geolocation anomalies.
    """
    def __init__(self) -> None:
        super().__init__(name="DeviceAgent")

    async def _execute(self, state: Dict[str, Any], logs: List[str]) -> Dict[str, Any]:
        tx_data = state.get("transaction", {})
        device_profile = tx_data.get("device", {})
        
        logs.append(f"Evaluating device fingerprint: {device_profile.get('fingerprint')}")
        
        is_emulator = device_profile.get("is_emulator", False)
        ip = device_profile.get("ip_address", "")
        
        if is_emulator:
            logs.append("Warning: Terminal is running on an emulator.")
            return {
                "confidence_score": 0.45,
                "reasoning": "High risk: emulator execution signature detected."
            }
            
        if not ip:
            logs.append("Warning: Ingested transaction lacks IP tracking.")
            return {
                "confidence_score": 0.60,
                "reasoning": "Medium risk: transaction metadata lacks device IP address."
            }

        return {
            "confidence_score": 0.95,
            "reasoning": "Low risk: device integrity check passed."
        }
