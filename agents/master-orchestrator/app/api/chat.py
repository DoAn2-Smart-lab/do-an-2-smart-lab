"""
Router FastAPI cho kenh Chat (uu tien lam truoc theo README.md - Voice se them o Tuan 12
qua app/api/voice.py rieng, chua tao trong skeleton nay).
"""
from fastapi import APIRouter
from pydantic import BaseModel

from app.graph.builder import build_graph

router = APIRouter()
_graph = build_graph()


class ChatRequest(BaseModel):
    user: str
    message: str


class ChatResponse(BaseModel):
    reply: str


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    result = _graph.invoke(
        {
            "raw_input": request.message,
            "input_channel": "chat",
            "user": request.user,
            "intent": None,
            "target_agent": None,
            "agent_response": None,
            "reply_text": None,
        }
    )
    return ChatResponse(reply=result["reply_text"])
