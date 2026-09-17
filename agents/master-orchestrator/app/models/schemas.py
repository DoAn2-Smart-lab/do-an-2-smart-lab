"""
Pydantic model cho payload MQTT.

Cac field PHAI khop voi cot "Payload mau" trong
docs-thiet-ke/Thiet-ke-Event-Bus-MQTT-Topic-Schema.md (ban chot Ngay 2). Neu Lab Data/Power
Agent doi field, sua file .md truoc roi moi sua lai o day, khong tu y doi field mot phia.
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


# ---- lab/orchestrator/intent (publish) ----
class IntentMessage(MqttEnvelope):
    intent: str
    user: str
    table_id: Optional[str] = None
    action: Optional[str] = None
    confidence: float = 0.9


# ---- lab/safety/status (subscribe) ----
class SafetyStatus(MqttEnvelope):
    table_id: str
    e_stop_ok: bool
    thermal_relay_ok: bool
    short_circuit_ok: bool
    contactor_state: Literal["open", "closed"]
    current_A: float
    temperature_C: float


# ---- lab/safety/command: yeu cau tu Orchestrator (publish) ----
class SafetyCommandRequest(MqttEnvelope):
    type: Literal["request"] = "request"
    table_id: str
    requested_action: str


# ---- lab/safety/command: ACK/NACK tu Safety Agent (subscribe) ----
class SafetyCommandAck(MqttEnvelope):
    type: Literal["ack"] = "ack"
    in_reply_to: str
    table_id: str
    approved: bool
    action: str
    reason: Optional[str] = None


# ---- lab/safety/alert (subscribe) ----
class SafetyAlert(MqttEnvelope):
    table_id: str
    fault_type: Literal["conveyor_jam", "overcurrent", "overtemperature"]
    value: float
    threshold: float
    severity: str
    action_taken: str


# ---- lab/data/query (publish) ----
class DataQuery(MqttEnvelope):
    query: str
    device_id: Optional[str] = None
    filters: dict = Field(default_factory=dict)


# ---- lab/data/result (subscribe) ----
class DataResult(MqttEnvelope):
    in_reply_to: str
    device_id: str
    status: Literal["ok", "not_found", "error"]
    spec: dict = Field(default_factory=dict)


# ---- lab/power/status (subscribe) ----
class PowerStatus(MqttEnvelope):
    total_kw: float
    peak_forecast_kw: float
    forecast_horizon_min: int
    lights: Literal["on", "off"]
    fans: Literal["on", "off"]


# ---- lab/power/command (publish) ----
class PowerCommand(MqttEnvelope):
    action: str
    table_id: str
    reason: Optional[str] = None
