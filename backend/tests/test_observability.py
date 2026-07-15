import pytest
from app.services.observability import ObservabilityService

def test_prometheus_metrics_generation() -> None:
    """
    Verifies that raw Prometheus scraping outputs compile as string lines.
    """
    service = ObservabilityService()
    content, media_type = service.generate_prometheus_metrics()
    
    assert len(content) > 0
    assert "text/plain" in media_type
    assert b"aegis_system_cpu_percent" in content
    assert b"aegis_trust_score" in content

def test_observability_summary_extraction() -> None:
    """
    Verifies that visual observability dashboard parameters extract correctly.
    """
    service = ObservabilityService()
    summary = service.get_observability_summary()
    
    # Check hardware keys
    assert "cpu_percent" in summary["system_metrics"]
    assert "gpu_percent" in summary["system_metrics"]
    assert "memory_percent" in summary["system_metrics"]
    
    # Check agent key structures
    assert len(summary["agent_metrics"]) == 7
    first_agent = summary["agent_metrics"][0]
    assert "agent_name" in first_agent
    assert "latency_ms" in first_agent
    assert "prompt_tokens" in first_agent

def test_recording_custom_metrics() -> None:
    """
    Verifies that recording metrics updates active Prometheus values.
    """
    service = ObservabilityService()
    service.record_agent_execution(
        agent_name="fraud-agent",
        duration_seconds=0.250,
        tokens_prompt=120,
        tokens_completion=45,
        confidence=0.92,
        trust_score=88.5,
        error_occurred=False,
        drift=0.02,
        hallucination_rate=0.01
    )
    
    # Trust score should have updated to 88.5
    assert service.trust_score_gauge._value.get() == 88.5
