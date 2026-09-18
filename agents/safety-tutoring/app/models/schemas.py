"""
Pydantic model cho payload MQTT cua Safety & Practical Tutoring Agent.

Cac field PHAI khop voi cot "Payload mau" trong
docs-thiet-ke/Thiet-ke-Event-Bus-MQTT-Topic-Schema.md (ban chot Ngay 2), chi lay dung 3 topic
lien quan Safety Agent (lab/safety/status, lab/safety/command, lab/safety/alert). Neu Master
Orchestrator/Lab Data/Power Agent doi field, sua file .md truoc roi moi sua lai o day, khong tu y
doi field mot phia.
"""
import uuid
from datetime import datetime, timedelta, timezone
from typing import Literal, Optional

from pydantic import BaseModel, Field

# Gio Viet Nam co dinh UTC+7 (khong co DST) - dung cho field "timestamp" theo dung vi du trong
# file schema (vd "2026-09-17T10:00:00+07:00").
VN_TZ = timezone(timedelta(hours=7))


def _now_vn() -> datetime:
    return datetime.now(VN_TZ)


class MqttEnvelope(BaseModel):
    """Truong bat buoc cho MOI payload, theo muc 'Nguyen tac' cua file schema:
    luon co message_id (UUID v4), timestamp (ISO 8601 +07:00), source_agent."""

    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=_now_vn)
    source_agent: str


# ---- lab/safety/status (publish) ----
class SafetyStatusMessage(MqttEnvelope):
    table_id: str
    e_stop_ok: bool
    thermal_relay_ok: bool
    short_circuit_ok: bool
    contactor_state: Literal["open", "closed"]
    current_A: float
    temperature_C: float


# ---- lab/safety/command: yeu cau tu Master Orchestrator (subscribe) ----
class SafetyCommandRequest(MqttEnvelope):
    type: Literal["request"] = "request"
    table_id: str
    requested_action: str


# ---- lab/safety/command: ACK/NACK cua Safety Agent (publish) ----
class SafetyCommandAck(MqttEnvelope):
    type: Literal["ack"] = "ack"
    in_reply_to: str
    table_id: str
    approved: bool
    action: str
    reason: Optional[str] = None


# ---- lab/safety/alert (publish) ----
class SafetyAlertMessage(MqttEnvelope):
    table_id: str
    fault_type: Literal["conveyor_jam", "overcurrent", "overtemperature"]
    value: float
    threshold: float
    severity: str
    action_taken: str
