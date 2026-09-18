"""
Pydantic model cho payload MQTT cua Lab Data Management Agent.

Cac field PHAI khop voi cot "Payload mau" trong
docs-thiet-ke/Thiet-ke-Event-Bus-MQTT-Topic-Schema.md (ban chot Ngay 2), chi lay dung 2 topic
lien quan Agent nay (lab/data/query, lab/data/result). Neu Master Orchestrator doi field, sua
file .md truoc roi moi sua lai o day, khong tu y doi field mot phia.
"""
import uuid
from datetime import date, datetime, time, timedelta, timezone
from typing import Optional

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


# ---- lab/data/query (subscribe) ----
class LabDataQueryMessage(MqttEnvelope):
    # "query" (KHONG phai "query_type") - dung dung ten field trong file schema. Gia tri hop le
    # hien tai: "device_info" | "schedule_lookup" | "borrow_record", nhung de la `str` (khong
    # phai Literal) de payload voi gia tri la nhung khac VAN parse duoc - de app/main.py tu tra
    # ve status="error" ro rang thay vi de pydantic am tham loai bo ca message (xem yeu cau
    # "query_type khong ho tro phai tra loi ro", khong duoc im lang).
    query: str
    device_id: Optional[str] = None
    filters: dict = Field(default_factory=dict)


# ---- lab/data/result (publish) ----
class LabDataResultMessage(MqttEnvelope):
    in_reply_to: str
    # Khac voi ban DataResult cu trong models cua Master Orchestrator (dang bat buoc device_id) -
    # o day de Optional vi "schedule_lookup"/"borrow_record theo sinh vien" khong co 1 device_id
    # duy nhat. Xem HANDOFF_LOG.md muc TODO: can noi long lai ben Orchestrator khi tich hop that.
    device_id: Optional[str] = None
    status: str  # "ok" | "not_found" | "error"
    spec: dict = Field(default_factory=dict)


# ---- Model con mo ta du lieu tra ve trong "spec", ung voi tung bang CSDL ----
class DeviceInfo(BaseModel):
    device_id: str
    name: str
    table_id: Optional[str] = None
    device_type: str
    status: str
    specifications: dict = Field(default_factory=dict)


class ScheduleInfo(BaseModel):
    class_name: str
    subject: str
    table_id: str
    practice_date: date
    start_time: time
    end_time: time
    instructor: str


class BorrowRecordInfo(BaseModel):
    device_id: str
    student_id: str
    student_name: Optional[str] = None
    borrowed_at: datetime
    returned_at: Optional[datetime] = None
    status: str
