import uuid
import time
import logging
from typing import Dict, Any, List, Tuple, Union
import numpy as np
import networkx as nx
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, IsolationForest
from sklearn.neighbors import LocalOutlierFactor

logger = logging.getLogger("aegisai.ml.models")

# -----------------
# Base Model Class
# -----------------
class BaseAegisModel:
    """
    Standard interface exposed by all AegisAI machine learning governance models.
    """
    def __init__(self, name: str, version: str) -> None:
        self._name = name
        self._version = version
        self._status = "healthy"
        self._is_trained = False

    def predict(self, features: Union[List[float], Dict[str, Any]]) -> int:
        """Predicts binary decision (0 for normal, 1 for anomaly/risk)."""
        raise NotImplementedError()

    def predict_proba(self, features: Union[List[float], Dict[str, Any]]) -> float:
        """Predicts risk probability (0.0 to 1.0)."""
        raise NotImplementedError()

    def confidence_score(self, features: Union[List[float], Dict[str, Any]]) -> float:
        """Returns normalized confidence probability (0.0 to 1.0)."""
        raise NotImplementedError()

    def model_version(self) -> str:
        return self._version

    def health_status(self) -> str:
        return self._status

# -----------------
# Fraud Model
# -----------------
class AegisFraudModel(BaseAegisModel):
    """
    Evaluates transactional parameters using Scikit-Learn RandomForest and GradientBoosting Classifiers.
    Feature vector format: [amount, device_is_emulator, location_match, risk_tier]
    """
    def __init__(self) -> None:
        super().__init__(name="AegisFraudModel", version="v1.0.0")
        self.rf = RandomForestClassifier(n_estimators=10, random_state=42)
        self.gb = GradientBoostingClassifier(n_estimators=10, random_state=42)
        self._train_initial()

    def _train_initial(self) -> None:
        """Trains models on initial synthetic distributions."""
        try:
            # 100 sample synthetic records
            # Features: [amount (scaled), device_is_emulator (0/1), location_match (0/1), customer_risk_level (0=low, 1=med, 2=high)]
            X = []
            y = []
            for _ in range(80): # Normal transactions
                X.append([np.random.uniform(10, 3000), 0, 1, np.random.choice([0, 1])])
                y.append(0)
            for _ in range(20): # Fraudulent transactions
                X.append([np.random.uniform(5000, 50000), np.random.choice([0, 1]), np.random.choice([0, 1]), np.random.choice([1, 2])])
                y.append(1)

            X_arr = np.array(X)
            y_arr = np.array(y)

            # Fit RF and GB ensemble
            self.rf.fit(X_arr, y_arr)
            self.gb.fit(X_arr, y_arr)
            self._is_trained = True
            logger.info("AegisFraudModel trained successfully.")
        except Exception as e:
            self._status = "degraded"
            logger.error(f"Failed to train AegisFraudModel: {e}")

    def _prepare_features(self, features: Union[List[float], Dict[str, Any]]) -> np.ndarray:
        if isinstance(features, dict):
            # Parse dict keys
            amount = float(features.get("amount", 0.0))
            is_emulator = 1 if features.get("device_is_emulator", False) else 0
            location_match = 1 if features.get("location_match", True) else 0
            risk_tier = 2 if features.get("customer_risk", "medium") == "high" else (1 if features.get("customer_risk") == "medium" else 0)
            features = [amount, is_emulator, location_match, risk_tier]
        return np.array(features).reshape(1, -1)

    def predict(self, features: Union[List[float], Dict[str, Any]]) -> int:
        if not self._is_trained:
            return 0
        X = self._prepare_features(features)
        return int(self.rf.predict(X)[0])

    def predict_proba(self, features: Union[List[float], Dict[str, Any]]) -> float:
        if not self._is_trained:
            return 0.05
        X = self._prepare_features(features)
        # Average ensemble probability
        prob_rf = self.rf.predict_proba(X)[0][1]
        prob_gb = self.gb.predict_proba(X)[0][1]
        return float((prob_rf + prob_gb) / 2)

    def confidence_score(self, features: Union[List[float], Dict[str, Any]]) -> float:
        """Returns safety/trust level (1.0 - risk probability)."""
        prob = self.predict_proba(features)
        return float(1.0 - prob)

# -----------------
# Behavior Anomaly Model
# -----------------
class AegisBehaviorModel(BaseAegisModel):
    """
    Evaluates transaction behavior anomalies using Isolation Forest.
    Features: [amount, hourly_velocity, loc_distance]
    """
    def __init__(self) -> None:
        super().__init__(name="AegisBehaviorModel", version="v1.0.0")
        self.clf = IsolationForest(n_estimators=10, random_state=42)
        self._train_initial()

    def _train_initial(self) -> None:
        try:
            X = []
            for _ in range(100):
                # Normal amounts centered around 50-500 USD, velocity 1-3, distance 0-10
                X.append([np.random.normal(200, 100), np.random.normal(2, 1), np.random.normal(5, 5)])
            self.clf.fit(np.array(X))
            self._is_trained = True
            logger.info("AegisBehaviorModel trained successfully.")
        except Exception as e:
            self._status = "degraded"
            logger.error(f"Failed to train AegisBehaviorModel: {e}")

    def _prepare_features(self, features: Union[List[float], Dict[str, Any]]) -> np.ndarray:
        if isinstance(features, dict):
            amount = float(features.get("amount", 0.0))
            velocity = float(features.get("velocity", 1.0))
            dist = float(features.get("location_distance", 0.0))
            features = [amount, velocity, dist]
        return np.array(features).reshape(1, -1)

    def predict(self, features: Union[List[float], Dict[str, Any]]) -> int:
        if not self._is_trained:
            return 0
        X = self._prepare_features(features)
        # Isolation Forest returns -1 for anomalies, 1 for normal
        pred = self.clf.predict(X)[0]
        return 1 if pred == -1 else 0

    def predict_proba(self, features: Union[List[float], Dict[str, Any]]) -> float:
        if not self._is_trained:
            return 0.05
        X = self._prepare_features(features)
        # Convert decision function score to risk probability
        score = self.clf.decision_function(X)[0] # range [-0.5, 0.5] typically
        # Normalize score to [0, 1] risk probability where lower score = more anomalous
        prob = float(1.0 - (score + 0.5))
        return max(0.0, min(1.0, prob))

    def confidence_score(self, features: Union[List[float], Dict[str, Any]]) -> float:
        return float(1.0 - self.predict_proba(features))

# -----------------
# AML Graph Engine
# -----------------
class AegisAmlModel(BaseAegisModel):
    """
    Evaluates graph transfer networks to detect cycles and structuring rule breaches.
    """
    def __init__(self) -> None:
        super().__init__(name="AegisAmlModel", version="v1.0.0")
        self._is_trained = True

    def build_network_graph(self, tx_list: List[Dict[str, Any]]) -> nx.DiGraph:
        """
        Builds a directed transaction relationship graph from history.
        """
        G = nx.DiGraph()
        for tx in tx_list:
            src = str(tx.get("customer_id"))
            dst = str(tx.get("beneficiary_id"))
            amount = float(tx.get("amount", 0.0))
            if src and dst and src != "None" and dst != "None":
                if G.has_edge(src, dst):
                    G[src][dst]["weight"] += amount
                    G[src][dst]["count"] += 1
                else:
                    G.add_edge(src, dst, weight=amount, count=1)
        return G

    def predict(self, features: Union[List[float], Dict[str, Any]]) -> int:
        # returns 1 if high risk, else 0
        return 1 if self.predict_proba(features) > 0.60 else 0

    def predict_proba(self, features: Union[List[float], Dict[str, Any]]) -> float:
        """
        Calculates AML risk based on graph attributes and structuring alerts.
        """
        if not isinstance(features, dict):
            return 0.05

        amount = float(features.get("amount", 0.0))
        tx_history = features.get("history", [])
        customer_id = str(features.get("customer_id"))

        risk = 0.0

        # Structuring check: Just below $10,000 bounds or $5,000 bounds
        if 4800.0 <= amount < 5000.0 or 9500.0 <= amount < 10000.0:
            risk += 0.40

        # Graph cycle and routing check
        if tx_history and customer_id:
            try:
                G = self.build_network_graph(tx_history)
                # Check for cycle containment in the graph
                cycles = list(nx.simple_cycles(G))
                has_cycle = any(customer_id in cycle for cycle in cycles)
                if has_cycle:
                    risk += 0.45

                # Out-degree centrality (high volume of transfers out to different recipients)
                if G.has_node(customer_id):
                    deg = G.out_degree(customer_id)
                    if deg > 5:
                        risk += 0.15
            except Exception as e:
                logger.error(f"AML Graph evaluation error: {e}")

        return min(1.0, max(0.0, risk))

    def confidence_score(self, features: Union[List[float], Dict[str, Any]]) -> float:
        return float(1.0 - self.predict_proba(features))

# -----------------
# KYC Classifier
# -----------------
class AegisKycModel(BaseAegisModel):
    """
    Evaluates client document validity and profiling rules.
    """
    def __init__(self) -> None:
        super().__init__(name="AegisKycModel", version="v1.0.0")
        self._is_trained = True

    def predict(self, features: Union[List[float], Dict[str, Any]]) -> int:
        return 1 if self.predict_proba(features) > 0.60 else 0

    def predict_proba(self, features: Union[List[float], Dict[str, Any]]) -> float:
        """
        Calculates verification alignment failures.
        """
        if not isinstance(features, dict):
            return 0.05

        is_doc_matched = features.get("require_document_match", True)
        customer_status = features.get("customer_status", "active")
        risk_level = features.get("risk_level", "medium")

        risk = 0.0
        if not is_doc_matched:
            risk += 0.70
        if customer_status != "active":
            risk += 0.20
        if risk_level == "high":
            risk += 0.10

        return min(1.0, max(0.0, risk))

    def confidence_score(self, features: Union[List[float], Dict[str, Any]]) -> float:
        return float(1.0 - self.predict_proba(features))


# Global estimators dictionary instantiated at boot
fraud_estimator = AegisFraudModel()
behavior_estimator = AegisBehaviorModel()
aml_estimator = AegisAmlModel()
kyc_estimator = AegisKycModel()
