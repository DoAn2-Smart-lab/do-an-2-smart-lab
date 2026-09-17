# KHI NÀO DÙNG CLAUDE (chat này) VÀ KHI NÀO DÙNG CLAUDE CODE TRÊN VSCODE?

> Mục đích: tránh nhầm lẫn — có việc nên làm ở đây (lên kế hoạch, soạn tài liệu, tổ chức file),
> có việc BẮT BUỘC phải làm bằng Claude Code chạy trong VSCode trên máy tính cá nhân (vì cần
> TIA Portal, PLCSIM Advanced, kết nối PLC thật, chạy server local, hoặc thao tác git). Bảng dưới
> đánh dấu rõ theo từng tuần trong kế hoạch 15 tuần đã nộp GVHD.

## Nguyên tắc phân biệt

| Đặc điểm công việc | Làm ở đâu |
|---|---|
| Soạn/sửa tài liệu (đề cương, báo cáo, worksheet), tổ chức thư mục, tổng hợp ý tưởng | Ở đây (Claude/Cowork) |
| Viết code Python/FastAPI/LangGraph, chạy thử server, cài MQTT broker, debug lỗi runtime | **Claude Code trên VSCode** |
| Thao tác TIA Portal V20, PLCSIM Advanced, Watch Table, download chương trình xuống PLC | Bắt buộc làm tay trên máy (Windows), Claude Code chỉ hỗ trợ viết/xem code `.scl`, KHÔNG thể tự thao tác TIA Portal |
| Kết nối PLC thật tại phòng lab, đo tín hiệu thực | Tại lab, không AI nào thay thế được |
| `git commit`, quản lý version code | **Claude Code trên VSCode** (đã có sẵn thư mục dự án ở máy) |
| Đọc/phân tích lại code cũ đã viết, refactor | **Claude Code trên VSCode** (đọc trực tiếp toàn bộ repo, nhanh và chính xác hơn dán từng đoạn vào chat) |

**Lý do kỹ thuật:** phiên làm việc này chạy trên máy chủ đám mây, không thể cài TIA Portal (phần
mềm Windows có bản quyền), không kết nối được tới PLC/PLCSIM Advanced đang chạy trên máy cá nhân
hoặc mạng phòng lab, và không giữ được trạng thái server/process chạy nền qua nhiều ngày như
VSCode có thể. Vì vậy toàn bộ phần "code thật + chạy thật" của Đồ án 2 phải làm bằng Claude Code
cài trực tiếp trong VSCode trên máy bạn.

---

## Cắm cờ theo từng tuần (đối chiếu kế hoạch 15 tuần trong đề cương)

| Tuần | Nội dung | Vị trí thực hiện |
|---|---|---|
| 1 | Nộp đề cương; cài LangGraph/FastAPI/MQTT broker; rà soát code Đồ án 1 | 🟡 Đề cương: ở đây. 🔴 **Cài đặt môi trường + rà soát code: chuyển sang Claude Code/VSCode ngay từ tuần này** |
| 2 | Chốt sơ đồ khối, giao thức message giữa Agent | 🟡 Có thể thảo luận/vẽ sơ đồ ở đây, nhưng file schema JSON/code mẫu nên tạo bằng 🔴 Claude Code |
| 3–4 | Xây Master Orchestrator Agent (LangGraph, Intent Recognition) | 🔴 **Toàn bộ ở Claude Code/VSCode** — đây là code chạy thật |
| 5–6 | Safety Agent phần 1: mở rộng Data Block PLC, đọc trạng thái an toàn | 🔴 Sửa file `.scl` bằng Claude Code, nhưng ⚠️ **compile + download xuống PLCSIM Advanced phải làm tay trong TIA Portal** — Claude Code không thao tác được TIA Portal |
| 7 | Demo giữa kỳ, báo cáo tiến độ | 🟡 Viết báo cáo tiến độ có thể làm ở đây |
| 8–9 | Safety Agent phần 2: khóa liên động, đo thời gian phản hồi | 🔴 Claude Code/VSCode |
| 10 | Lab Data Management Agent: CSDL, API | 🔴 Claude Code/VSCode |
| 11 | Power & Load Management Agent | 🔴 Claude Code/VSCode |
| 12 | Tích hợp giọng nói (Speech-to-Text) | 🔴 Claude Code/VSCode |
| 13 | Tích hợp toàn hệ thống, kiểm thử, thu số liệu | 🔴 Claude Code/VSCode (chạy thật để lấy số liệu) |
| 14 | Viết báo cáo Đồ án 2 + bản thảo bài báo khoa học | 🟡 **Quay lại đây** — tổng hợp số liệu đã đo được từ Claude Code thành báo cáo Word hoàn chỉnh |
| 15 | Hoàn thiện, quay video demo, nghiệm thu | 🟡 Slide/báo cáo ở đây; 🔴 quay video demo hệ thống chạy thật cần làm tại máy/lab |

**Tóm gọn:** từ tuần 3 trở đi, phần lớn công việc là code thật — bạn nên mở VSCode, cài
Claude Code, và làm việc trực tiếp trong thư mục `Do-an-2-he-thong-da-agent-ptn-thong-minh/` (đã
gửi ở bước trước). Quay lại đây khi cần: soạn/chỉnh tài liệu Word, tổng hợp báo cáo, lên kế hoạch,
hoặc nhờ phân tích/định hướng tổng thể.

---

## Việc cần làm ngay bây giờ (Tuần 1, phần có thể chuẩn bị trước khi mở VSCode)

1. Đã xong: đề cương, tổ chức thư mục, đối chiếu ý tưởng Zalo (xem các file khác trong
   `docs-thiet-ke/`).
2. 🔴 **Việc tiếp theo phải chuyển sang Claude Code/VSCode:**
   - Mở thư mục `Do-an-2-he-thong-da-agent-ptn-thong-minh/` trong VSCode.
   - Cài Python 3.11+, tạo virtualenv, cài `langgraph`, `fastapi`, `uvicorn`, `paho-mqtt`.
   - Cài MQTT broker (Mosquitto) chạy local để test Event Bus giữa các Agent.
   - Copy/liên kết lại code Đồ án 1 (`mo-phong-s7-1500-smart-lab/scl/`,
     `mo-phong-s7-1500-smart-lab/python-bridge/`) vào tham chiếu, để Safety Agent tái sử dụng đúng
     logic `python-snap7` đã chạy ổn định.
   - Khởi tạo `git init` cho thư mục Đồ án 2 (nếu chưa có), commit lần đầu.

Khi bạn mở VSCode và bắt đầu phần code thật, hãy nói với tôi (trong phiên Claude Code ở đó) đúng
ngữ cảnh: "đây là Đồ án 2, kế thừa Đồ án 1 tại thư mục X, đề cương đã chốt tại Y" — có thể copy
nguyên câu lệnh ngữ cảnh mà tôi đã đưa ở bước trước, hoặc trỏ thẳng tới file `PROJECT_CONTEXT.md`.
