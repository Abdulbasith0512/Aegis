import pytest
from app.services.chaos_engine import DynamicChaosEngine

def test_chaos_engine_kill_agent_execution() -> None:
    """
    Verifies that killing an AI agent triggers consensus failures.
    """
    engine = DynamicChaosEngine()
    metrics = engine.execute_fault_injection(scenario="kill_agent", target_agent="fraud-agent")
    
    assert metrics["consensus_failure_triggered"] is True
    assert metrics["recovery_time_seconds"] >= 4.5
    assert metrics["trust_drop_index"] == 30.0
    assert metrics["recovery_success"] is True

def test_chaos_engine_prompt_injection_execution() -> None:
    """
    Verifies that prompt injections trigger compliance policy violations.
    """
    engine = DynamicChaosEngine()
    metrics = engine.execute_fault_injection(scenario="prompt_injection", target_agent="kyc-agent")
    
    assert metrics["consensus_failure_triggered"] is False
    assert metrics["policy_violations_triggered"] == 1
    assert metrics["trust_drop_index"] == 45.0
    assert metrics["recovery_success"] is True

def test_chaos_engine_api_failure_metrics() -> None:
    """
    Verifies that API failures register a recovery success failure flag.
    """
    engine = DynamicChaosEngine()
    metrics = engine.execute_fault_injection(scenario="api_failure", target_agent="system")
    
    assert metrics["recovery_success"] is False
    assert metrics["trust_drop_index"] == 25.0
