"""
Test luong that cua Lab Data Management Agent - dung Mosquitto that dang chay san
(localhost:1883, KHONG mock MQTT). CSDL dung SQLite THAT (khong fake) tren 1 file tam rieng cho
lan chay test, seed du lieu mau tu CHINH app/db/seed.py (dung 1 nguon voi script seed that, tranh
lech du lieu mau giua test va production).

Chay: pytest tests/test_lab_data_agent.py (tu thu muc agents/lab-data-management/, can Mosquitto
dang chay o localhost:1883).
"""
import json
import os
import tempfile
import threading
import time
import uuid
from pathlib import Path

# QUAN TRONG: dat LAB_DATA_DATABASE_URL truoc khi import app.db/app.main lan dau - engine duoc
# tao NGAY LUC IMPORT (xem app/db/session.py). Dung 1 file SQLite tam rieng cho lan chay test
# nay, khong dung chung file lab_data.db that (tranh lam ban du lieu dev/demo va tranh xung
# dot neu chay test song song voi server dang chay that).
_TEST_DB_PATH = Path(tempfile.gettempdir()) / f"lab_data_test_{uuid.uuid4().hex}.db"
os.environ["LAB_DATA_DATABASE_URL"] = f"sqlite:///{_TEST_DB_PATH}"

import paho.mqtt.client as mqtt
import pytest
from fastapi.testclient import TestClient

from app.db.seed import SAMPLE_BORROW_RECORDS, SAMPLE_DEVICES, SAMPLE_SCHEDULES, init_db, seed
from app.db.session import SessionLocal
from app.main import app
from app.models.schemas import LabDataQueryMessage, LabDataResultMessage
from app.mqtt.topics import TOPIC_DATA_QUERY, TOPIC_DATA_RESULT

MQTT_HOST = os.getenv("MQTT_BROKER_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_BROKER_PORT", "1883"))


def _setup_module_db() -> None:
    init_db()
    with SessionLocal() as session:
        seed(session)


_setup_module_db()


def teardown_module(module) -> None:
    """Hook xunit-style cua pytest - tu dong goi sau khi CHAY XONG toan bo test trong file nay,
    don file SQLite tam da tao o dau file."""
    try:
        _TEST_DB_PATH.unlink(missing_ok=True)
    except OSError:
        pass


class MqttWaiter:
    """Test harness MQTT client rieng (khong phai client cua Lab Data Agent) - dung de publish
    query va cho result that qua Mosquitto dang chay san."""

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
def waiter():
    harness = MqttWaiter()
    harness.subscribe(TOPIC_DATA_RESULT)
    yield harness
    harness.close()


def _send_query(waiter: MqttWaiter, **kwargs) -> LabDataResultMessage:
    request = LabDataQueryMessage(source_agent="test-harness", **kwargs)
    waiter.publish(TOPIC_DATA_QUERY, request.model_dump_json())
    raw = waiter.wait_for(lambda m: m.get("in_reply_to") == request.message_id)
    return LabDataResultMessage(**raw)


def test_device_info_found(waiter):
    with TestClient(app):
        time.sleep(0.2)  # cho startup() subscribe xong truoc khi publish query
        sample = SAMPLE_DEVICES[0]  # PLC-01
        result = _send_query(waiter, query="device_info", device_id=sample["device_id"])

        assert result.status == "ok"
        assert result.device_id == sample["device_id"]
        assert result.spec["device"]["name"] == sample["name"]
        assert result.spec["device"]["table_id"] == sample["table_id"]
        assert result.spec["device"]["specifications"] == sample["specifications"]


def test_device_info_not_found(waiter):
    with TestClient(app):
        time.sleep(0.2)
        result = _send_query(waiter, query="device_info", device_id="KHONG-TON-TAI-999")

        assert result.status == "not_found"
        assert result.spec == {}


def test_device_info_missing_device_id_is_error(waiter):
    with TestClient(app):
        time.sleep(0.2)
        result = _send_query(waiter, query="device_info")

        assert result.status == "error"
        assert "device_id" in result.spec.get("error", "")


def test_schedule_lookup_by_table_and_date(waiter):
    with TestClient(app):
        time.sleep(0.2)
        sample = SAMPLE_SCHEDULES[0]
        result = _send_query(
            waiter,
            query="schedule_lookup",
            filters={"table_id": sample["table_id"], "date": sample["practice_date"].isoformat()},
        )

        assert result.status == "ok"
        schedules = result.spec["schedules"]
        assert len(schedules) == 1
        assert schedules[0]["class_name"] == sample["class_name"]
        assert schedules[0]["subject"] == sample["subject"]
        assert schedules[0]["instructor"] == sample["instructor"]


def test_schedule_lookup_no_match_is_not_found(waiter):
    with TestClient(app):
        time.sleep(0.2)
        result = _send_query(
            waiter, query="schedule_lookup", filters={"table_id": "B99", "date": "2099-01-01"}
        )

        assert result.status == "not_found"


def test_schedule_lookup_invalid_date_is_error(waiter):
    with TestClient(app):
        time.sleep(0.2)
        result = _send_query(waiter, query="schedule_lookup", filters={"date": "khong-phai-ngay"})

        assert result.status == "error"
        assert "date" in result.spec.get("error", "")


def test_borrow_record_by_device_id(waiter):
    with TestClient(app):
        time.sleep(0.2)
        sample = SAMPLE_BORROW_RECORDS[0]  # MOTOR-B03-01, sv001, chua tra
        result = _send_query(waiter, query="borrow_record", device_id=sample["device_id"])

        assert result.status == "ok"
        records = result.spec["borrow_records"]
        assert len(records) == 1
        assert records[0]["student_id"] == sample["student_id"]
        assert records[0]["status"] == "borrowed"
        assert records[0]["returned_at"] is None


def test_borrow_record_by_student_id(waiter):
    with TestClient(app):
        time.sleep(0.2)
        sample = SAMPLE_BORROW_RECORDS[1]  # PLC-01, sv002, da tra
        result = _send_query(waiter, query="borrow_record", filters={"student_id": sample["student_id"]})

        assert result.status == "ok"
        records = result.spec["borrow_records"]
        assert len(records) == 1
        assert records[0]["device_id"] == sample["device_id"]
        assert records[0]["status"] == "returned"
        assert records[0]["returned_at"] is not None


def test_borrow_record_missing_identifier_is_error(waiter):
    with TestClient(app):
        time.sleep(0.2)
        result = _send_query(waiter, query="borrow_record")

        assert result.status == "error"


def test_unsupported_query_type_is_error(waiter):
    with TestClient(app):
        time.sleep(0.2)
        result = _send_query(waiter, query="firmware_update_history")

        assert result.status == "error"
        assert "firmware_update_history" in result.spec.get("error", "")
