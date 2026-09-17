# Lab Data Management Agent

Trạng thái: 🔴 CHƯA VIẾT CODE — Tuần 10, thực hiện ở Claude Code/VSCode.

## Nhiệm vụ
- CSDL thiết bị (CB, PLC, contactor, rơ-le nhiệt, biến tần...) — mỗi bản ghi gồm mã thiết bị, loại,
  thông số kỹ thuật, vị trí, ngày kiểm định, trạng thái.
- Lịch thực hành, tình trạng bàn thực hành, chu kỳ kiểm định, lịch sử mượn/trả.
- Tính năng upload tài liệu mới (bản vẽ, SOP) — theo ý tưởng nhóm trao đổi qua Zalo.

## Công nghệ dự kiến
SQLAlchemy + SQLite (giai đoạn đầu) hoặc PostgreSQL, expose qua FastAPI, subscribe MQTT topic
`lab/data/query`, publish `lab/data/result`.

## Việc cần làm khi bắt đầu (ở VSCode)
1. Thiết kế schema CSDL (bảng `devices`, `practice_schedule`, `borrow_history`, `documents`).
2. Viết API CRUD cơ bản.
3. Kết nối vào Event Bus, test bằng 3 truy vấn mẫu (tiêu chí nghiệm thu #3 trong đề cương).
