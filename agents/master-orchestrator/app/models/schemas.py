"""
Pydantic model cho payload MQTT.

Cac field PHAI khop voi cot "Payload mau" trong
docs-thiet-ke/Thiet-ke-Event-Bus-MQTT-Topic-Schema.md. File .md do ghi ro day la ban nhap
Tuan 2, "can chot" JSON Schema chinh thuc — neu Lab Data/Power Agent doi field, sua file .md
truoc roi moi sua lai o day, khong tu y doi field mot phia.
"""
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class MqttEnvelope(BaseModel):
    """Truong bat buoc cho MOI payload, theo muc 'Nguyen tac' cua file schema:
    luon co timestamp (ISO 8601) va source_agent."""

    source_agent: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ---- lab/orchestrator/intent (publish) ----
class IntentMessage(MqttEnvelope):
    intent: str
    user: str


# ---- lab/safety/status (subscribe) ----
class SafetyStatus(MqttEnvelope):
    e_stop_ok: bool
    thermal_relay_ok: bool
    short_circuit_ok: bool


# ---- lab/safety/alert (subscribe) ----
class SafetyAlert(MqttEnvelope):
    fault_type: str
    value: float
    table_id: str


# ---- lab/data/query (publish) ----
class DataQuery(MqttEnvelope):
    query: str
    device_id: Optional[str] = None


# ---- lab/data/result (subscribe) ----
class DataResult(MqttEnvelope):
    device_id: str
    spec: dict


# ---- lab/power/status (subscribe) ----
class PowerStatus(MqttEnvelope):
    total_kw: float
    peak_forecast_kw: float
    lights: Literal["on", "off"]
    fans: Literal["on", "off"]


# ---- lab/power/command (publish) ----
class PowerCommand(MqttEnvelope):
    action: Literal["turn_on", "turn_off"]
    zone: str
