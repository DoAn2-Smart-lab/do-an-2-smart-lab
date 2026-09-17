# THIẾT KẾ EVENT BUS / MQTT TOPIC SCHEMA (bản chốt Ngày 2)

> Bản nháp Tuần 2 đã được rà soát và bổ sung đầy đủ: payload chi tiết field-by-field, QoS,
> retain flag, và cơ chế trả lời (ACK) để Master Orchestrator hết chờ (`wait_response`) khi
> gọi Safety Agent. Khi triển khai ở Claude Code/VSCode, dùng bản này làm nguồn cho
> `app/mqtt/topics.py` và `app/models/schemas.py`.

## Nguyên tắc
- Broker: Mosquitto chạy local (`localhost:1883` khi phát triển).
- Envelope chung cho MỌI message: luôn có `message_id` (UUID v4), `timestamp` (ISO 8601,
  có offset +07:00), `source_agent`. Phần dữ liệu riêng của từng topic nằm trong object gốc
  (không bọc thêm lớp `payload` để giữ đúng tinh thần bản nháp gốc — xem ví dụ bên dưới).
- Master Orchestrator KHÔNG điều khiển PLC trực tiếp — mọi lệnh liên quan an toàn phải đi qua
  Safety Agent, Safety Agent là nơi DUY NHẤT publish lệnh đóng/cắt contactor xuống PLC.
- Định danh vị trí dùng thống nhất `table_id` dạng `"B01"`..`"B0n"` (khớp PLC Đồ án 1), KHÔNG
  dùng `zone`/`table_3` để tránh lệch giữa các agent.
- QoS mặc định: 0 = tối đa 1 lần (best-effort, dữ liệu status tần suất cao); 1 = ít nhất 1 lần
  (lệnh điều khiển, kết quả truy vấn); 2 = đúng 1 lần (cảnh báo an toàn — không được mất, không
  được trùng).

## Danh sách topic (bản chốt)

### 1. `lab/orchestrator/intent`
- Publisher: Master Orchestrator | Subscriber: Safety / LabData / Power Agent
- QoS: 1 · Retain: false

```json
{
  "message_id": "uuid-v4",
  "timestamp": "2026-09-17T10:00:00+07:00",
  "source_agent": "master-orchestrator",
  "intent": "start_dol_practice",
  "user": "sv001",
  "table_id": "B03",
  "action": "power_on",
  "confidence": 0.92
}
```
Bổ sung so với nháp: tách rõ `table_id` và `action` khỏi câu lệnh thô (TODO trong code hiện
đang gộp chung, đây là chỗ cần sửa `app/intent/classifier.py`), thêm `confidence` để Safety
Agent có thể từ chối nếu độ tin cậy thấp.

### 2. `lab/safety/status`
- Publisher: Safety Agent | Subscriber: Master Orchestrator, LabData Agent
- QoS: 1 · Retain: **true** (agent mới subscribe phải đọc được trạng thái hiện tại ngay)

```json
{
  "message_id": "uuid-v4",
  "timestamp": "...",
  "source_agent": "safety-agent",
  "table_id": "B03",
  "e_stop_ok": true,
  "thermal_relay_ok": true,
  "short_circuit_ok": true,
  "contactor_state": "open",
  "current_A": 4.2,
  "temperature_C": 45.1
}
```
Publish định kỳ (đề xuất mỗi 2–5s) hoặc ngay khi có thay đổi trạng thái.

### 3. `lab/safety/command`
- Publisher: Master Orchestrator (**yêu cầu**) và Safety Agent (**thực thi + ACK**)
- QoS: 1 · Retain: false

Đây là chỗ nháp gốc chưa rõ: bản gốc ghi Safety Agent là publisher duy nhất xuống PLC, nhưng
không có kênh nào để Orchestrator *yêu cầu* Safety Agent hành động. Chốt lại thành 2 chiều trên
cùng topic, phân biệt bằng field `type`:

```json
// Orchestrator -> Safety Agent (yêu cầu)
{
  "message_id": "uuid-A",
  "timestamp": "...",
  "source_agent": "master-orchestrator",
  "type": "request",
  "table_id": "B03",
  "requested_action": "close_contactor"
}
```
```json
// Safety Agent -> Orchestrator (ACK/NACK, giải quyết wait_response)
{
  "message_id": "uuid-B",
  "in_reply_to": "uuid-A",
  "timestamp": "...",
  "source_agent": "safety-agent",
  "type": "ack",
  "table_id": "B03",
  "approved": true,
  "action": "close_contactor",
  "reason": null
}
```
`in_reply_to` = `message_id` của request tương ứng → Orchestrator dùng để match và thoát
`wait_response`. Timeout đề xuất: 3s không có ACK → Orchestrator coi là lỗi, báo người dùng.
`approved: false` kèm `reason` (VD `"e_stop_not_ok"`) khi Safety Agent từ chối lệnh.

### 4. `lab/safety/alert`
- Publisher: Safety Agent | Subscriber: Master Orchestrator, Telegram bridge
- QoS: **2** · Retain: false

```json
{
  "message_id": "uuid-v4",
  "timestamp": "...",
  "source_agent": "safety-agent",
  "table_id": "B03",
  "fault_type": "overcurrent",
  "value": 10.5,
  "threshold": 10.3,
  "severity": "critical",
  "action_taken": "contactor_opened"
}
```
`fault_type` kế thừa đúng 3 loại lỗi của Đồ án 1: `"conveyor_jam" | "overcurrent" |
"overtemperature"`.

### 5. `lab/data/query`
- Publisher: Master Orchestrator | Subscriber: Lab Data Management Agent
- QoS: 1 · Retain: false

```json
{
  "message_id": "uuid-v4",
  "timestamp": "...",
  "source_agent": "master-orchestrator",
  "query": "device_info",
  "device_id": "PLC-01",
  "filters": { "date": "2026-09-17" }
}
```

### 6. `lab/data/result`
- Publisher: Lab Data Management Agent | Subscriber: Master Orchestrator
- QoS: 1 · Retain: false

```json
{
  "message_id": "uuid-v4",
  "in_reply_to": "uuid của query tương ứng",
  "timestamp": "...",
  "source_agent": "lab-data-agent",
  "device_id": "PLC-01",
  "status": "ok",
  "spec": {}
}
```
Thêm `in_reply_to` và `status` (`"ok" | "not_found" | "error"`) — nháp gốc chưa có, cần để
Orchestrator biết truy vấn thất bại hay thành công.

### 7. `lab/power/status`
- Publisher: Power & Load Management Agent | Subscriber: Master Orchestrator, LabData Agent
- QoS: 0 · Retain: **true**

```json
{
  "message_id": "uuid-v4",
  "timestamp": "...",
  "source_agent": "power-agent",
  "total_kw": 4.2,
  "peak_forecast_kw": 6.0,
  "forecast_horizon_min": 30,
  "lights": "on",
  "fans": "on"
}
```

### 8. `lab/power/command`
- Publisher: Master Orchestrator | Subscriber: Power & Load Management Agent
- QoS: 1 · Retain: false

```json
{
  "message_id": "uuid-v4",
  "timestamp": "...",
  "source_agent": "master-orchestrator",
  "action": "turn_off",
  "table_id": "B03",
  "reason": "peak_forecast_exceeded"
}
```
Không liên quan an toàn cấp điện động cơ (đèn/quạt) — không đi qua Safety Agent.

## Việc cần chốt ở Tuần 2 (làm ở VSCode/Claude Code khi implement)
- Định nghĩa JSON Schema chính thức cho từng topic (dùng `pydantic` model) — dựa trên các ví dụ
  ở trên, đưa vào `app/models/schemas.py`.
- Viết publisher/subscriber mẫu cho từng Agent bằng `paho-mqtt`, đặt tên topic tập trung ở
  `app/mqtt/topics.py`.
- Implement cơ chế `in_reply_to` + timeout 3s cho `lab/safety/command` để thay thế
  `wait_response` đang chờ trong code Orchestrator.
- Sửa `app/intent/classifier.py` để tách `table_id`/`action` khỏi `raw_text`.
- Test bằng `mosquitto_sub`/`mosquitto_pub` trước khi tích hợp vào LangGraph.
