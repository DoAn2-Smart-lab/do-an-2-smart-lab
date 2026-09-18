"""
Wrapper python-snap7 cho Safety & Practical Tutoring Agent - doc/ghi DB tren PLC S7-1500 qua
S7comm, ke thua truc tiep cach lam cua Do an 1
(``C:\\DT4-smart laboratory\\...\\mo-phong-s7-1500-smart-lab\\python-bridge\\main_bridge.py``).

QUAN TRONG - hien CHUA CO PLCSIM Advanced chay duoc (dang cho license), nen class nay PHAI nhan
duoc mot `client` da co san (fake/mock) de inject khi test, KHONG duoc tu tao ket noi that va
KHONG duoc block truong hop khong co PLC. Xem tests/test_safety_agent.py de biet cach dung
FakeSnap7Client thay the.

---- Nguon offset ----
`OFFSET_MOTOR_CURRENT` / `OFFSET_MOTOR_TEMPERATURE` lay Y NGUYEN tu
`scl/DB_Alert.scl` + `python-bridge/main_bridge.py` (DB2, "Details view" da xac nhan that o
Do an 1) - KHONG duoc doi neu chua doi chieu lai 2 file do.

`OFFSET_SAFETY_FLAGS` (E-Stop/ro-le nhiet/ngan mach/contactor) la CAC TAG MOI cho bai thuc hanh
DOL/dao chieu sao-tam giac cua Do an 2, CHUA TON TAI trong DB_Alert.scl that (xem
agents/safety-tutoring/README.md muc 1: phai tu tay mo TIA Portal them tag nay, compile +
download qua PLCSIM, roi doi chieu lai "Details view" that). Offset `26` o day chi la vi tri
TIEP NOI SAU byte cuoi cung da biet (0..25 da dung het cho DB_Alert goc) - PHAI sua lai cho khop
100% voi Details view that ngay khi file .scl duoc cap nhat, KHONG duoc coi day la so cuoi cung.
"""
import logging
from typing import Optional, Protocol

import snap7
import snap7.client

logger = logging.getLogger(__name__)


class Snap7ClientProtocol(Protocol):
    """Interface toi thieu ma SafetyPlcClient can o client - dung dung chu ky ham cua
    snap7.client.Client that, nen fake test chi can implement dung tung nay ham, khong can
    PLCSIM/DLL that."""

    def connect(self, address: str, rack: int, slot: int) -> None: ...

    def disconnect(self) -> None: ...

    def get_connected(self) -> bool: ...

    def db_read_bool(self, db_number: int, byte_offset: int, bit_offset: int) -> bool: ...

    def db_write_bool(self, db_number: int, byte_offset: int, bit_offset: int, value: bool) -> None: ...

    def db_read_real(self, db_number: int, offset: int) -> float: ...


# ---- Offset KE THUA THAT tu Do an 1 (DB_Alert / DB2) - khong duoc bia so ----
OFFSET_MOTOR_CURRENT = 8         # Real, 4 byte -> anh xa sang "current_A" cua lab/safety/status
OFFSET_MOTOR_TEMPERATURE = 12    # Real, 4 byte -> anh xa sang "temperature_C"

# ---- Offset TAM DAT cho tag DOL/sao-tam giac MOI, CHUA CO trong .scl that - xem docstring ----
OFFSET_SAFETY_FLAGS = 26         # 1 byte gop chung 5 bit ben duoi - TODO xac nhan lai voi .scl
BIT_E_STOP_OK = 0
BIT_THERMAL_RELAY_OK = 1
BIT_SHORT_CIRCUIT_OK = 2
BIT_CONTACTOR_STATE = 3          # bit DOC - trang thai tiep diem phu, PLC ghi, Python CHI DOC
BIT_CONTACTOR_CMD = 4            # bit GHI - lenh dong/cat, Safety Agent la noi DUY NHAT ghi bit nay

DEFAULT_PLC_IP = "192.168.0.1"
DEFAULT_PLC_RACK = 0
DEFAULT_PLC_SLOT = 1
DEFAULT_DB_NUMBER = 2


class SafetyPlcClient:
    """Boc quanh python-snap7, gan voi DUNG MOT ban thuc hanh (`table_id`) tren DUNG MOT DB.
    Model nhieu ban/nhieu DB dong thoi chua can trong pham vi demo Ngay 2 - xem HANDOFF_LOG.md
    phan TODO."""

    def __init__(
        self,
        table_id: str,
        plc_ip: str = DEFAULT_PLC_IP,
        rack: int = DEFAULT_PLC_RACK,
        slot: int = DEFAULT_PLC_SLOT,
        db_number: int = DEFAULT_DB_NUMBER,
        client: Optional[Snap7ClientProtocol] = None,
    ):
        self._table_id = table_id
        self._plc_ip = plc_ip
        self._rack = rack
        self._slot = slot
        self._db_number = db_number
        # Chi tu tao snap7.client.Client() that khi khong co client nao duoc inject - cho phep
        # test dung fake ma KHONG can PLCSIM/DLL snap7 that cai san.
        self._client: Snap7ClientProtocol = client if client is not None else snap7.client.Client()

    @property
    def table_id(self) -> str:
        return self._table_id

    def connect(self) -> None:
        try:
            self._client.connect(self._plc_ip, self._rack, self._slot)
        except Exception:
            logger.exception(
                "Khong ket noi duoc PLC %s (rack=%s slot=%s) cho ban %s - se tiep tuc thu lai "
                "o vong doc trang thai tiep theo, KHONG lam sap Safety Agent.",
                self._plc_ip, self._rack, self._slot, self._table_id,
            )

    def disconnect(self) -> None:
        try:
            self._client.disconnect()
        except Exception:
            logger.exception("Loi khi ngat ket noi PLC cho ban %s", self._table_id)

    def read_safety_status(self) -> dict:
        """Tra ve dict khop dung field cua lab/safety/status (xem models/schemas.py:
        SafetyStatusMessage)."""
        return {
            "table_id": self._table_id,
            "e_stop_ok": self._client.db_read_bool(self._db_number, OFFSET_SAFETY_FLAGS, BIT_E_STOP_OK),
            "thermal_relay_ok": self._client.db_read_bool(
                self._db_number, OFFSET_SAFETY_FLAGS, BIT_THERMAL_RELAY_OK
            ),
            "short_circuit_ok": self._client.db_read_bool(
                self._db_number, OFFSET_SAFETY_FLAGS, BIT_SHORT_CIRCUIT_OK
            ),
            "contactor_state": (
                "closed"
                if self._client.db_read_bool(self._db_number, OFFSET_SAFETY_FLAGS, BIT_CONTACTOR_STATE)
                else "open"
            ),
            "current_A": self._client.db_read_real(self._db_number, OFFSET_MOTOR_CURRENT),
            "temperature_C": self._client.db_read_real(self._db_number, OFFSET_MOTOR_TEMPERATURE),
        }

    def close_contactor(self, table_id: str) -> None:
        self._assert_table(table_id)
        self._client.db_write_bool(self._db_number, OFFSET_SAFETY_FLAGS, BIT_CONTACTOR_CMD, True)

    def open_contactor(self, table_id: str) -> None:
        self._assert_table(table_id)
        self._client.db_write_bool(self._db_number, OFFSET_SAFETY_FLAGS, BIT_CONTACTOR_CMD, False)

    def _assert_table(self, table_id: str) -> None:
        if table_id != self._table_id:
            raise ValueError(
                f"SafetyPlcClient nay quan ly ban {self._table_id!r}, khong duoc goi voi "
                f"table_id={table_id!r} - moi ban thuc hanh phai co instance rieng."
            )


_plc_client: Optional[SafetyPlcClient] = None


def init_plc_client(
    table_id: str,
    plc_ip: str = DEFAULT_PLC_IP,
    rack: int = DEFAULT_PLC_RACK,
    slot: int = DEFAULT_PLC_SLOT,
    db_number: int = DEFAULT_DB_NUMBER,
    client: Optional[Snap7ClientProtocol] = None,
) -> SafetyPlcClient:
    global _plc_client
    _plc_client = SafetyPlcClient(
        table_id=table_id, plc_ip=plc_ip, rack=rack, slot=slot, db_number=db_number, client=client
    )
    return _plc_client


def get_plc_client() -> SafetyPlcClient:
    if _plc_client is None:
        raise RuntimeError("PLC client chua duoc khoi tao - goi init_plc_client() truoc (xem app/main.py)")
    return _plc_client


def is_plc_client_initialized() -> bool:
    return _plc_client is not None
