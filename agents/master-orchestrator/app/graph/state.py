"""
State schema cho LangGraph, dung dung 5 buoc mo ta trong agents/master-orchestrator/README.md:
receive_input -> classify_intent -> route_to_agent -> wait_response -> reply_user.
"""
from typing import Literal, Optional, TypedDict


class OrchestratorState(TypedDict):
    raw_input: str
    input_channel: Literal["chat", "voice"]
    user: str
    intent: Optional[str]
    target_agent: Optional[Literal["safety_tutoring", "lab_data", "power_load"]]
    agent_response: Optional[dict]
    reply_text: Optional[str]
