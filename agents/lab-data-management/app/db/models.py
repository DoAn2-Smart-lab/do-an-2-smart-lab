"""
ORM model (SQLAlchemy 2.0 style, `Mapped`/`mapped_column`) cho CSDL Lab Data Management Agent.

3 bang toi thieu theo yeu cau Ngay 6-10:
- devices: thiet bi trong phong thi nghiem, lien ket ban thuc hanh qua `table_id` (dinh dang
  "B0n" - THONG NHAT voi cac Agent khac, xem docs-thiet-ke/Thiet-ke-Event-Bus-MQTT-Topic-Schema.md).
- schedules: lich thuc hanh (lop, mon, ban, ngay/gio, giang vien).
- borrow_records: muon/tra thiet bi (thiet bi, sinh vien, thoi gian muon/tra, trang thai).
"""
from datetime import date as date_
from datetime import datetime, time as time_

from sqlalchemy import JSON, Date, DateTime, ForeignKey, String, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Device(Base):
    __tablename__ = "devices"

    device_id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    table_id: Mapped[str | None] = mapped_column(String, nullable=True)
    device_type: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="active")
    # Thong so ky thuat dang JSON tu do (vd {"model": "...", "power_kw": 0.75}) - moi loai thiet
    # bi co bo thong so khac nhau nen khong tach cot rieng.
    specifications: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    borrow_records: Mapped[list["BorrowRecord"]] = relationship(back_populates="device")


class Schedule(Base):
    __tablename__ = "schedules"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    class_name: Mapped[str] = mapped_column(String, nullable=False)
    subject: Mapped[str] = mapped_column(String, nullable=False)
    table_id: Mapped[str] = mapped_column(String, nullable=False)
    practice_date: Mapped[date_] = mapped_column(Date, nullable=False)
    start_time: Mapped[time_] = mapped_column(Time, nullable=False)
    end_time: Mapped[time_] = mapped_column(Time, nullable=False)
    instructor: Mapped[str] = mapped_column(String, nullable=False)


class BorrowRecord(Base):
    __tablename__ = "borrow_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    device_id: Mapped[str] = mapped_column(String, ForeignKey("devices.device_id"), nullable=False)
    student_id: Mapped[str] = mapped_column(String, nullable=False)
    student_name: Mapped[str | None] = mapped_column(String, nullable=True)
    borrowed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    returned_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False, default="borrowed")

    device: Mapped["Device"] = relationship(back_populates="borrow_records")
