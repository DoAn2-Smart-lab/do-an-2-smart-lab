# Master Orchestrator Agent

Trạng thái: 🟢 Ngày 2 — `wait_response` cho nhánh `safety_tutoring` giờ CHỜ ACK THẬT trên
`lab/safety/command` (khớp `in_reply_to`, timeout 3s), `table_id`/`action` đã được tách riêng
khỏi câu nói thô trong `classifier.py`. Đã test lại 4/4 kịch bản Intent Recognition với thư viện
+ Mosquitto broker thật, không mock. Còn lại: `lab_data`/`power_load` vẫn là fire-and-forget
(chưa chờ kết quả thật), Voice vẫn để dành Tuần 12.

## Cấu trúc đã tạo
```
app/
├── main.py            # FastAPI entrypoint — startup subscribe đủ SUBSCRIBE_TOPICS
├── api/chat.py         # POST /chat — chạy LangGraph trong thread pool (asyncio.to_thread)
├── graph/              # state.py (+table_id/action/safety_request_message_id) + nodes.py + builder.py
├── intent/classifier.py # rule-based + trích table_id (regex "B0n") + action, bỏ dấu trước khi so khớp
├── mqtt/               # topics.py (8 topic + QoS/retain đúng schema Ngày 2),
│                       # client.py (wrapper paho-mqtt, publish đúng QoS/retain, wait_for_ack())
└── models/schemas.py    # Pydantic: message_id/timestamp(+07:00)/source_agent + SafetyCommandRequest/Ack
tests/test_intent_classifier.py  # 4 kịch bản — đã chạy pass bằng thư viện thật (Python 3.14)
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
