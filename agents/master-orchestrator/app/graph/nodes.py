"""
Cac node cua LangGraph state machine (dung ten nhu README.md mo ta):
receive_input -> classify_intent -> route_to_agent -> wait_response -> reply_user.

Cap nhat Ngay 2: wait_response cho nhanh safety_tutoring gio CHO ACK THAT tren
lab/safety/command (khop "in_reply_to", timeout 3s theo
docs-thiet-ke/Thiet-ke-Event-Bus-MQTT-Topic-Schema.md), thay cho placeholder truoc day.

Con TODO: lab_data/power_load VAN con la fire-and-forget (chua co co che cho ket qua that -
schema co dinh nghia "in_reply_to" cho lab/data/result nhung chua duoc yeu cau lam trong Ngay 2
nay). Tham so cu the hon cua tung lenh (vd loai hanh dong chi tiet cho lab_data) cung chua duoc
tach tu cau noi that ngoai table_id/action.
"""
from pydantic import ValidationError

from app.graph.state import OrchestratorState
from app.intent.classifier import classify
from app.models.schemas import (
    DataQuery,
    IntentMessage,
    PowerCommand,
    SafetyCommandAck,
    SafetyCommandRequest,
)
from app.mqtt.client import get_client
from app.mqtt.topics import TOPIC_DATA_QUERY, TOPIC_ORCHESTRATOR_INTENT, TOPIC_POWER_COMMAND, TOPIC_SAFETY_COMMAND

SOURCE_AGENT = "master-orchestrator"
SAFETY_COMMAND_TIMEOUT_SECONDS = 3.0

# Anh xa tu "action" chung (dung trong IntentMessage broadcast) sang "requested_action" cu the
# cho PLC (dung trong SafetyCommandRequest) - dung dung vi du trong file schema.
_ACTION_TO_REQUESTED_ACTION = {
    "power_on": "close_contactor",
}


def receive_input(state: OrchestratorState) -> dict:
    return {"raw_input": state["raw_input"].strip()}


def classify_intent(state: OrchestratorState) -> dict:
    result = classify(state["raw_input"])
    return {
        "intent": result.intent,
        "target_agent": result.target_agent,
        "table_id": result.table_id,
        "action": result.action,
    }


def route_to_agent(state: OrchestratorState) -> dict:
    target = state.get("target_agent")
    if target is None:
        return {}

    client = get_client()

    if target == "safety_tutoring":
        # 1. Broadcast y dinh chung tren topic chung (Safety/LabData/Power deu subscribe).
        client.publish(
            TOPIC_ORCHESTRATOR_INTENT,
            IntentMessage(
                source_agent=SOURCE_AGENT,
                intent=state["intent"],
                user=state["user"],
                table_id=state.get("table_id"),
                action=state.get("action"),
            ),
        )

        # 2. Gui YEU CAU cu the len lab/safety/command, nho lai message_id de wait_response
        # doi chieu ACK.
        requested_action = _ACTION_TO_REQUESTED_ACTION.get(state.get("action"), "close_contactor")
        request = SafetyCommandRequest(
            source_agent=SOURCE_AGENT,
            table_id=state.get("table_id") or "UNKNOWN",
            requested_action=requested_action,
        )
        client.publish(TOPIC_SAFETY_COMMAND, request)
        return {"safety_request_message_id": request.message_id}

    elif target == "lab_data":
        client.publish(
            TOPIC_DATA_QUERY,
            DataQuery(source_agent=SOURCE_AGENT, query=state["intent"]),
        )
    elif target == "power_load":
        client.publish(
            TOPIC_POWER_COMMAND,
            PowerCommand(
                source_agent=SOURCE_AGENT,
                action=state.get("action") or "turn_off",
                table_id=state.get("table_id") or "UNKNOWN",
            ),
        )

    return {}


def wait_response(state: OrchestratorState) -> dict:
    if state.get("target_agent") == "safety_tutoring" and state.get("safety_request_message_id"):
        client = get_client()
        raw = client.wait_for_ack(state["safety_request_message_id"], timeout=SAFETY_COMMAND_TIMEOUT_SECONDS)
        if raw is None:
            return {"agent_response": {"timed_out": True}}
        try:
            ack = SafetyCommandAck(**raw)
        except ValidationError:
            return {"agent_response": {"timed_out": False, "invalid": True}}
        return {"agent_response": ack.model_dump()}

    # lab_data / power_load: TODO - chua co co che cho ket qua that, van la placeholder.
    return {"agent_response": None}


def reply_user(state: OrchestratorState) -> dict:
    if state.get("target_agent") is None:
        return {
            "reply_text": "Xin loi, toi chua nhan dien duoc yeu cau nay. Ban co the noi ro hon khong?"
        }

    if state.get("target_agent") == "safety_tutoring":
        response = state.get("agent_response") or {}
        table_id = state.get("table_id") or "?"

        if response.get("timed_out"):
            return {
                "reply_text": (
                    f"Khong nhan duoc phan hoi tu Safety Agent cho ban {table_id} trong "
                    f"{SAFETY_COMMAND_TIMEOUT_SECONDS:.0f} giay - vui long kiem tra lai he thong "
                    "an toan truoc khi thu lai."
                )
            }
        if response.get("invalid"):
            return {"reply_text": "Nhan duoc phan hoi khong hop le tu Safety Agent, vui long thu lai."}
        if response.get("approved"):
            return {"reply_text": f"Da cap nguon cho ban {response.get('table_id', table_id)}. Ban co the bat dau thuc hanh."}
        return {
            "reply_text": (
                f"Khong the cap nguon cho ban {response.get('table_id', table_id)}: "
                f"{response.get('reason') or 'dieu kien an toan chua dat'}."
            )
        }

    return {
        "reply_text": (
            f"Da chuyen yeu cau '{state['raw_input']}' toi {state['target_agent']}. "
            "Dang cho phan hoi (skeleton - logic cho phan hoi that cho lab_data/power_load "
            "se hoan thien sau)."
        )
    }
