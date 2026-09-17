# PROJECT_CONTEXT — Hệ thống Đa Agent quản trị Phòng thí nghiệm Điện công nghiệp thông minh (Đồ án 2)

## Mục tiêu
Chuyển đổi từ mô hình giám sát/cảnh báo đơn luồng của Đồ án 1 (PLC ảo S7-1500 → Python → Telegram)
sang kiến trúc **Hệ thống Đa Agent (Multi-Agent System)** quản trị toàn bộ phòng thí nghiệm Điện
công nghiệp, có giao diện Chat/Voice, định vị học thuật "Smart Educational Engineering Laboratory
with Agentic Safety Interlocks" (Education 5.0).

**Nhóm 05** — Lữ Phan Thành Phát (CNDD2311025), Trần Lê Tuấn (CNDD2311012).
GVHD Đồ án 1: ThS. Lê Quốc Khương. GVHD định hướng Đồ án 2/NCKH/KLTN: ThS. Trần Trung Khánh.

## Phạm vi Đồ án 2 (đã nộp đề cương — xem `docs-thiet-ke/`)
4 Agent cốt lõi: Master Orchestrator, Safety & Practical Tutoring, Lab Data Management,
Power & Load Management — giao tiếp qua Event Bus/MQTT, không dùng Digital Twin 3D/CAD (để dành
cho Khóa luận tốt nghiệp — xem lý do ở `docs-thiet-ke/Tong-hop-y-tuong-Zalo-va-dinh-huong-tiep-theo.md`).

## Kế thừa từ Đồ án 1
Dự án mô phỏng gốc nằm ở thư mục anh em `mo-phong-s7-1500-smart-lab/` (Đồ án 1) — các thành phần
tái sử dụng trực tiếp:
- `scl/DB_ConveyorMonitor.scl`, `scl/DB_Alert.scl`, `scl/FB_SimulateConveyor.scl` — nền tảng PLC.
- `python-bridge/main_bridge.py` (python-snap7, S7comm port 102) — nâng cấp thành lớp giao tiếp
  PLC dùng chung cho Safety & Practical Tutoring Agent.
- Kênh Telegram Bot — giữ làm cảnh báo dự phòng song song Chat/Voice.

## Cấu trúc thư mục
```
Do-an-2-he-thong-da-agent-ptn-thong-minh/
├── PROJECT_CONTEXT.md              <- đọc đầu tiên (người + AI)
├── README.md                        <- hướng dẫn nhanh
├── HANDOFF_LOG.md                   <- nhật ký tiến độ theo tuần
├── docs-thiet-ke/                   <- đề cương, worksheet thiết kế, tổng hợp ý tưởng
│   ├── De-cuong-chi-tiet-Do-an-2-Nhom05.docx
│   └── Tong-hop-y-tuong-Zalo-va-dinh-huong-tiep-theo.md
├── scl/                              <- code PLC mở rộng (DB thiết bị chi tiết, bài DOL/sao-tam giác)
├── python-bridge/                    <- lớp giao tiếp PLC dùng chung cho Safety Agent
├── agents/                           <- code 4 Agent (Orchestrator, Safety, Lab Data, Power)
├── test-harness/                     <- script test tay từng Agent
├── data-logs/                        <- log/CSV/DB sinh ra khi chạy
└── archive-deprecated/               <- version cũ, không xóa
```

## Quy ước đặt tên file mới
- Đề cương, worksheet, tổng hợp ý tưởng → `docs-thiet-ke/`
- Code PLC (.scl) → `scl/`
- Code từng Agent → `agents/<ten-agent>/`
- Kết quả/log khi chạy → tự sinh vào `data-logs/`
- Version cũ không dùng nữa → `archive-deprecated/`, không xóa
- Tên file/thư mục không dấu, không khoảng trắng (dùng `-`/`_`)

## Trạng thái hiện tại
- [2026-09-17] Đã nộp đề cương chi tiết Đồ án 2 cho GVHD (đúng hạn 1 tuần kể từ 14/09/2026).
- [2026-09-17] Đã tổng hợp và phân loại các ý tưởng nhóm trao đổi qua Zalo, đối chiếu với phạm vi
  đã chốt — xem `docs-thiet-ke/Tong-hop-y-tuong-Zalo-va-dinh-huong-tiep-theo.md`.
- [2026-09-17] Đã soạn dự thảo Event Bus/MQTT topic schema (Tuần 2) — xem
  `docs-thiet-ke/Thiet-ke-Event-Bus-MQTT-Topic-Schema.md`.
- [2026-09-17] Đã dựng khung `requirements.txt` và README kế hoạch cho từng Agent trong `agents/`.
- [2026-09-17] Đã ghi rõ việc nào làm ở đây (Cowork), việc nào bắt buộc chuyển sang Claude Code
  trong VSCode — xem `docs-thiet-ke/Huong-dan-khi-nao-dung-Claude-Code-VSCode.md`.
- [ ] **Tiếp theo (chuyển sang Claude Code/VSCode ngay từ đây):** cài môi trường Python +
  LangGraph/FastAPI/MQTT broker, rà soát lại code Đồ án 1, bắt đầu code Master Orchestrator Agent
  (Tuần 3-4).
