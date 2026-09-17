# Safety & Practical Tutoring Agent

Trạng thái: 🔴 CHƯA VIẾT CODE — Tuần 5-9, thực hiện ở Claude Code/VSCode.
⚠️ Phần sửa `.scl` (Data Block PLC) cần compile + download qua TIA Portal (thao tác tay, không AI
nào làm thay được).

## Nhiệm vụ
- Hướng dẫn từng bước bài thực hành DOL, đảo chiều sao-tam giác.
- Đọc trạng thái an toàn từ PLC (ngắn mạch, rơ-le nhiệt, E-Stop) qua lớp kế thừa
  `python-snap7` của Đồ án 1 (`../../mo-phong-s7-1500-smart-lab/python-bridge/main_bridge.py`).
- Là nơi DUY NHẤT được phép publish lệnh đóng contactor (`lab/safety/command`).

## Việc cần làm khi bắt đầu (ở VSCode)
1. Mở lại `DB_ConveyorMonitor.scl` / `DB_Alert.scl` / `FB_SimulateConveyor.scl` của Đồ án 1, thêm
   tag mô phỏng bài DOL/sao-tam giác (contactor, rơ-le nhiệt, E-Stop) — sửa bằng Claude Code, rồi
   **tự tay mở TIA Portal để compile + download xuống PLCSIM Advanced**.
2. Viết lớp Python đọc các tag an toàn mới, publish lên `lab/safety/status`.
3. Viết logic: chỉ publish `close_contactor` khi cả 3 điều kiện an toàn đều `true`.
4. Kiểm thử bằng kịch bản giả lập lỗi (tái dùng cơ chế `Fault_Inject` của Đồ án 1).
