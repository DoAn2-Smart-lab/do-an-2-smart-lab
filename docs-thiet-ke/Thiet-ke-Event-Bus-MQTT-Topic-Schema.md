# THIẾT KẾ EVENT BUS / MQTT TOPIC SCHEMA (dự thảo Tuần 2)

> Bản nháp để nhóm chốt trước khi viết code ở Claude Code/VSCode. Có thể chỉnh sửa trực tiếp file
> này ở đây (Cowork) trước, khi đã thống nhất thì mới sang VSCode implement.

## Nguyên tắc
- Broker: Mosquitto chạy local (`localhost:1883` khi phát triển).
- Payload: JSON, luôn có `timestamp` (ISO 8601) và `source_agent`.
- Master Orchestrator KHÔNG điều khiển PLC trực tiếp — mọi lệnh liên quan an toàn phải đi qua
  topic của Safety Agent, Safety Agent là nơi DUY NHẤT publish lệnh đóng/cắt contactor.

## Danh sách topic (nháp)

| Topic | Publisher | Subscriber | Payload mẫu | Ý nghĩa |
|---|---|---|---|---|
| `lab/orchestrator/intent` | Master Orchestrator | Safety / LabData / Power Agent | `{"intent": "start_dol_practice", "user": "sv001", "timestamp": "..."}` | Ý định đã nhận diện từ Chat/Voice |
| `lab/safety/status` | Safety Agent | Master Orchestrator | `{"e_stop_ok": true, "thermal_relay_ok": true, "short_circuit_ok": true, "timestamp": "..."}` | Trạng thái các điều kiện an toàn đọc từ PLC |
| `lab/safety/command` | Safety Agent | (nội bộ → PLC qua python-snap7) | `{"action": "close_contactor", "table_id": "B03", "approved": true}` | Lệnh cấp nguồn — CHỈ Safety Agent được publish |
| `lab/safety/alert` | Safety Agent | Master Orchestrator, Telegram bridge | `{"fault_type": "overcurrent", "value": 10.5, "table_id": "B03"}` | Cảnh báo sự cố, kế thừa cơ chế `_AtFault` của Đồ án 1 |
| `lab/data/query` | Master Orchestrator | Lab Data Management Agent | `{"query": "device_info", "device_id": "PLC-01"}` | Truy vấn CSDL thiết bị/lịch thực hành |
| `lab/data/result` | Lab Data Management Agent | Master Orchestrator | `{"device_id": "PLC-01", "spec": {...}}` | Kết quả truy vấn |
| `lab/power/status` | Power & Load Management Agent | Master Orchestrator, Lab Data Agent | `{"total_kw": 4.2, "peak_forecast_kw": 6.0, "lights": "on", "fans": "on"}` | Trạng thái năng lượng toàn phòng |
| `lab/power/command` | Master Orchestrator | Power & Load Management Agent | `{"action": "turn_off", "zone": "B03"}` | Lệnh điều khiển đèn/quạt (không liên quan an toàn cấp điện động cơ) |

## Việc cần chốt ở Tuần 2 (làm ở VSCode/Claude Code khi implement)
- Định nghĩa JSON Schema chính thức cho từng topic (dùng `pydantic` model).
- Viết publisher/subscriber mẫu cho từng Agent bằng `paho-mqtt`.
- Test bằng `mosquitto_sub`/`mosquitto_pub` trước khi tích hợp vào LangGraph.
