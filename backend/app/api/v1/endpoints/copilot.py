import uuid
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_permission
from app.schemas.copilot import CopilotQueryRequest, CopilotMessageResponse, CopilotSessionCreate, CopilotSessionResponse
from app.repositories.copilot import CopilotRepository
from app.services.copilot import RegulatoryCopilotService
from app.models.users import User

router: APIRouter = APIRouter(prefix="/copilot", tags=["Regulatory Copilot"])

@router.post("/sessions", response_model=CopilotSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_chat_session(
    payload: CopilotSessionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("read:transactions"))
) -> CopilotSessionResponse:
    """
    Instantiates a new Regulatory Copilot session chat thread.
    Requires 'read:transactions' permission.
    """
    repo = CopilotRepository(db)
    session = await repo.create_session(payload.title)

    return CopilotSessionResponse(
        id=session.id,
        title=session.title,
        created_at=session.created_at,
        messages=[]
    )

@router.get("/sessions", response_model=List[CopilotSessionResponse])
async def list_chat_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("read:transactions"))
) -> List[CopilotSessionResponse]:
    """
    Lists past chat session threads.
    Requires 'read:transactions' permission.
    """
    repo = CopilotRepository(db)
    sessions = await repo.list_sessions()

    response = []
    for s in sessions:
        msgs = []
        for m in s.messages:
            msgs.append(CopilotMessageResponse(
                id=m.id,
                session_id=m.session_id,
                role=m.role,
                content=m.content,
                sources=m.sources,
                report_html=m.report_html,
                created_at=m.created_at
            ))

        response.append(CopilotSessionResponse(
            id=s.id,
            title=s.title,
            created_at=s.created_at,
            messages=msgs
        ))
    return response

@router.post("/sessions/{session_id}/query", response_model=CopilotMessageResponse)
async def query_regulatory_copilot(
    session_id: uuid.UUID,
    payload: CopilotQueryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("read:transactions"))
) -> CopilotMessageResponse:
    """
    Submits user prompt query to the Copilot session thread, triggers RAG context search,
    calculates answer, and registers in DB.
    Requires 'read:transactions' permission.
    """
    repo = CopilotRepository(db)
    session = await repo.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session thread not found."
        )

    service = RegulatoryCopilotService(db)
    msg = await service.query_copilot(session_id, payload.query)

    return CopilotMessageResponse(
        id=msg.id,
        session_id=msg.session_id,
        role=msg.role,
        content=msg.content,
        sources=msg.sources,
        report_html=msg.report_html,
        created_at=msg.created_at
    )

@router.get("/messages/{message_id}/download-report")
async def download_printable_report(
    message_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("read:transactions"))
) -> Response:
    """
    Exports printable PDF-ready HTML report document.
    Requires 'read:transactions' permission.
    """
    repo = CopilotRepository(db)
    msg = await repo.get_message(message_id)
    if not msg or not msg.report_html:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compliance report template not found for this message."
        )

    # Return HTML document as attachment file download
    headers = {
        "Content-Disposition": f'attachment; filename="AegisAI_Regulatory_Report_{msg.id.hex[:8].upper()}.html"'
    }
    return Response(content=msg.report_html, media_type="text/html", headers=headers)
