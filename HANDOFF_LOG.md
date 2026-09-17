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
- [ ] Cài đặt môi trường: LangGraph, FastAPI AsyncIO, MQTT broker (Mosquitto).
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

## Việc tiếp theo (Tuần 2 trở đi)
- [ ] Chốt chính thức JSON Schema của từng topic (hiện đang là bản nháp trong file .md) cùng
  người phụ trách Lab Data + Power Agent trước khi 2 agent đó bắt đầu code, để `models/schemas.py`
  không phải sửa lại nhiều lần.
- [ ] Cài Mosquitto, chạy thử `mosquitto_sub`/`mosquitto_pub` để test end-to-end với skeleton
  Master Orchestrator trước khi có Safety/LabData/Power Agent thật.
