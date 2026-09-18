"""
Engine + Session SQLAlchemy cho Lab Data Management Agent.

Dev/Ngay 6-10 dung SQLite tai `agents/lab-data-management/data/lab_data.db` (file duong dan
TUYET DOI, khong phu thuoc thu muc dang chay uvicorn/pytest tu dau - giong PROJECT_ROOT cua
`python-bridge/main_bridge.py` o Do an 1). Co the doi sang PostgreSQL sau nay (README.md) chi
bang cach doi bien moi truong LAB_DATA_DATABASE_URL, khong can sua code o day.
"""
import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent  # .../agents/lab-data-management/
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "lab_data.db"
DEFAULT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

DATABASE_URL = os.getenv("LAB_DATA_DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")

# SQLite mac dinh chan dung lai connection tu thread khac - FastAPI/paho chay handler tren
# thread nen (paho loop_start) nen PHAI tat check_same_thread, giong nguyen tac cua
# python-snap7 client trong safety-tutoring (khong duoc block/crash vi khac thread).
_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=_connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass
