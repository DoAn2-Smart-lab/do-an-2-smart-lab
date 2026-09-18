# HANDOFF LOG — Đồ án 2

## 2026-09-17
- Nhận tài liệu định hướng Đồ án 2 từ ThS. Trần Trung Khánh (ban hành 14/09/2026): Nhóm 05 chuyển
  sang xây Hệ thống Đa Agent quản trị phòng thí nghiệm, 4 Agent cốt lõi.
- Soạn và nộp đề cương chi tiết Đồ án 2 (mục tiêu, sơ đồ khối, phân công, kế hoạch 15 tuần).
- Thu thập ý tưởng bổ sung của nhóm qua Zalo (Thành Phát): Local AI, CSDL thiết bị chi tiết, upload
  tài liệu, Digital Twin/CAD qua Claude MCP — đã đối chiếu và ghi rõ ý nào nằm trong phạm vi Đồ án
  2, ý nào để dành cho Khóa luận tốt nghiệp.
- Dựng khung thư mục dự án `Do-an-2-he-thong-da-agent-ptn-thong-minh/`.

- Soạn dự thảo Event Bus/MQTT topic schema, `requirements.txt`, README kế hoạch cho 4 Agent.
- Soạn bảng phân định "làm ở Cowork" vs "bắt buộc chuyển sang Claude Code/VSCode" theo từng tuần.

## Việc tiếp theo (Tuần 1 — chuyển sang Claude Code/VSCode)
- [x] Cài đặt môi trường: LangGraph, FastAPI AsyncIO, MQTT broker (Mosquitto) — Mosquitto đã được
  cài trước đó, tự chạy nền dưới dạng Windows Service (không cần khởi động tay).
- [x] Rà soát lại code Đồ án 1 để xác định phần cần nâng cấp cho Safety Agent (xem tóm tắt trong
  phiên Claude Code — kỹ thuật timer thời gian thực, chốt giá trị `_AtFault`, mẫu 2-tầng DB, lớp
  giao tiếp `python-snap7` trong `main_bridge.py`).
- [x] `git init` cho thư mục Đồ án 2, commit lần đầu — xem mục "Dọn dẹp trùng lặp" bên dưới.
- [x] Mở Claude Code tại `C:\DoAn2-smartlab\` (đường dẫn cố định từ nay, không còn nằm trong
  Downloads) — xem mục "Dọn dẹp trùng lặp" bên dưới.
- [x] Tạo khung sườn code (skeleton) `agents/master-orchestrator/` (FastAPI + LangGraph 5-node,
  intent classifier rule-based đã test pass 4/4 kịch bản, MQTT client + topics/schemas đúng
  `docs-thiet-ke/Thiet-ke-Event-Bus-MQTT-Topic-Schema.md`). Còn thiếu: `wait_response` chờ MQTT
  thật, tách tham số lệnh cụ thể, Voice (Tuần 12).

## Dọn dẹp trùng lặp (2026-09-17, cuối ngày)
Máy có nhiều bản sao rải rác do export nhiều lần từ phiên Cowork trước khi chuyển sang Claude
Code (`Do-an-2-he-thong-da-agent-ptn-thong-minh.zip`, `_1.zip`, `_2.zip`, và 2 thư mục đã giải
nén `_1`/`_2` trong Downloads) — đã dọn về đúng 1 bản duy nhất:
- **Bản chính thức (từ nay):** `C:\DoAn2-smartlab\` — chuyển toàn bộ nội dung từ bản Downloads
  `_1` (bản có nhiều file/code nhất, gồm skeleton `agents/master-orchestrator/` vừa tạo) vào đây,
  giữ nguyên `venv/` (Python 3.14) đã có sẵn ở đó.
- **Đã xóa hẳn:** thư mục Downloads `_2` (chỉ có README kế hoạch, không có code, đã merge hết vào
  bản chính trước đó) và thư mục Downloads `_1` gốc (rỗng sau khi chuyển).
- **Đã archive** (không xóa hẳn, phòng cần đối chiếu bản Cowork gốc) 3 file `.zip` + 1 bản `.docx`
  đề cương nằm lẻ ngoài Downloads vào `archive-deprecated/zips-cowork-2026-09-17/`.
- **Không đụng tới** `C:\DT4-smart laboratory\...\mo-phong-s7-1500-smart-lab\` — đây là Đồ án 1
  đã nộp (đề tài khác), không phải bản trùng của Đồ án 2, vẫn là nguồn kế thừa chính thức.
- Đã `git init` + thêm `.gitignore` (loại `venv/`, `__pycache__/`, `.env`, nội dung `data-logs/`)
  + commit lần đầu tại `C:\DoAn2-smartlab\`.

## Ngày 1 (2026-09-17) — HOÀN THÀNH
- Môi trường cài đủ: `fastapi` 0.141.1, `langgraph` 1.2.11, `langchain-core`, `paho-mqtt` 2.1.0,
  `python-snap7` 3.1.2, `pydantic` 2.13, `uvicorn`, `python-dotenv`, `sqlalchemy`, `requests`,
  `pytest` — cài trong `venv/` tại `C:\DoAn2-smartlab\venv\` (Python 3.14.6).
- MQTT broker Mosquitto đã cài sẵn từ trước, chạy nền dưới dạng Windows Service tại
  `localhost:1883` — không cần cài lại hay khởi động tay.
- **Master Orchestrator Agent test PASS 4/4 kịch bản với thư viện thật, KHÔNG mock:**
  - `pytest tests/test_intent_classifier.py` — 4/4 pass (safety_tutoring, lab_data, power_load,
    unknown).
  - Toàn bộ chuỗi thật đã chạy qua `TestClient` gọi HTTP `POST /chat` → LangGraph 5-node →
    intent classifier → publish MQTT thật lên Mosquitto Windows Service — xác nhận bằng 1
    subscriber Python độc lập nhận đúng JSON trên cả 3 topic (`lab/orchestrator/intent`,
    `lab/data/query`, `lab/power/command`), đúng field theo
    `docs-thiet-ke/Thiet-ke-Event-Bus-MQTT-Topic-Schema.md`.
  - Không phát sinh lỗi import/tương thích phiên bản nào cần sửa (paho-mqtt v2
    `CallbackAPIVersion.VERSION2`, LangGraph `StateGraph`/`START`/`END`, FastAPI `@app.on_event`
    — tất cả đều chạy đúng với bản đã cài).

## Ngày 2 (2026-09-17) — HOÀN THÀNH
- Ghi đè `docs-thiet-ke/Thiet-ke-Event-Bus-MQTT-Topic-Schema.md` bằng bản chốt Ngày 2: envelope
  chung `message_id`/`timestamp` (+07:00)/`source_agent`, QoS + retain cho từng topic, đổi
  `zone`→`table_id` thống nhất, và cơ chế request/ACK 2 chiều trên `lab/safety/command`.
- Cập nhật code theo đúng schema mới:
  - `app/mqtt/topics.py`: đủ 8 topic + `TOPIC_QOS`/`TOPIC_RETAIN`; `lab/safety/command` giờ vừa
    publish (request) vừa subscribe (ack) — có chặn cứng không cho publish `type="ack"`.
  - `app/models/schemas.py`: envelope có `message_id` (UUID v4) + `timestamp` giờ VN (+07:00);
    thêm `SafetyCommandRequest`/`SafetyCommandAck` theo đúng ví dụ JSON trong schema.
  - `app/mqtt/client.py`: `publish()` giờ tự dùng đúng QoS/retain theo topic; thêm
    `wait_for_ack(message_id, timeout)` — khớp `in_reply_to`, dùng `threading.Event`, đã verify
    thật cả 2 nhánh (có ACK trả lời nhanh <1s / hết giờ đúng ~3s) bằng 1 Safety Agent giả lập
    qua broker Mosquitto thật.
  - `app/graph/nodes.py`: `wait_response` cho `safety_tutoring` giờ CHỜ ACK THẬT (không còn
    placeholder) — publish broadcast lên `lab/orchestrator/intent` rồi gửi yêu cầu cụ thể lên
    `lab/safety/command`, chờ tối đa 3s, báo lỗi rõ ràng nếu timeout hoặc bị từ chối
    (`approved: false` kèm `reason`). `lab_data`/`power_load` **vẫn còn là TODO** — vẫn
    fire-and-forget, chưa chờ kết quả thật.
  - `app/intent/classifier.py`: tách `table_id` (regex `B0n`) và `action` ra khỏi câu nói thô
    thay vì gộp chung vào 1 chuỗi `intent`.
  - `app/api/chat.py`: chạy `graph.invoke()` trong thread pool (`asyncio.to_thread`) vì giờ có
    thể block thật tới 3s khi chờ Safety Agent — tránh nghẽn event loop FastAPI.
- **Test:** `pytest` 4/4 vẫn pass (mở rộng thêm assertion `table_id`/`action` cho từng kịch bản,
  không có test nào fail phải sửa lại). Verify thêm bằng script thủ công (không nằm trong bộ
  test tracked — cần Safety Agent giả lập, chưa phù hợp làm unit test tự động): xác nhận cả
  nhánh ACK thành công và nhánh timeout 3s đều đúng thiết kế.
- **TODO còn lại:** cơ chế chờ kết quả thật cho `lab_data` (`lab/data/result`, đã có sẵn
  `in_reply_to` trong schema nhưng chưa nối) và `power_load` (schema chưa có kênh phản hồi);
  Voice (Tuần 12); thay rule-based classifier bằng SLM local.

## Safety & Practical Tutoring Agent — logic + test giả lập (2026-09-18)
- Xây xong khung code tại `agents/safety-tutoring/` (đặt đúng thư mục đã có sẵn từ trước, không
  tạo `agents/safety-agent/` mới để tránh trùng lặp — README/PROJECT_CONTEXT.md đều đã dùng tên
  `safety-tutoring`), theo đúng quy ước của `agents/master-orchestrator/`:
  - `app/models/schemas.py`: `SafetyStatusMessage`, `SafetyCommandRequest`, `SafetyCommandAck`,
    `SafetyAlertMessage` — đúng field/kiểu theo
    `docs-thiet-ke/Thiet-ke-Event-Bus-MQTT-Topic-Schema.md`.
  - `app/mqtt/topics.py`, `app/mqtt/client.py`: chỉ 3/8 topic Safety Agent cần
    (`lab/safety/status|command|alert`), có chặn cứng không cho publish `type="request"` (việc đó
    là của Orchestrator).
  - `app/plc/snap7_client.py` — `SafetyPlcClient` bọc `python-snap7`, nhận tham số `client=` để
    inject fake/mock (không phụ thuộc PLCSIM Advanced thật, hiện vẫn đang chờ license):
    - `current_A`/`temperature_C` dùng ĐÚNG offset thật kế thừa từ Đồ án 1
      (`OFFSET_MOTOR_CURRENT=8`, `OFFSET_MOTOR_TEMPERATURE=12`, đối chiếu từ
      `scl/DB_Alert.scl` + `python-bridge/main_bridge.py` của Đồ án 1, DB2, "Details view" đã
      xác nhận thật) — không bịa số cho 2 field này.
    - `e_stop_ok`/`thermal_relay_ok`/`short_circuit_ok`/`contactor_state` là **tag MỚI cho bài
      DOL/đảo chiều sao-tam giác của Đồ án 2, CHƯA tồn tại trong `.scl` thật** (Đồ án 1 chỉ mô
      phỏng kẹt băng tải/quá dòng/quá nhiệt, không có E-Stop/rơ-le nhiệt/contactor riêng). Offset
      tạm đặt `OFFSET_SAFETY_FLAGS=26` (nối tiếp sau byte cuối đã biết) — đánh dấu rõ TODO trong
      code, **PHẢI đối chiếu lại "Details view" thật trong TIA Portal sau khi hoàn thành việc sửa
      tay `DB_Alert.scl`** (mục 1 trong `agents/safety-tutoring/README.md`), không được coi đây
      là offset cuối cùng.
  - `app/main.py`: publish `lab/safety/status` mỗi 3s (`SAFETY_STATUS_INTERVAL_SECONDS`, cấu hình
    qua `.env`), subscribe `lab/safety/command`, `interlock_ok = e_stop_ok AND thermal_relay_ok
    AND short_circuit_ok` trước khi `close_contactor` (approve/reject kèm `reason` dạng
    `"e_stop_not_ok"`/`"thermal_relay_not_ok"`/`"short_circuit_not_ok"`); `open_contactor` luôn
    được phép (cắt điện là thao tác an toàn, không cần qua interlock). Alert `overcurrent`
    (>10.3A) / `overtemperature` (>80.5°C) chỉ publish một lần lúc **vừa chuyển sang vượt ngưỡng**
    (rising-edge, theo đúng triết lý chống spam của `main_bridge.py` Đồ án 1), kèm tự động
    `open_contactor` (`action_taken: "contactor_opened"`).
- **Test: `pytest tests/test_safety_agent.py` — PASS 5/5**, dùng Mosquitto thật đang chạy sẵn ở
  `localhost:1883` (KHÔNG mock MQTT, chỉ fake PLC qua `FakeSnap7Client` mô phỏng đúng byte-level
  offset/bit thật):
  1. `close_contactor` được approve khi đủ 3 điều kiện an toàn (round-trip MQTT thật, khớp
     `in_reply_to`).
  2. `close_contactor` bị reject kèm `reason="e_stop_not_ok"` khi E-Stop chưa OK, contactor không
     bị đóng.
  3. `open_contactor` luôn được approve kể cả khi rơ-le nhiệt chưa OK.
  4. Vượt ngưỡng quá dòng (11.0A) → publish đúng `lab/safety/alert`, tự cắt contactor.
  5. Không spam alert khi vẫn còn vượt ngưỡng qua nhiều chu kỳ liên tiếp (edge-trigger).
- **TODO còn lại (chặn bởi license PLCSIM Advanced, KHÔNG tự làm thay được):**
  - Mở TIA Portal, thêm tag `E_Stop_OK`/`Thermal_Relay_OK`/`Short_Circuit_OK`/`Contactor_State`/
    `Contactor_Cmd` vào `DB_Alert.scl` (bài DOL/sao-tam giác), compile + download qua PLCSIM
    Advanced (thao tác tay, không AI nào làm thay được) — **sau đó bắt buộc mở "Details view"
    (View > Extended) để lấy offset byte thật, sửa lại `OFFSET_SAFETY_FLAGS` và các `BIT_*` trong
    `app/plc/snap7_client.py` cho khớp 100%** (không được giữ nguyên số tạm `26`).
  - Test tích hợp thật với `SafetyPlcClient(client=None)` (dùng `snap7.client.Client()` thật) nối
    PLCSIM Advanced qua S7comm — chưa làm được, cần license.
  - Xác nhận `PLC_IP`/`PLC_RACK`/`PLC_SLOT`/`PLC_DB_NUMBER` thật trong `.env` (hiện để mặc định
    kế thừa Đồ án 1: `192.168.0.1`, rack 0, slot 1, DB2) khớp với cấu hình PLCSIM thật khi có.
  - Kiến trúc hiện mới hỗ trợ 1 bàn thực hành / 1 `SafetyPlcClient` / 1 DB — khi có nhiều bàn thật
    cần mở rộng sang mapping `table_id -> db_number` (chưa cần trong phạm vi demo hiện tại).
