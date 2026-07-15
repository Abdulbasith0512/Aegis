import abc
from typing import Dict, Any, Tuple
from app.schemas.trust import TrustCalculationRequest

class BaseTrustEngine(abc.ABC):
    """
    Abstract Base Class for the Trust Calculation Engine.
    Subclasses can implement ML models (e.g. Random Forest, neural nets) or custom heuristic pipelines.
    """
    @abc.abstractmethod
    def calculate_score(self, telemetry: TrustCalculationRequest) -> Tuple[int, Dict[str, float], Dict[str, Any]]:
        """
        Computes Trust Score, returns (score, weights_configuration, reasons).
        """
        pass

class WeightedTrustEngine(BaseTrustEngine):
    """
    Baseline production heuristic model applying standard weighted parameters.
    Allows clear interpretability, warning triggers, and SLA latency scaling.
    """
    def __init__(self) -> None:
        # Default Weights config totaling 1.00
        self.weights = {
            "agent_confidence": 0.20,
            "historical_accuracy": 0.15,
            "model_drift": 0.10,
            "data_quality": 0.10,
            "latency": 0.05,
            "policy_compliance": 0.20,
            "explainability": 0.10,
            "agent_consensus": 0.10
        }

    def calculate_score(self, telemetry: TrustCalculationRequest) -> Tuple[int, Dict[str, float], Dict[str, Any]]:
        """
        Computes the final trust score (0 to 100).
        """
        reasons: Dict[str, Any] = {"warnings": [], "contributions": {}}

        # 1. Evaluate Latency SLA scale (SLA threshold = 100ms)
        # Latency above 100ms reduces latency security parameter linearly down to 1000ms.
        latency_val = 1.0
        if telemetry.latency_ms > 100.0:
            latency_val = max(0.0, 1.0 - ((telemetry.latency_ms - 100.0) / 900.0))
            reasons["warnings"].append(f"Latency exceeded 100ms SLA target: {telemetry.latency_ms:.1f}ms")

        # 2. Evaluate Policy Compliance
        compliance_val = 1.0 if telemetry.policy_compliance else 0.0
        if not telemetry.policy_compliance:
            reasons["warnings"].append("Deterministic policy check verification failed.")

        # 3. Evaluate Model Drift Warning
        drift_val = 1.0 - telemetry.model_drift
        if telemetry.model_drift > 0.30:
            reasons["warnings"].append(f"High model feature drift warning: {telemetry.model_drift:.2f}")

        # 4. Evaluate Data Quality
        if telemetry.data_quality < 0.90:
            reasons["warnings"].append(f"Poor transaction data quality ratio: {telemetry.data_quality:.2f}")

        # 5. Evaluate Consensus
        if telemetry.agent_consensus < 0.67:
            reasons["warnings"].append(f"Low supervisor consensus alignment: {telemetry.agent_consensus:.2f}")

        # Multiply inputs by their respective weights
        contrib = {
            "agent_confidence": telemetry.agent_confidence * self.weights["agent_confidence"],
            "historical_accuracy": telemetry.historical_accuracy * self.weights["historical_accuracy"],
            "model_drift": drift_val * self.weights["model_drift"],
            "data_quality": telemetry.data_quality * self.weights["data_quality"],
            "latency": latency_val * self.weights["latency"],
            "policy_compliance": compliance_val * self.weights["policy_compliance"],
            "explainability": telemetry.explainability_score * self.weights["explainability"],
            "agent_consensus": telemetry.agent_consensus * self.weights["agent_consensus"]
        }
        
        reasons["contributions"] = contrib

        # Total score calculation (0 to 100)
        total_sum = sum(contrib.values())
        final_score = int(round(total_sum * 100))

        return final_score, self.weights, reasons
