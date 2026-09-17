# Power & Load Management Agent

Trạng thái: 🔴 CHƯA VIẾT CODE — Tuần 11, thực hiện ở Claude Code/VSCode.

## Nhiệm vụ
- Giám sát đóng/cắt chiếu sáng, quạt thông gió.
- Đo công suất tiêu thụ toàn lab (mô phỏng hoặc cảm biến thật nếu có điều kiện).
- Dự báo phụ tải đỉnh (moving average/regression đơn giản), đề xuất tiết kiệm năng lượng.

## Việc cần làm khi bắt đầu (ở VSCode)
1. Mô phỏng dữ liệu công suất nếu chưa có cảm biến thật (tham khảo cách tạo dữ liệu mô phỏng bằng
   TON/LCG đã dùng ở Đồ án 1).
2. Viết thuật toán dự báo phụ tải đỉnh đơn giản.
3. Publish trạng thái lên `lab/power/status`, subscribe lệnh điều khiển `lab/power/command`.
4. Kiểm thử cảnh báo khi vượt phụ tải đỉnh giả định (tiêu chí nghiệm thu #4 trong đề cương).
