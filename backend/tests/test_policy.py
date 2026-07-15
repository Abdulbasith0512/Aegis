import pytest
from app.services.policy_engine import PolicyEngine

def test_policy_engine_resolve_nested_fields() -> None:
    """
    Verifies that the policy engine can extract nested parameters using dot-notation paths.
    """
    mock_tx = {
        "amount": 2500.00,
        "account": {
            "status": "active",
            "customer": {
                "risk_tier": "low"
            }
        }
    }
    
    engine = PolicyEngine()
    
    assert engine.resolve_field("amount", mock_tx) == 2500.00
    assert engine.resolve_field("account.status", mock_tx) == "active"
    assert engine.resolve_field("account.customer.risk_tier", mock_tx) == "low"
    assert engine.resolve_field("account.non_existent", mock_tx) is None

def test_policy_engine_rule_comparisons() -> None:
    """
    Verifies that logic operators run successfully.
    """
    engine = PolicyEngine()
    
    # Equals checks
    assert engine.evaluate_rule("equals", "USD", "USD") is True
    assert engine.evaluate_rule("equals", "USD", "EUR") is False
    
    # Comparison checks
    assert engine.evaluate_rule("less_than_or_equal", 10000.0, 5000.0) is True
    assert engine.evaluate_rule("less_than_or_equal", 10000.0, 15000.0) is False
    
    # Between / Not Between checks
    assert engine.evaluate_rule("not_between", [4500.0, 5000.0], 4800.0) is False
    assert engine.evaluate_rule("not_between", [4500.0, 5000.0], 2500.0) is True

def test_policy_engine_transaction_evaluation_pass() -> None:
    """
    Verifies that a valid transaction complies with standard policies.
    """
    mock_tx = {
        "amount": 250.00,
        "currency": "USD",
        "account": {
            "status": "active"
        }
    }
    
    engine = PolicyEngine()
    res = engine.evaluate_transaction(mock_tx)
    
    # Overall status should pass (trust_score is not in the transaction so that rule skips/fails,
    # but let's check since POL-GOV-404 requires trust_score >= 75. If trust_score is missing, it will return False.
    # So we should pass a mock trust_score as well!)
    mock_tx["trust_score"] = 90
    res = engine.evaluate_transaction(mock_tx)
    
    assert res.overall_status == "pass"
    for p in res.policies_checked:
        assert p.status == "pass"

def test_policy_engine_transaction_evaluation_structuring_block() -> None:
    """
    Verifies that structured transaction amounts (smurfing check) get blocked.
    """
    mock_tx = {
        "amount": 4800.00, # AML structuring warning: between 4500 and 5000
        "currency": "USD",
        "trust_score": 92,
        "account": {
            "status": "active"
        }
    }
    
    engine = PolicyEngine()
    res = engine.evaluate_transaction(mock_tx)
    
    assert res.overall_status == "fail"
    # Locate AML policy and check that it failed
    aml_policy = next(p for p in res.policies_checked if p.policy_id == "POL-AML-202")
    assert aml_policy.status == "fail"
