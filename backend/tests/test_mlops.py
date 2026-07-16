import pytest
import uuid
from typing import Dict, Any, List
from app.services.mlops import MLOpsService
from app.schemas.mlops import ModelVersionCreate, DeploymentConfigUpdate

class MockModelVersion:
    def __init__(self, id: uuid.UUID, agent_id: uuid.UUID, version_string: str, parameters_hash: str):
        self.id = id
        self.agent_id = agent_id
        self.version_string = version_string
        self.parameters_hash = parameters_hash
        self.accuracy_benchmark = 0.95
        self.hyperparameters = {}
        self.metrics = {}

class MockDeploymentConfig:
    def __init__(self, agent_id: uuid.UUID):
        self.agent_id = agent_id
        self.deployment_type = "production"
        self.active_version_id = None
        self.canary_version_id = None
        self.canary_split = 100
        self.shadow_version_id = None
        self.ab_version_a_id = None
        self.ab_version_b_id = None
        self.ab_split = 50

class MockAgentMLOpsRepository:
    def __init__(self):
        self.configs = {}
        self.versions = {}

    async def get_agent_by_name(self, name: str):
        class MockAgent:
            id = uuid.UUID("440c95ef-eeea-4c91-b956-621817293a55")
            name = "aml-agent"
        return MockAgent()

    async def get_deployment_config(self, agent_id: uuid.UUID):
        if agent_id not in self.configs:
            self.configs[agent_id] = MockDeploymentConfig(agent_id)
        return self.configs[agent_id]

    async def list_versions(self, agent_id: uuid.UUID):
        if agent_id not in self.versions:
            v1_id = uuid.UUID("c53c4573-cbcd-47d0-99c0-b8d4f09d290c")
            v2_id = uuid.UUID("9a97d4df-05df-4d6d-92a0-bdcf6193bf20")
            self.versions[agent_id] = [
                MockModelVersion(v1_id, agent_id, "v1.0.0", "hash1"),
                MockModelVersion(v2_id, agent_id, "v2.0.0-canary", "hash2"),
            ]
        return self.versions[agent_id]

@pytest.mark.anyio
async def test_mlops_service_routing():
    repo = MockAgentMLOpsRepository()
    service = MLOpsService(repo)

    # 1. Test Production routing
    route = await service.route_model_version("aml-agent")
    assert route["primary_version"] == "v1.0.0"
    assert route["shadow_version"] is None

    # 2. Test Canary Routing (forced 100% split)
    agent = await repo.get_agent_by_name("aml-agent")
    config = await repo.get_deployment_config(agent.id)
    versions = await repo.list_versions(agent.id)
    
    config.deployment_type = "canary"
    config.active_version_id = versions[0].id
    config.canary_version_id = versions[1].id
    config.canary_split = 100

    route_canary = await service.route_model_version("aml-agent")
    assert route_canary["primary_version"] == "v2.0.0-canary"
    assert route_canary["mode"] == "canary_active"

    # 3. Test Shadow Routing
    config.deployment_type = "production"
    config.shadow_version_id = versions[1].id
    route_shadow = await service.route_model_version("aml-agent")
    assert route_shadow["primary_version"] == "v1.0.0"
    assert route_shadow["shadow_version"] == "v2.0.0-canary"
