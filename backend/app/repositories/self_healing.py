import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.governance import HealingIncident, RecoveryAction

class SelfHealingRepository:
    """
    Handles database operations for HealingIncident and RecoveryAction entities.
    """
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_incident(
        self,
        agent_name: str,
        failure_type: str,
        description: str
    ) -> HealingIncident:
        """
        Creates and registers an anomaly incident log.
        """
        incident = HealingIncident(
            agent_name=agent_name,
            failure_type=failure_type,
            description=description,
            status="detected"
        )
        self.db.add(incident)
        await self.db.commit()
        await self.db.refresh(incident)
        return incident

    async def resolve_incident(self, incident_id: uuid.UUID) -> Optional[HealingIncident]:
        """
        Sets incident status to 'resolved'.
        """
        incident = await self.db.get(HealingIncident, incident_id)
        if not incident:
            return None
        incident.status = "resolved"
        incident.resolved_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(incident)
        return incident

    async def add_recovery_action(
        self,
        incident_id: uuid.UUID,
        action_step: str,
        status: str = "pending",
        details: Optional[Dict[str, Any]] = None
    ) -> RecoveryAction:
        """
        Appends a recovery step to an incident log.
        """
        action = RecoveryAction(
            incident_id=incident_id,
            action_step=action_step,
            status=status,
            details=details
        )
        self.db.add(action)
        await self.db.commit()
        await self.db.refresh(action)
        return action

    async def update_recovery_action_status(
        self,
        action_id: uuid.UUID,
        status: str,
        details: Optional[Dict[str, Any]] = None
    ) -> Optional[RecoveryAction]:
        """Updates the status of an existing recovery step."""
        action = await self.db.get(RecoveryAction, action_id)
        if not action:
            return None
        action.status = status
        if details is not None:
            action.details = details
        await self.db.commit()
        await self.db.refresh(action)
        return action

    async def list_active_incidents(self, limit: int = 50) -> List[HealingIncident]:
        """Lists incidents currently unresolved (detected, healing, or failed)."""
        result = await self.db.execute(
            select(HealingIncident)
            .where(HealingIncident.status != "resolved")
            .options(selectinload(HealingIncident.recovery_actions))
            .order_by(HealingIncident.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list_all_incidents(self, limit: int = 50) -> List[HealingIncident]:
        """Lists all historical and current incidents."""
        result = await self.db.execute(
            select(HealingIncident)
            .options(selectinload(HealingIncident.recovery_actions))
            .order_by(HealingIncident.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_incident_details(self, incident_id: uuid.UUID) -> Optional[HealingIncident]:
        """Eagerly loads incident record containing recovery steps list."""
        result = await self.db.execute(
            select(HealingIncident)
            .where(HealingIncident.id == incident_id)
            .options(selectinload(HealingIncident.recovery_actions))
        )
        return result.scalars().first()

class BackupModelRegistry:
    """Backup Registry to simulate version mappings."""
    def __init__(self) -> None:
        self.registry = {
            "fraud-agent": {"active": "v2.0.0-drift", "backup": "v1.9.0-stable"},
            "aml-agent": {"active": "v1.2.0-slow", "backup": "v1.1.5-stable"},
            "kyc-agent": {"active": "v2.1.0-poisoned", "backup": "v2.0.0-stable"}
        }

    def get_backup_version(self, agent_name: str) -> str:
        return self.registry.get(agent_name, {}).get("backup", "v1.0.0-baseline")
