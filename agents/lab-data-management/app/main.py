"""
Entrypoint Lab Data Management Agent.

Chay (tu thu muc agents/lab-data-management/, sau khi da pip install -r requirements.txt o thu
muc goc du an):
    uvicorn app.main:app --reload

Nhiem vu (xem docs-thiet-ke/Thiet-ke-Event-Bus-MQTT-Topic-Schema.md):
- Subscribe lab/data/query, xu ly theo `query` ("device_info" | "schedule_lookup" |
  "borrow_record"), tra ve lab/data/result voi `in_reply_to` khop `message_id` cua query, `status`
  phu hop ("ok" | "not_found" | "error").
- CSDL SQLite (SQLAlchemy) - xem app/db/{session,models,seed}.py.
"""
import logging
import os
from datetime import date

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import BorrowRecord, Device, Schedule
from app.db.seed import init_db
from app.db.session import SessionLocal
from app.models.schemas import (
    BorrowRecordInfo,
    DeviceInfo,
    LabDataQueryMessage,
    LabDataResultMessage,
    ScheduleInfo,
)
from app.mqtt.client import LabDataAgentMqttClient, get_client, init_client
from app.mqtt.topics import SUBSCRIBE_TOPICS, TOPIC_DATA_RESULT

load_dotenv()

logger = logging.getLogger(__name__)

SOURCE_AGENT = "lab-data-agent"

MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "localhost")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", "1883"))

app = FastAPI(title="Lab Data Management Agent")


def handle_device_info(session: Session, request: LabDataQueryMessage) -> tuple[str, dict]:
    if not request.device_id:
        return "error", {"error": "thieu 'device_id' cho query 'device_info'"}

    device = session.get(Device, request.device_id)
    if device is None:
        return "not_found", {}

    info = DeviceInfo.model_validate(device, from_attributes=True)
    return "ok", {"device": info.model_dump(mode="json")}


def handle_schedule_lookup(session: Session, request: LabDataQueryMessage) -> tuple[str, dict]:
    table_id = request.filters.get("table_id")
    date_str = request.filters.get("date")

    stmt = select(Schedule)
    if table_id:
        stmt = stmt.where(Schedule.table_id == table_id)
    if date_str:
        try:
            parsed_date = date.fromisoformat(date_str)
        except ValueError:
            return "error", {"error": f"'filters.date' khong hop le (can dang YYYY-MM-DD): {date_str!r}"}
        stmt = stmt.where(Schedule.practice_date == parsed_date)
    stmt = stmt.order_by(Schedule.practice_date, Schedule.start_time)

    schedules = session.execute(stmt).scalars().all()
    if not schedules:
        return "not_found", {}

    infos = [ScheduleInfo.model_validate(s, from_attributes=True).model_dump(mode="json") for s in schedules]
    return "ok", {"schedules": infos}


def handle_borrow_record(session: Session, request: LabDataQueryMessage) -> tuple[str, dict]:
    device_id = request.device_id
    student_id = request.filters.get("student_id")

    if not device_id and not student_id:
        return "error", {"error": "can 'device_id' hoac 'filters.student_id' cho query 'borrow_record'"}

    stmt = select(BorrowRecord)
    if device_id:
        stmt = stmt.where(BorrowRecord.device_id == device_id)
    if student_id:
        stmt = stmt.where(BorrowRecord.student_id == student_id)
    stmt = stmt.order_by(BorrowRecord.borrowed_at.desc())

    records = session.execute(stmt).scalars().all()
    if not records:
        return "not_found", {}

    infos = [BorrowRecordInfo.model_validate(r, from_attributes=True).model_dump(mode="json") for r in records]
    return "ok", {"borrow_records": infos}


# ---- Anh xa "query" -> ham xu ly - them query moi thi chi can them 1 dong o day ----
QUERY_HANDLERS = {
    "device_info": handle_device_info,
    "schedule_lookup": handle_schedule_lookup,
    "borrow_record": handle_borrow_record,
}


def handle_query_request(mqtt_client: LabDataAgentMqttClient, request: LabDataQueryMessage) -> LabDataResultMessage:
    """Xu ly 1 yeu cau tren lab/data/query, publish lab/data/result tuong ung, tra ve message
    da publish."""
    handler = QUERY_HANDLERS.get(request.query)

    if handler is None:
        status, spec = "error", {"error": f"query khong duoc ho tro: {request.query!r}"}
    else:
        try:
            with SessionLocal() as session:
                status, spec = handler(session, request)
        except Exception:
            logger.exception("Loi noi bo khi xu ly query '%s'", request.query)
            status, spec = "error", {"error": "loi noi bo khi truy van CSDL"}

    result = LabDataResultMessage(
        source_agent=SOURCE_AGENT,
        in_reply_to=request.message_id,
        device_id=request.device_id,
        status=status,
        spec=spec,
    )
    mqtt_client.publish(TOPIC_DATA_RESULT, result)
    return result


def _on_query(payload: dict) -> None:
    try:
        request = LabDataQueryMessage(**payload)
    except ValidationError:
        logger.warning("Payload lab/data/query khong hop le: %s", payload)
        return
    handle_query_request(get_client(), request)


@app.on_event("startup")
def startup() -> None:
    init_db()  # tao bang neu chua co - KHONG tu seed du lieu mau (xem app/db/seed.py de seed tay)

    mqtt_client = init_client(host=MQTT_BROKER_HOST, port=MQTT_BROKER_PORT)
    mqtt_client.connect()
    for topic in SUBSCRIBE_TOPICS:
        mqtt_client.subscribe(topic, handler=_on_query)


@app.on_event("shutdown")
def shutdown() -> None:
    get_client().disconnect()
