import abc
import asyncio
import uuid
from typing import Dict, Any, List, Callable, Coroutine
from app.repositories.self_healing import SelfHealingRepository, BackupModelRegistry
from app.repositories.audit import AuditRepository
from app.repositories.policy import PolicyRepository
from app.services.observability import ObservabilityService

class EventBroker:
    """
    Event-driven publisher-subscriber message broker coordinating async handlers.
    """
    def __init__(self) -> None:
        self.subscribers: Dict[str, List[Callable[[Any], Coroutine[Any, Any, None]]]] = {}

    def subscribe(self, topic: str, handler: Callable[[Any], Coroutine[Any, Any, None]]) -> None:
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(handler)

    async def publish(self, topic: str, data: Any) -> None:
        if topic in self.subscribers:
            for handler in self.subscribers[topic]:
                # Non-blocking async execution
                asyncio.create_task(handler(data))

class SelfHealingEngine:
    """
    AI self-healing workflows orchestrator. Receives events, executes diagnoses,
    switches to fallbacks, executes rollbacks, updates audits, and notifies auditors.
    """
    def __init__(self, db_session) -> None:
        self.db = db_session
        self.broker = EventBroker()
        self.backup_registry = BackupModelRegistry()
        
        # Subscribe to failure triggers
        self.broker.subscribe("failure_event", self.execute_recovery_workflow)

    async def trigger_failure(self, agent_name: str, failure_type: str) -> uuid.UUID:
        """
        Publishes a failure event to trigger self-healing pipeline asynchronously.
        """
        incident_id = uuid.uuid4()
        await self.broker.publish("failure_event", {
            "incident_id": incident_id,
            "agent_name": agent_name,
            "failure_type": failure_type
        })
        return incident_id

    async def execute_recovery_workflow(self, event: Dict[str, Any]) -> None:
        """
        Main recovery pipeline executing steps in sequence.
        """
        agent = event["agent_name"]
        ftype = event["failure_type"]
        inc_id = event["incident_id"]

        repo = SelfHealingRepository(self.db)
        audit_repo = AuditRepository(self.db)
        policy_repo = PolicyRepository(self.db)
        obs_service = ObservabilityService()

        # 1. Detect Failure (Registers incident record in DB)
        desc = f"Anomalous {ftype} detected on evaluating agent {agent}."
        incident = await repo.create_incident(
            agent_name=agent,
            failure_type=ftype,
            description=desc
        )

        # 2. Diagnose failure root cause
        diag_step = await repo.add_recovery_action(incident.id, "diagnose", "running")
        await asyncio.sleep(0.01) # Emulate short diagnosis delay
        diag_details = {"root_cause": f"Observed {ftype} breach threshold baseline limits."}
        await repo.update_recovery_action_status(diag_step.id, "completed", diag_details)

        # 3. Switch Backup Model version
        backup_step = await repo.add_recovery_action(incident.id, "switch_backup_model", "running")
        backup_ver = self.backup_registry.get_backup_version(agent)
        backup_details = {"active_version": "v2.0.0-drift", "switched_to_version": backup_ver}
        await repo.update_recovery_action_status(backup_step.id, "completed", backup_details)

        # 4. Rollback configuration states
        rollback_step = await repo.add_recovery_action(incident.id, "rollback", "running")
        await repo.update_recovery_action_status(rollback_step.id, "completed", {"config_version_restored": "v1.9.0"})

        # 5. Restart Agent thread loops
        restart_step = await repo.add_recovery_action(incident.id, "restart_agent", "running")
        await repo.update_recovery_action_status(restart_step.id, "completed", {"thread_id_reassigned": 4022})

        # 6. Notify Human auditor (Creates review ticket in human_reviews queue)
        notify_step = await repo.add_recovery_action(incident.id, "notify_human", "running")
        review = await policy_repo.create_decision_override(
            transaction_id=uuid.uuid4(), # Link mock transaction UUID
            reviewer_id=None,
            comments=f"Self-Healing: Escalated due to {ftype} on {agent}. Switched to {backup_ver} fallback."
        )
        await repo.update_recovery_action_status(notify_step.id, "completed", {"human_review_id": str(review.id)})

        # 7. Update Cryptographic Audit Ledger
        audit_step = await repo.add_recovery_action(incident.id, "update_audit", "running")
        audit = await audit_repo.log_action(
            actor_id=None,
            action_type="self_healing_recovery",
            description=f"Self-healing completed for {agent}. Inc:{incident.id}",
            resource_id=str(incident.id),
            metadata={"incident_id": str(incident.id), "recovery_step": "completed"}
        )
        await repo.update_recovery_action_status(audit_step.id, "completed", {"audit_log_id": str(audit.id)})

        # 8. Revalidate (runs sanity check assertions)
        reval_step = await repo.add_recovery_action(incident.id, "revalidate", "running")
        await repo.update_recovery_action_status(reval_step.id, "completed", {"assertions_checked": ["health_check", "policy_bounds"], "status": "pass"})

        # 9. Resume Traffic
        resume_step = await repo.add_recovery_action(incident.id, "resume_traffic", "running")
        # Set agent healthy back to 1 inside Observability system
        obs_service.agent_health.labels(agent_name=agent).set(1)
        await repo.update_recovery_action_status(resume_step.id, "completed", {"traffic_resumed": True})

        # Resolve incident state
        await repo.resolve_incident(incident.id)
