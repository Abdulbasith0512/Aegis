import abc
import asyncio
import logging
import time
from typing import Any, Dict, List
from pydantic import BaseModel, Field

# Setup core agent logger
logger = logging.getLogger("aegisai.agents")

class AgentResponse(BaseModel):
    """
    Standard schema exposed by all AegisAI agents.
    """
    status: str = Field(..., description="Execution status: 'success' or 'failed'.")
    confidence_score: float = Field(..., description="Normalized confidence probability (0.0 to 1.0).")
    reasoning: str = Field(..., description="Plain-text justification of decision verdict.")
    execution_time: float = Field(..., description="Agent processing runtime duration in seconds.")
    logs: List[str] = Field(default_factory=list, description="Execution logging traces and warnings.")

class BaseGovernanceAgent(abc.ABC):
    """
    Abstract base class enforcing standard agent properties, logging, and retry logic.
    """
    def __init__(self, name: str, max_retries: int = 3, backoff_seconds: float = 0.5) -> None:
        self.name: str = name
        self.max_retries: int = max_retries
        self.backoff_seconds: float = backoff_seconds
        self.agent_logger = logging.getLogger(f"aegisai.agents.{name}")

    async def run(self, state: Dict[str, Any]) -> AgentResponse:
        """
        Main runner coordinating timing, standard error logging, and retry loops.
        """
        logs: List[str] = []
        start_time = time.perf_counter()
        
        attempt = 0
        while attempt < self.max_retries:
            try:
                attempt += 1
                logs.append(f"Starting execution attempt {attempt}...")
                
                # Execute agent-specific logic
                result = await self._execute(state, logs)
                
                end_time = time.perf_counter()
                execution_time = end_time - start_time
                logs.append("Execution completed successfully.")
                
                return AgentResponse(
                    status="success",
                    confidence_score=result.get("confidence_score", 1.0),
                    reasoning=result.get("reasoning", "No reasons specified."),
                    execution_time=execution_time,
                    logs=logs
                )
            except Exception as e:
                self.agent_logger.warning(f"Attempt {attempt} failed: {e}")
                logs.append(f"Attempt {attempt} failed: {str(e)}")
                if attempt >= self.max_retries:
                    end_time = time.perf_counter()
                    execution_time = end_time - start_time
                    logs.append("Maximum execution retries exceeded. Failing.")
                    return AgentResponse(
                        status="failed",
                        confidence_score=0.0,
                        reasoning=f"Agent runtime failure: {str(e)}",
                        execution_time=execution_time,
                        logs=logs
                    )
                # Exponential backoff sleep
                await asyncio.sleep(self.backoff_seconds * (2 ** (attempt - 1)))

    @abc.abstractmethod
    async def _execute(self, state: Dict[str, Any], logs: List[str]) -> Dict[str, Any]:
        """
        Core logic to be implemented by child classes.
        """
        pass
