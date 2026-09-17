"""
Router FastAPI cho kenh Chat (uu tien lam truoc theo README.md - Voice se them o Tuan 12
qua app/api/voice.py rieng, chua tao trong skeleton nay).

Ngay 2: graph.invoke() gio co the block toi 3 giay that (wait_response cho ACK Safety Agent)
- chay trong thread pool qua asyncio.to_thread() de khong lam nghen event loop cua FastAPI khi
co nhieu request Chat cung luc.
"""
import asyncio

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
    initial_state = {
        "raw_input": request.message,
        "input_channel": "chat",
        "user": request.user,
        "intent": None,
        "target_agent": None,
        "table_id": None,
        "action": None,
        "safety_request_message_id": None,
        "agent_response": None,
        "reply_text": None,
    }
    result = await asyncio.to_thread(_graph.invoke, initial_state)
    return ChatResponse(reply=result["reply_text"])
