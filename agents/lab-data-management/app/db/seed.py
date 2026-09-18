"""
Migration/seed script cho CSDL Lab Data Management Agent (SQLite, dev/test).

Chay doc lap (tu thu muc agents/lab-data-management/, sau khi da active venv o thu muc goc du an):
    python -m app.db.seed

Tao bang neu chua co (`init_db`) roi chen du lieu mau NEU tung bang dang rong (`seed` - idempotent,
chay lai nhieu lan khong bi trung du lieu). `tests/test_lab_data_agent.py` cung import truc tiep
`SAMPLE_*`/`seed`/`init_db` tu day de dung CHUNG 1 nguon du lieu mau voi script nay, tranh lech.
"""
from datetime import date, datetime, time

from sqlalchemy.orm import Session

from app.db.models import BorrowRecord, Device, Schedule
from app.db.session import Base, SessionLocal, engine

SAMPLE_DEVICES = [
    dict(
        device_id="PLC-01", name="PLC S7-1500 ban B01", table_id="B01", device_type="PLC",
        status="active", specifications={"model": "CPU 1516-3 PN/DP", "firmware": "V2.9"},
    ),
    dict(
        device_id="PLC-03", name="PLC S7-1500 ban B03", table_id="B03", device_type="PLC",
        status="active", specifications={"model": "CPU 1516-3 PN/DP", "firmware": "V2.9"},
    ),
    dict(
        device_id="MOTOR-B03-01", name="Dong co 3 pha ban B03", table_id="B03", device_type="motor",
        status="maintenance", specifications={"power_kw": 0.75, "voltage_V": 380},
    ),
]

SAMPLE_SCHEDULES = [
    dict(
        class_name="DA2-N05", subject="Thuc hanh PLC co ban", table_id="B03",
        practice_date=date(2026, 9, 20), start_time=time(7, 0), end_time=time(9, 30),
        instructor="ThS. Tran Trung Khanh",
    ),
    dict(
        class_name="DA2-N05", subject="Thuc hanh khoi dong DOL / dao chieu sao-tam giac", table_id="B03",
        practice_date=date(2026, 9, 22), start_time=time(13, 0), end_time=time(15, 30),
        instructor="ThS. Tran Trung Khanh",
    ),
]

SAMPLE_BORROW_RECORDS = [
    dict(
        device_id="MOTOR-B03-01", student_id="sv001", student_name="Nguyen Van A",
        borrowed_at=datetime(2026, 9, 18, 8, 0), returned_at=None, status="borrowed",
    ),
    dict(
        device_id="PLC-01", student_id="sv002", student_name="Tran Thi B",
        borrowed_at=datetime(2026, 9, 10, 8, 0), returned_at=datetime(2026, 9, 10, 11, 0),
        status="returned",
    ),
]


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def seed(session: Session) -> None:
    if session.query(Device).count() == 0:
        session.add_all(Device(**row) for row in SAMPLE_DEVICES)
        session.flush()  # can co truoc khi insert BorrowRecord (FK toi devices.device_id)
    if session.query(Schedule).count() == 0:
        session.add_all(Schedule(**row) for row in SAMPLE_SCHEDULES)
    if session.query(BorrowRecord).count() == 0:
        session.add_all(BorrowRecord(**row) for row in SAMPLE_BORROW_RECORDS)
    session.commit()


def main() -> None:
    init_db()
    with SessionLocal() as session:
        seed(session)


if __name__ == "__main__":
    main()
