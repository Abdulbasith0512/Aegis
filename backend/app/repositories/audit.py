import hashlib
import json
import uuid
from typing import Any, Dict, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.governance import AuditLog

class AuditRepository:
    """
    Handles appending cryptographic ledger audit logs inside PostgreSQL.
    Enforces WORM-compliance via SHA-256 hashing links.
    """
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def log_action(
        self,
        action_type: str,
        description: str,
        actor_id: Optional[uuid.UUID] = None,
        resource_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """
        Creates and signs a new audit log record.
        Chains hashes: SHA256(Record_n + Hash_n-1).
        """
        # 1. Fetch previous hash
        prev_result = await self.db.execute(
            select(AuditLog).order_by(AuditLog.created_at.desc()).limit(1)
        )
        prev_log = prev_result.scalars().first()
        prev_hash: str = prev_log.ledger_hash if prev_log else "0" * 64

        # 2. Serialize payload details to build chain signature
        meta_str: str = json.dumps(metadata, sort_keys=True) if metadata else "{}"
        payload_data: str = (
            f"{actor_id or ''}|{action_type}|{description}|{resource_id or ''}|"
            f"{meta_str}|{prev_hash}"
        )

        # 3. Calculate SHA-256 checksum
        current_hash: str = hashlib.sha256(payload_data.encode("utf-8")).hexdigest()

        # 4. Save audit log record
        log_record = AuditLog(
            actor_id=actor_id,
            action_type=action_type,
            description=description,
            resource_id=resource_id,
            audit_metadata=metadata,
            ledger_hash=current_hash
        )

        self.db.add(log_record)
        await self.db.commit()
        await self.db.refresh(log_record)
        return log_record
