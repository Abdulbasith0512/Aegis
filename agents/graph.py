from typing import Any, Dict, TypedDict
from langgraph.graph import StateGraph, START, END

from agents.base import AgentResponse
from agents.device import DeviceAgent
from agents.kyc import KYCAgent
from agents.fraud import FraudAgent
from agents.aml import AMLAgent
from agents.policy import PolicyAgent
from agents.explainability import ExplainabilityAgent
from agents.supervisor import SupervisorAgent

class AgentGraphState(TypedDict):
    """
    State schemas maintained across graph executions.
    """
    transaction: Dict[str, Any]
    device_result: AgentResponse
    kyc_result: AgentResponse
    fraud_result: AgentResponse
    aml_result: AgentResponse
    policy_result: AgentResponse
    explainability_result: AgentResponse
    supervisor_result: AgentResponse

# Initialize nodes as instances
device_agent = DeviceAgent()
kyc_agent = KYCAgent()
fraud_agent = FraudAgent()
aml_agent = AMLAgent()
policy_agent = PolicyAgent()
explain_agent = ExplainabilityAgent()
supervisor_agent = SupervisorAgent()

# Define Async Node functions mapping state mutations
async def run_device_agent(state: AgentGraphState) -> Dict[str, Any]:
    res = await device_agent.run(state)
    return {"device_result": res}

async def run_kyc_agent(state: AgentGraphState) -> Dict[str, Any]:
    res = await kyc_agent.run(state)
    return {"kyc_result": res}

async def run_fraud_agent(state: AgentGraphState) -> Dict[str, Any]:
    res = await fraud_agent.run(state)
    return {"fraud_result": res}

async def run_aml_agent(state: AgentGraphState) -> Dict[str, Any]:
    res = await aml_agent.run(state)
    return {"aml_result": res}

async def run_policy_agent(state: AgentGraphState) -> Dict[str, Any]:
    res = await policy_agent.run(state)
    return {"policy_result": res}

async def run_explainability_agent(state: AgentGraphState) -> Dict[str, Any]:
    res = await explain_agent.run(state)
    return {"explainability_result": res}

async def run_supervisor_agent(state: AgentGraphState) -> Dict[str, Any]:
    res = await supervisor_agent.run(state)
    return {"supervisor_result": res}

# Construct the StateGraph
workflow = StateGraph(AgentGraphState)

# Register Nodes
workflow.add_node("device_node", run_device_agent)
workflow.add_node("kyc_node", run_kyc_agent)
workflow.add_node("fraud_node", run_fraud_agent)
workflow.add_node("aml_node", run_aml_agent)
workflow.add_node("policy_node", run_policy_agent)
workflow.add_node("explainability_node", run_explainability_agent)
workflow.add_node("supervisor_node", run_supervisor_agent)

# Set Flow Transitions
# Execution sequence: START -> Device -> KYC -> Fraud -> AML -> Policy -> Explainability -> Supervisor -> END
workflow.add_edge(START, "device_node")
workflow.add_edge("device_node", "kyc_node")
workflow.add_edge("kyc_node", "fraud_node")
workflow.add_edge("fraud_node", "aml_node")
workflow.add_edge("aml_node", "policy_node")
workflow.add_edge("policy_node", "explainability_node")
workflow.add_edge("explainability_node", "supervisor_node")
workflow.add_edge("supervisor_node", END)

# Compile Graph
compiled_graph = workflow.compile()
