import sys
import os
import pytest

# Ensure the root directory is in the PYTHONPATH to find the top-level agents directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from agents import run_governance_graph

@pytest.mark.anyio
async def test_normal_approved_transaction() -> None:
    """
    Verifies that a standard low-risk transaction flows successfully and gets approved.
    """
    mock_transaction = {
        "amount": 250.00,
        "currency": "USD",
        "reference_number": "TX-99882",
        "device": {
            "fingerprint": "dev-12345",
            "ip_address": "192.168.1.50",
            "is_emulator": False
        },
        "account": {
            "customer": {
                "email": "customer_test@gmail.com",
                "status": "active",
                "risk_level": "low"
            }
        }
    }
    
    result = await run_governance_graph(mock_transaction)
    
    assert result["status"] == "success"
    assert result["verdict"] == "approved"
    assert result["trust_score"] >= 75
    
    # Assert all sub-agent outputs exist
    details = result["details"]
    assert details["device"].status == "success"
    assert details["kyc"].status == "success"
    assert details["fraud"].status == "success"
    assert details["aml"].status == "success"
    assert details["policy"].status == "success"
    assert details["explainability"].status == "success"

@pytest.mark.anyio
async def test_emulator_warning_review_verdict() -> None:
    """
    Verifies that emulator usage decreases the trust score, triggering under_review.
    """
    mock_transaction = {
        "amount": 1200.00,
        "currency": "USD",
        "reference_number": "TX-99883",
        "device": {
            "fingerprint": "dev-emu",
            "ip_address": "10.0.0.8",
            "is_emulator": True # Emulator risk triggers
        },
        "account": {
            "customer": {
                "email": "customer_test@gmail.com",
                "status": "active",
                "risk_level": "low"
            }
        }
    }
    
    result = await run_governance_graph(mock_transaction)
    
    assert result["status"] == "success"
    assert result["verdict"] == "under_review"
    assert result["trust_score"] < 75

@pytest.mark.anyio
async def test_non_usd_currency_policy_block() -> None:
    """
    Verifies that transactions in EUR/non-USD currencies fail policy checks and get declined.
    """
    mock_transaction = {
        "amount": 100.00,
        "currency": "EUR", # Non-USD trigger
        "reference_number": "TX-99884",
        "device": {
            "fingerprint": "dev-12345",
            "ip_address": "192.168.1.50",
            "is_emulator": False
        },
        "account": {
            "customer": {
                "email": "customer_test@gmail.com",
                "status": "active",
                "risk_level": "low"
            }
        }
    }
    
    result = await run_governance_graph(mock_transaction)
    
    assert result["status"] == "success"
    assert result["verdict"] == "declined"
