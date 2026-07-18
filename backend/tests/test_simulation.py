import pytest
import uuid
import asyncio
from app.models.simulation import SimulationScenario
from app.services.simulation_engine import SyntheticDataGenerator, FailureInjector

def test_synthetic_data_distribution():
    scenario = SimulationScenario(
        num_transactions=1000,
        fraud_percentage=0.05,
        drift_percentage=0.10
    )
    
    dist = SyntheticDataGenerator.calculate_distribution(scenario)
    assert dist["fraud"] == 50
    assert dist["drift"] == 100
    assert dist["normal"] == 850
    assert sum(dist.values()) == 1000

def test_failure_injector_no_failures():
    injector = FailureInjector([])
    
    # Should not add latency
    latency = injector.get_latency_ms(100.0)
    assert latency == 100.0
    
    # Should not crash
    assert not injector.simulate_agent_crash()
    
    # Should not drift
    acc = injector.adjust_accuracy(0.95)
    assert acc == 0.95

def test_failure_injector_with_failures():
    injector = FailureInjector(["db_latency", "model_drift"])
    
    # Should add latency (at least 500ms)
    latency = injector.get_latency_ms(100.0)
    assert latency >= 600.0
    
    # Should drop accuracy
    acc = injector.adjust_accuracy(0.95)
    assert acc < 0.95
