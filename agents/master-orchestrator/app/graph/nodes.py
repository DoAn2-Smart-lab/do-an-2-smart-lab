"""
Cac node cua LangGraph state machine (dung ten nhu README.md mo ta):
receive_input -> classify_intent -> route_to_agent -> wait_response -> reply_user.

SKELETON: wait_response CHUA thuc su cho phan hoi qua MQTT tu sub-agent (se lam khi tich hop
that o Tuan 3-4, can them co che timeout + lang nghe topic ket qua tuong ung). Tham so cu the
cua tung lenh (ten ban thuc hanh, zone, action bat/tat...) cung chua duoc tach tu cau noi that
- classify() moi chi tra ve intent chung chung, du de route_to_agent chon dung topic.
"""
from app.graph.state import OrchestratorState
from app.intent.classifier import classify
from app.models.schemas import DataQuery, IntentMessage, PowerCommand
from app.mqtt.client import get_client
from app.mqtt.topics import TOPIC_DATA_QUERY, TOPIC_ORCHESTRATOR_INTENT, TOPIC_POWER_COMMAND

SOURCE_AGENT = "master-orchestrator"


def receive_input(state: OrchestratorState) -> dict:
    return {"raw_input": state["raw_input"].strip()}


def classify_intent(state: OrchestratorState) -> dict:
    result = classify(state["raw_input"])
    return {"intent": result.intent, "target_agent": result.target_agent}


def route_to_agent(state: OrchestratorState) -> dict:
    target = state.get("target_agent")
    if target is None:
        return {}

    client = get_client()

    if target == "safety_tutoring":
        # Theo schema: lab/orchestrator/intent la topic broadcast, ca 3 sub-agent deu
        # subscribe - Safety Agent tu loc lay ban tin lien quan bang field "intent".
        client.publish(
            TOPIC_ORCHESTRATOR_INTENT,
            IntentMessage(source_agent=SOURCE_AGENT, intent=state["intent"], user=state["user"]),
        )
    elif target == "lab_data":
        client.publish(
            TOPIC_DATA_QUERY,
            DataQuery(source_agent=SOURCE_AGENT, query=state["intent"]),
        )
    elif target == "power_load":
        # TODO (Tuan 3-4): suy ra dung "action"/"zone" tu cau lenh that thay vi gia tri mac dinh.
        client.publish(
            TOPIC_POWER_COMMAND,
            PowerCommand(source_agent=SOURCE_AGENT, action="turn_on", zone="default"),
        )

    return {}


def wait_response(state: OrchestratorState) -> dict:
    # TODO (Tuan 3-4): cho phan hoi that qua lab/safety/status|alert, lab/data/result,
    # lab/power/status (co timeout), roi gan vao agent_response.
    return {"agent_response": None}


def reply_user(state: OrchestratorState) -> dict:
    if state.get("target_agent") is None:
        return {
            "reply_text": "Xin loi, toi chua nhan dien duoc yeu cau nay. Ban co the noi ro hon khong?"
        }
    return {
        "reply_text": (
            f"Da chuyen yeu cau '{state['raw_input']}' toi {state['target_agent']}. "
            "Dang cho phan hoi (skeleton - logic cho phan hoi that se hoan thien o Tuan 3-4)."
        )
    }
