import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.governance import CopilotSession, CopilotMessage

class CopilotRepository:
    """
    Handles database operations for CopilotSession and CopilotMessage logs.
    """
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_session(self, title: str) -> CopilotSession:
        """Instantiates a new chat session thread context."""
        session = CopilotSession(
            title=title,
            created_at=datetime.utcnow()
        )
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def list_sessions(self, limit: int = 30) -> List[CopilotSession]:
        """Lists chat sessions order by creation time."""
        result = await self.db.execute(
            select(CopilotSession)
            .options(selectinload(CopilotSession.messages))
            .order_by(CopilotSession.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_session(self, session_id: uuid.UUID) -> Optional[CopilotSession]:
        """Retrieves a single session thread containing full nested messages lists."""
        result = await self.db.execute(
            select(CopilotSession)
            .where(CopilotSession.id == session_id)
            .options(selectinload(CopilotSession.messages))
        )
        return result.scalars().first()

    async def add_message(
        self,
        session_id: uuid.UUID,
        role: str,
        content: str,
        sources: Optional[Dict[str, Any]] = None,
        report_html: Optional[str] = None
    ) -> CopilotMessage:
        """Appends a new query or answer bubble in a session context."""
        msg = CopilotMessage(
            session_id=session_id,
            role=role,
            content=content,
            sources=sources,
            report_html=report_html,
            created_at=datetime.utcnow()
        )
        self.db.add(msg)
        await self.db.commit()
        await self.db.refresh(msg)
        return msg

    async def get_message(self, message_id: uuid.UUID) -> Optional[CopilotMessage]:
        """Retrieves a single chat message detail."""
        return await self.db.get(CopilotMessage, message_id)
