"""
Test luong that cua Safety & Practical Tutoring Agent - dung Mosquitto that dang chay san
(localhost:1883, KHONG mock MQTT), chi mock/fake phan PLC (chua co PLCSIM Advanced, dang cho
license - xem app/plc/snap7_client.py). Bao phu 2 nghiem thu chinh cua Ngay 2:
  1. Luong MQTT request (lab/safety/command) -> kiem interlock -> ACK/NACK.
  2. Luong phat lab/safety/alert khi current_A/temperature_C vuot nguong.

Chay: pytest tests/test_safety_agent.py (tu thu muc agents/safety-tutoring/, can Mosquitto dang
chay o localhost:1883).
"""
import json
import os
import threading
import time
import uuid

# QUAN TRONG: dat interval RAT DAI truoc khi import app.main lan dau - cac hang so cua module do
# (SAFETY_TABLE_ID, STATUS_INTERVAL_SECONDS...) duoc doc tu env NGAY LUC IMPORT. Dat dai de thread
# nen (_status_loop) khong tu chay xen vao trong luc test dang chu dong goi run_cycle(), tranh
# publish trung/flaky.
os.environ.setdefault("SAFETY_STATUS_INTERVAL_SECONDS", "999")
os.environ.setdefault("SAFETY_TABLE_ID", "B03")

import paho.mqtt.client as mqtt
import pytest
import snap7.util
from fastapi.testclient import TestClient

from app.main import app, get_monitor
from app.models.schemas import SafetyCommandAck, SafetyCommandRequest
from app.mqtt.topics import TOPIC_SAFETY_ALERT, TOPIC_SAFETY_COMMAND
from app.plc.snap7_client import (
    BIT_CONTACTOR_CMD,
    BIT_CONTACTOR_STATE,
    BIT_E_STOP_OK,
    BIT_SHORT_CIRCUIT_OK,
    BIT_THERMAL_RELAY_OK,
    OFFSET_MOTOR_CURRENT,
    OFFSET_MOTOR_TEMPERATURE,
    OFFSET_SAFETY_FLAGS,
    init_plc_client,
)

TABLE_ID = "B03"
MQTT_HOST = os.getenv("MQTT_BROKER_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_BROKER_PORT", "1883"))


class FakeSnap7Client:
    """Thay the snap7.client.Client that bang bo nho gia lap trong tien trinh - dung LAI dung
    cac ham get_bool/set_bool/get_real/set_real cua snap7.util tren cung offset that su Safety
    Agent doc/ghi, nen fake nay mo phong dung hanh vi byte-level cua PLC that (khong phai canned
    dict). Rieng bit CONTACTOR_CMD: khi Safety Agent ghi bit nay, fake tu cap nhat luon bit
    CONTACTOR_STATE tuong ung de mo phong PLC dong tiep diem ngay lap tuc (phan ladder logic that
    chua co vi .scl chua duoc bo sung tag nay - xem docstring app/plc/snap7_client.py)."""

    def __init__(self, db_size: int = 32):
        self._dbs: dict[int, bytearray] = {}
        self._db_size = db_size
        self._connected = False

    def _buf(self, db_number: int) -> bytearray:
        return self._dbs.setdefault(db_number, bytearray(self._db_size))

    def connect(self, address: str, rack: int, slot: int) -> None:
        self._connected = True

    def disconnect(self) -> None:
        self._connected = False

    def get_connected(self) -> bool:
        return self._connected

    def db_read_bool(self, db_number: int, byte_offset: int, bit_offset: int) -> bool:
        return snap7.util.get_bool(self._buf(db_number), byte_offset, bit_offset)

    def db_write_bool(self, db_number: int, byte_offset: int, bit_offset: int, value: bool) -> None:
        buf = self._buf(db_number)
        snap7.util.set_bool(buf, byte_offset, bit_offset, value)
        if byte_offset == OFFSET_SAFETY_FLAGS and bit_offset == BIT_CONTACTOR_CMD:
            snap7.util.set_bool(buf, OFFSET_SAFETY_FLAGS, BIT_CONTACTOR_STATE, value)

    def db_read_real(self, db_number: int, offset: int) -> float:
        return snap7.util.get_real(self._buf(db_number), offset)

    def db_write_real(self, db_number: int, offset: int, value: float) -> None:
        snap7.util.set_real(self._buf(db_number), offset, value)

    # ---- tien ich rieng cho test, khong phai mot phan cua Snap7ClientProtocol ----
    def seed_safe_state(self, current_A: float = 4.2, temperature_C: float = 45.0) -> None:
        self.db_write_bool(2, OFFSET_SAFETY_FLAGS, BIT_E_STOP_OK, True)
        self.db_write_bool(2, OFFSET_SAFETY_FLAGS, BIT_THERMAL_RELAY_OK, True)
        self.db_write_bool(2, OFFSET_SAFETY_FLAGS, BIT_SHORT_CIRCUIT_OK, True)
        self.db_write_real(2, OFFSET_MOTOR_CURRENT, current_A)
        self.db_write_real(2, OFFSET_MOTOR_TEMPERATURE, temperature_C)


class MqttWaiter:
    """Test harness MQTT client rieng (khong phai client cua Safety Agent) - dung de publish
    request va cho ACK/alert that qua Mosquitto dang chay san."""

    def __init__(self):
        self._client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"test-harness-{uuid.uuid4().hex[:8]}")
        self._client.on_message = self._on_message
        self._messages: list[dict] = []
        self._lock = threading.Lock()
        self._event = threading.Event()
        self._client.connect(MQTT_HOST, MQTT_PORT)
        self._client.loop_start()

    def _on_message(self, client, userdata, msg):
        with self._lock:
            self._messages.append(json.loads(msg.payload.decode("utf-8")))
        self._event.set()

    def subscribe(self, topic: str, qos: int = 1) -> None:
        self._client.subscribe(topic, qos=qos)

    def publish(self, topic: str, payload_json: str, qos: int = 1) -> None:
        self._client.publish(topic, payload_json, qos=qos)

    def wait_for(self, predicate, timeout: float = 5.0) -> dict:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            with self._lock:
                for message in self._messages:
                    if predicate(message):
                        return message
            self._event.wait(max(0.0, deadline - time.monotonic()))
            self._event.clear()
        raise TimeoutError(f"Khong nhan duoc message phu hop trong {timeout}s")

    def close(self) -> None:
        self._client.loop_stop()
        self._client.disconnect()


@pytest.fixture()
def fake_plc() -> FakeSnap7Client:
    fake = FakeSnap7Client()
    fake.seed_safe_state()
    return fake


@pytest.fixture()
def waiter():
    harness = MqttWaiter()
    yield harness
    harness.close()


def test_close_contactor_approved_when_interlock_ok(fake_plc, waiter):
    init_plc_client(table_id=TABLE_ID, client=fake_plc)
    waiter.subscribe(TOPIC_SAFETY_COMMAND)

    with TestClient(app):
        time.sleep(0.2)  # cho startup() subscribe xong truoc khi publish request
        request = SafetyCommandRequest(
            source_agent="test-harness", table_id=TABLE_ID, requested_action="close_contactor"
        )
        waiter.publish(TOPIC_SAFETY_COMMAND, request.model_dump_json())

        raw = waiter.wait_for(lambda m: m.get("in_reply_to") == request.message_id)
        ack = SafetyCommandAck(**raw)

        assert ack.approved is True
        assert ack.action == "close_contactor"
        assert ack.table_id == TABLE_ID
        assert ack.reason is None
        assert fake_plc.db_read_bool(2, OFFSET_SAFETY_FLAGS, BIT_CONTACTOR_STATE) is True


def test_close_contactor_rejected_when_e_stop_not_ok(fake_plc, waiter):
    fake_plc.db_write_bool(2, OFFSET_SAFETY_FLAGS, BIT_E_STOP_OK, False)
    init_plc_client(table_id=TABLE_ID, client=fake_plc)
    waiter.subscribe(TOPIC_SAFETY_COMMAND)

    with TestClient(app):
        time.sleep(0.2)
        request = SafetyCommandRequest(
            source_agent="test-harness", table_id=TABLE_ID, requested_action="close_contactor"
        )
        waiter.publish(TOPIC_SAFETY_COMMAND, request.model_dump_json())

        raw = waiter.wait_for(lambda m: m.get("in_reply_to") == request.message_id)
        ack = SafetyCommandAck(**raw)

        assert ack.approved is False
        assert ack.reason == "e_stop_not_ok"
        assert fake_plc.db_read_bool(2, OFFSET_SAFETY_FLAGS, BIT_CONTACTOR_STATE) is False


def test_open_contactor_always_allowed_even_when_unsafe(fake_plc, waiter):
    fake_plc.db_write_bool(2, OFFSET_SAFETY_FLAGS, BIT_THERMAL_RELAY_OK, False)
    fake_plc.db_write_bool(2, OFFSET_SAFETY_FLAGS, BIT_CONTACTOR_STATE, True)  # dang dong san
    init_plc_client(table_id=TABLE_ID, client=fake_plc)
    waiter.subscribe(TOPIC_SAFETY_COMMAND)

    with TestClient(app):
        time.sleep(0.2)
        request = SafetyCommandRequest(
            source_agent="test-harness", table_id=TABLE_ID, requested_action="open_contactor"
        )
        waiter.publish(TOPIC_SAFETY_COMMAND, request.model_dump_json())

        raw = waiter.wait_for(lambda m: m.get("in_reply_to") == request.message_id)
        ack = SafetyCommandAck(**raw)

        assert ack.approved is True
        assert fake_plc.db_read_bool(2, OFFSET_SAFETY_FLAGS, BIT_CONTACTOR_STATE) is False


def test_alert_published_on_overcurrent(fake_plc, waiter):
    fake_plc.seed_safe_state(current_A=11.0, temperature_C=45.0)  # vuot nguong 10.3A
    fake_plc.db_write_bool(2, OFFSET_SAFETY_FLAGS, BIT_CONTACTOR_STATE, True)
    init_plc_client(table_id=TABLE_ID, client=fake_plc)
    waiter.subscribe(TOPIC_SAFETY_ALERT)

    with TestClient(app):
        time.sleep(0.2)
        get_monitor().run_cycle()  # tu goi 1 chu ky thay vi cho thread nen (interval=999s)

        alert = waiter.wait_for(lambda m: m.get("fault_type") == "overcurrent")

        assert alert["table_id"] == TABLE_ID
        assert alert["value"] == pytest.approx(11.0)
        assert alert["threshold"] == pytest.approx(10.3)
        assert alert["severity"] == "critical"
        assert alert["action_taken"] == "contactor_opened"
        assert fake_plc.db_read_bool(2, OFFSET_SAFETY_FLAGS, BIT_CONTACTOR_STATE) is False


def test_alert_not_republished_while_still_over_threshold(fake_plc, waiter):
    fake_plc.seed_safe_state(current_A=11.0, temperature_C=45.0)
    init_plc_client(table_id=TABLE_ID, client=fake_plc)
    waiter.subscribe(TOPIC_SAFETY_ALERT)

    with TestClient(app):
        time.sleep(0.2)
        monitor = get_monitor()
        monitor.run_cycle()
        waiter.wait_for(lambda m: m.get("fault_type") == "overcurrent")

        monitor.run_cycle()
        monitor.run_cycle()
        time.sleep(0.5)  # cho neu co alert thu 2 bi gui nham thi kip toi

        overcurrent_alerts = [m for m in waiter._messages if m.get("fault_type") == "overcurrent"]
        assert len(overcurrent_alerts) == 1
