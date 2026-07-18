import pytest
import uuid
from typing import Dict, Any
from app.schemas.transaction import TransactionInterceptRequest
from ml.models import fraud_estimator, behavior_estimator, aml_estimator, kyc_estimator
from app.services.vector_store import AegisVectorStore

def test_transaction_intercept_request_validation() -> None:
    """Verifies Pydantic validation on incoming transaction requests."""
    cust_id = uuid.uuid4()
    payload = {
        "customer_id": str(cust_id),
        "amount": 250.0,
        "currency": "USD",
        "channel": "mobile",
        "transaction_type": "transfer",
        "device": {
            "fingerprint": "dev_fingerprint_abc",
            "ip_address": "192.168.1.1",
            "is_emulator": False
        }
    }
    
    req = TransactionInterceptRequest(**payload)
    assert req.customer_id == cust_id
    assert req.amount == 250.0
    assert req.currency == "USD"
    assert req.device.fingerprint == "dev_fingerprint_abc"

def test_real_ml_estimators_predict() -> None:
    """Checks prediction output ranges and probas for scikit-learn models."""
    # Test Fraud RFC/GBC Ensemble
    features_safe = {"amount": 100.0, "device_is_emulator": False, "location_match": True, "customer_risk": "low"}
    features_risk = {"amount": 45000.0, "device_is_emulator": True, "location_match": False, "customer_risk": "high"}

    assert fraud_estimator.predict_proba(features_safe) < 0.30
    assert fraud_estimator.predict_proba(features_risk) > 0.60
    assert 0.0 <= fraud_estimator.confidence_score(features_safe) <= 1.0

    # Test Behavior Anomaly IsolationForest
    behavior_safe = {"amount": 200.0, "velocity": 2.0, "location_distance": 5.0}
    behavior_anomaly = {"amount": 95000.0, "velocity": 45.0, "location_distance": 8500.0}

    assert behavior_estimator.predict_proba(behavior_safe) < 0.50
    assert behavior_estimator.predict_proba(behavior_anomaly) > 0.50

    # Test AML Network/Structuring
    aml_structuring = {"amount": 4900.0, "customer_id": "cust_a", "beneficiary_id": "cust_b", "history": []}
    assert aml_estimator.predict_proba(aml_structuring) >= 0.40

    # Test KYC matches
    kyc_fail = {"require_document_match": False, "customer_status": "suspended", "risk_level": "high"}
    assert kyc_estimator.predict_proba(kyc_fail) > 0.80

def test_deterministic_vector_store_embeddings() -> None:
    """Verifies that vector hashing creates 384 dimensional normalized vectors."""
    # Create vector store with a mock qdrant client (None is fine as we trigger fallback)
    store = AegisVectorStore(client=None)
    store.use_fallback = True

    exp_text1 = "Transaction flagged. Warnings: Emulator terminal profile signature matched."
    exp_text2 = "Transaction clean: fits standard behavioral and profiling limits."

    v1 = store.generate_embedding(exp_text1)
    v2 = store.generate_embedding(exp_text2)

    assert len(v1) == 384
    assert len(v2) == 384
    
    # Check L2 Normalization (dot product of normalized vector with itself should be ~1.0)
    norm = sum(x*x for x in v1)
    assert abs(norm - 1.0) < 1e-5
