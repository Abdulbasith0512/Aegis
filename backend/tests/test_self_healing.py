import pytest
import asyncio
from app.services.self_healing import EventBroker, BackupModelRegistry

def test_event_broker_dispatch() -> None:
    """
    Verifies that the EventBroker publishes events to registered callbacks.
    """
    broker = EventBroker()
    received_data = []

    async def mock_handler(data: dict) -> None:
        received_data.append(data)

    broker.subscribe("test_topic", mock_handler)
    
    async def run_test() -> None:
        await broker.publish("test_topic", {"status": "triggered"})
        await asyncio.sleep(0.01)

    asyncio.run(run_test())
    
    assert len(received_data) == 1
    assert received_data[0]["status"] == "triggered"

def test_backup_registry_mappings() -> None:
    """
    Verifies that backup versions are correctly queried from the registry.
    """
    registry = BackupModelRegistry()
    assert registry.get_backup_version("fraud-agent") == "v1.9.0-stable"
    assert registry.get_backup_version("nonexistent") == "v1.0.0-baseline"
