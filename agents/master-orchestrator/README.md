# Master Orchestrator Agent

Trạng thái: 🟡 KHUNG SƯỜN (skeleton) đã tạo bằng Claude Code — chạy được end-to-end với bộ phân
loại rule-based (4/4 kịch bản test đã pass), nhưng **`wait_response` chưa chờ phản hồi MQTT thật**
và tham số lệnh (tên bàn thực hành, zone, action...) chưa được tách từ câu nói thật. Việc còn lại
vẫn đúng lịch Tuần 3-4.

## Cấu trúc đã tạo
```
app/
├── main.py            # FastAPI entrypoint (uvicorn app.main:app --reload)
├── api/chat.py         # POST /chat — chạy LangGraph, trả reply_text
├── graph/              # state.py + nodes.py + builder.py (5 node đúng thứ tự bên dưới)
├── intent/classifier.py # rule-based, bỏ dấu trước khi so khớp — TODO: thay bằng SLM local
├── mqtt/               # topics.py (đúng docs-thiet-ke/Thiet-ke-Event-Bus-MQTT-Topic-Schema.md),
│                       # client.py (wrapper paho-mqtt, chặn publish ngoài PUBLISH_TOPICS)
└── models/schemas.py    # Pydantic khớp đúng payload mẫu trong file schema
tests/test_intent_classifier.py  # 4 kịch bản — đã chạy pass bằng python 3.14
```

## Nhiệm vụ
- Nhận lệnh từ Chat (trước) và Voice (Tuần 12) từ người dùng (giảng viên/KTV/sinh viên).
- Intent Recognition: phân loại lệnh thành 1 trong các nhóm ứng với 3 sub-agent.
- Định tuyến (routing) yêu cầu qua MQTT topic `lab/orchestrator/intent`.
- KHÔNG được phép gọi PLC trực tiếp — mọi việc liên quan an toàn phải qua Safety Agent.

## Công nghệ dự kiến
LangGraph (state machine) + FastAPI AsyncIO (nhận request từ giao diện Chat).

## Việc cần làm khi bắt đầu (ở VSCode)
1. Định nghĩa state graph LangGraph: node `receive_input` → `classify_intent` → `route_to_agent`
   → `wait_response` → `reply_user`.
2. Viết bộ phân loại intent tối thiểu (rule-based hoặc SLM local — xem
   `docs-thiet-ke/Tong-hop-y-tuong-Zalo-va-dinh-huong-tiep-theo.md` mục 2) cho 4 nhóm lệnh mẫu.
3. Test bằng 4 kịch bản lệnh khác nhau (tiêu chí nghiệm thu #1 trong đề cương).
