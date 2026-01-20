from fastapi import APIRouter
from uuid import uuid4

from app.api.models import ChatRequest, ChatResponse
from app.orchestrator import ConversationOrchestrator

router = APIRouter()
orchestrator = ConversationOrchestrator()

@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    session_id = req.session_id or uuid4().hex
    print(f"Received message for session: {session_id}")
    try:
        reply = orchestrator.handle(session_id, req.message)
    except Exception as e:
        reply=(
            "Sorry, something went wrong while processing your request. ",
            "Could you please try again later?"
        )
    
    return ChatResponse(
        session_id=session_id,
        reply=reply
    )
