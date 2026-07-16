import os
import uuid
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("aegisai.mlflow")

# Try to import mlflow dynamically
try:
    import mlflow
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False

class MLflowSimulationAdapter:
    """
    MLflow Client Adapter that supports external MLflow server logging when available,
    and falls back to database-backed run logging.
    """
    def __init__(self) -> None:
        self.tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "")
        self.active_run_id: Optional[str] = None
        
        if MLFLOW_AVAILABLE and self.tracking_uri:
            try:
                mlflow.set_tracking_uri(self.tracking_uri)
                mlflow.set_experiment("AegisAI-Banking-Supervision")
                logger.info(f"MLflow Adapter successfully connected to: {self.tracking_uri}")
            except Exception as e:
                logger.warning(f"Failed to connect to MLflow server at {self.tracking_uri}: {e}")

    def log_run_to_server(self, agent_name: str, run_name: str, params: Dict[str, Any], metrics: Dict[str, Any]) -> Optional[str]:
        """
        Submits hyperparams and metrics directly to MLflow if tracking server is configured.
        """
        if not (MLFLOW_AVAILABLE and self.tracking_uri):
            return None

        try:
            with mlflow.start_run(run_name=run_name) as run:
                # Log hyperparameters
                for k, v in params.items():
                    mlflow.log_param(k, v)
                
                # Log metrics
                for k, v in metrics.items():
                    mlflow.log_metric(k, float(v))
                
                # Add tagging
                mlflow.set_tag("agent", agent_name)
                mlflow.set_tag("framework", "AegisAI-MLOps")
                
                logger.info(f"Logged run '{run_name}' to remote MLflow server successfully. Run ID: {run.info.run_id}")
                return run.info.run_id
        except Exception as e:
            logger.error(f"Error logging run to MLflow server: {e}")
            return None

# Global simulation adapter
mlflow_adapter = MLflowSimulationAdapter()
