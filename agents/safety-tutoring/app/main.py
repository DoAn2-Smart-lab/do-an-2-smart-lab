"""
Entrypoint Safety & Practical Tutoring Agent.

Chay (tu thu muc agents/safety-tutoring/, sau khi da pip install -r requirements.txt o thu muc
goc du an):
    uvicorn app.main:app --reload

Nhiem vu (xem docs-thiet-ke/Thiet-ke-Event-Bus-MQTT-Topic-Schema.md):
- Publish lab/safety/status dinh ky (doc qua SafetyPlcClient).
- Subscribe lab/safety/command, kiem tra interlock (e_stop_ok AND thermal_relay_ok AND
  short_circuit_ok) truoc khi dong contactor, roi publish ACK/NACK.
- Publish lab/safety/alert khi current_A/temperature_C vuot nguong (ke thua dung nguong Do an 1).
- La noi DUY NHAT duoc phep publish lenh dong/cat contactor xuong PLC.
"""
import logging
import os
import threading
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import ValidationError

from app.models.schemas import SafetyAlertMessage, SafetyCommandAck, SafetyCommandRequest, SafetyStatusMessage
from app.mqtt.client import SafetyAgentMqttClient, get_client, init_client
from app.mqtt.topics import SUBSCRIBE_TOPICS, TOPIC_SAFETY_ALERT, TOPIC_SAFETY_COMMAND, TOPIC_SAFETY_STATUS
from app.plc.snap7_client import SafetyPlcClient, get_plc_client, init_plc_client, is_plc_client_initialized

load_dotenv()

logger = logging.getLogger(__name__)

SOURCE_AGENT = "safety-agent"

# Nguong dung DUNG theo Do an 1 (scl/DB_ConveyorMonitor.scl + python-bridge/main_bridge.py):
# qua dong > 10.3A, qua nhiet > 80.5 do C (Do an 1 goc dung 10.0A/80.0 do C lam nguong hien thi
# trong thong bao Telegram, nhung file schema Do an 2 da chot ro 10.3A/80.5 do C - dung dung so
# nay, KHONG dung lai 10.0/80.0 cua Do an 1).
OVERCURRENT_THRESHOLD_A = 10.3
OVERTEMPERATURE_THRESHOLD_C = 80.5

MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "localhost")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", "1883"))

SAFETY_TABLE_ID = os.getenv("SAFETY_TABLE_ID", "B03")
PLC_IP = os.getenv("PLC_IP", "192.168.0.1")
PLC_RACK = int(os.getenv("PLC_RACK", "0"))
PLC_SLOT = int(os.getenv("PLC_SLOT", "1"))
PLC_DB_NUMBER = int(os.getenv("PLC_DB_NUMBER", "2"))
STATUS_INTERVAL_SECONDS = float(os.getenv("SAFETY_STATUS_INTERVAL_SECONDS", "3.0"))

app = FastAPI(title="Safety & Practical Tutoring Agent")


def check_interlock(status: dict) -> tuple[bool, Optional[str]]:
    """3 dieu kien an toan PHAI dung TAT CA true moi duoc dong contactor (xem yeu cau Ngay 2:
    interlock_ok = e_stop_ok AND thermal_relay_ok AND short_circuit_ok). Tra ve (ok, reason) -
    reason la dieu kien DAU TIEN khong dat, dung dung ten field + hau to "_not_ok" nhu vi du
    trong file schema (vd "e_stop_not_ok")."""
    if not status["e_stop_ok"]:
        return False, "e_stop_not_ok"
    if not status["thermal_relay_ok"]:
        return False, "thermal_relay_not_ok"
    if not status["short_circuit_ok"]:
        return False, "short_circuit_not_ok"
    return True, None


def handle_command_request(
    plc_client: SafetyPlcClient,
    mqtt_client: SafetyAgentMqttClient,
    table_id: str,
    request: SafetyCommandRequest,
) -> Optional[SafetyCommandAck]:
    """Xu ly 1 yeu cau tren lab/safety/command, publish ACK/NACK tuong ung, tra ve ACK da publish
    (None neu yeu cau khong danh cho ban nay - de nhieu Safety Agent instance cung subscribe
    chung topic ma khong dam vao nhau)."""
    if request.table_id != table_id:
        return None

    if request.requested_action == "open_contactor":
        # Cat dien la thao tac AN TOAN, khong can kiem interlock - luon duoc phep.
        plc_client.open_contactor(request.table_id)
        ack = SafetyCommandAck(
            source_agent=SOURCE_AGENT,
            in_reply_to=request.message_id,
            table_id=request.table_id,
            approved=True,
            action="open_contactor",
        )
    elif request.requested_action == "close_contactor":
        status = plc_client.read_safety_status()
        ok, reason = check_interlock(status)
        if ok:
            plc_client.close_contactor(request.table_id)
        ack = SafetyCommandAck(
            source_agent=SOURCE_AGENT,
            in_reply_to=request.message_id,
            table_id=request.table_id,
            approved=ok,
            action="close_contactor",
            reason=reason,
        )
    else:
        ack = SafetyCommandAck(
            source_agent=SOURCE_AGENT,
            in_reply_to=request.message_id,
            table_id=request.table_id,
            approved=False,
            action=request.requested_action,
            reason="unknown_action",
        )

    mqtt_client.publish(TOPIC_SAFETY_COMMAND, ack)
    return ack


class SafetyMonitor:
    """Vong doc trang thai dinh ky: publish lab/safety/status moi lan goi run_cycle(), va publish
    lab/safety/alert CHI luc vua CHUYEN sang vuot nguong (rising-edge, dung dung trieu ly cua
    Do an 1 trong main_bridge.py - khong spam alert moi lan van con vuot nguong)."""

    def __init__(self, plc_client: SafetyPlcClient, mqtt_client: SafetyAgentMqttClient, table_id: str):
        self._plc = plc_client
        self._mqtt = mqtt_client
        self._table_id = table_id
        self._overcurrent_active = False
        self._overtemperature_active = False

    def run_cycle(self) -> SafetyStatusMessage:
        status = self._plc.read_safety_status()
        status_msg = SafetyStatusMessage(source_agent=SOURCE_AGENT, **status)
        self._mqtt.publish(TOPIC_SAFETY_STATUS, status_msg)

        self._overcurrent_active = self._check_alert(
            was_active=self._overcurrent_active,
            is_active=status["current_A"] > OVERCURRENT_THRESHOLD_A,
            fault_type="overcurrent",
            value=status["current_A"],
            threshold=OVERCURRENT_THRESHOLD_A,
        )
        self._overtemperature_active = self._check_alert(
            was_active=self._overtemperature_active,
            is_active=status["temperature_C"] > OVERTEMPERATURE_THRESHOLD_C,
            fault_type="overtemperature",
            value=status["temperature_C"],
            threshold=OVERTEMPERATURE_THRESHOLD_C,
        )
        return status_msg

    def _check_alert(self, was_active: bool, is_active: bool, fault_type: str, value: float, threshold: float) -> bool:
        if is_active and not was_active:
            logger.warning(
                "PHAT HIEN %s tren ban %s: %.2f (nguong %.2f) - dang cat contactor + publish alert",
                fault_type, self._table_id, value, threshold,
            )
            self._plc.open_contactor(self._table_id)
            alert = SafetyAlertMessage(
                source_agent=SOURCE_AGENT,
                table_id=self._table_id,
                fault_type=fault_type,
                value=value,
                threshold=threshold,
                severity="critical",
                action_taken="contactor_opened",
            )
            self._mqtt.publish(TOPIC_SAFETY_ALERT, alert)
        return is_active


_monitor: Optional[SafetyMonitor] = None
_stop_event: Optional[threading.Event] = None
_monitor_thread: Optional[threading.Thread] = None


def get_monitor() -> SafetyMonitor:
    if _monitor is None:
        raise RuntimeError("SafetyMonitor chua duoc khoi tao - server chua startup xong")
    return _monitor


def _make_command_handler(table_id: str):
    def _on_command(payload: dict) -> None:
        # Topic lab/safety/command la 2 chieu - bo qua chinh message "type": "ack" cua minh
        # vong lai (Safety Agent chi xu ly "type": "request").
        if payload.get("type") != "request":
            return
        try:
            request = SafetyCommandRequest(**payload)
        except ValidationError:
            logger.warning("Payload lab/safety/command khong hop le: %s", payload)
            return
        handle_command_request(get_plc_client(), get_client(), table_id, request)

    return _on_command


def _status_loop(monitor: SafetyMonitor, interval: float, stop_event: threading.Event) -> None:
    while not stop_event.wait(interval):
        try:
            monitor.run_cycle()
        except Exception:
            logger.exception("Loi trong vong lap doc trang thai an toan")


@app.on_event("startup")
def startup() -> None:
    global _monitor, _stop_event, _monitor_thread

    # Chi tu khoi tao PLC client that neu chua co ai inject truoc (vd test da goi
    # init_plc_client() voi fake truoc khi tao TestClient) - xem tests/test_safety_agent.py.
    if not is_plc_client_initialized():
        init_plc_client(
            table_id=SAFETY_TABLE_ID, plc_ip=PLC_IP, rack=PLC_RACK, slot=PLC_SLOT, db_number=PLC_DB_NUMBER
        )
    plc_client = get_plc_client()
    plc_client.connect()

    mqtt_client = init_client(host=MQTT_BROKER_HOST, port=MQTT_BROKER_PORT)
    mqtt_client.connect()
    for topic in SUBSCRIBE_TOPICS:
        mqtt_client.subscribe(topic, handler=_make_command_handler(plc_client.table_id))

    _monitor = SafetyMonitor(plc_client, mqtt_client, plc_client.table_id)
    _stop_event = threading.Event()
    _monitor_thread = threading.Thread(
        target=_status_loop, args=(_monitor, STATUS_INTERVAL_SECONDS, _stop_event), daemon=True
    )
    _monitor_thread.start()


@app.on_event("shutdown")
def shutdown() -> None:
    if _stop_event is not None:
        _stop_event.set()
    if _monitor_thread is not None:
        _monitor_thread.join(timeout=2)
    get_plc_client().disconnect()
    get_client().disconnect()
