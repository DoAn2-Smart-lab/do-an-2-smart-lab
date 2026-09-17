# README — Đồ án 2: Hệ thống Đa Agent quản trị Phòng thí nghiệm thông minh

## Đọc trước khi bắt đầu
1. `PROJECT_CONTEXT.md` — tổng quan dự án, cấu trúc thư mục, trạng thái hiện tại.
2. `docs-thiet-ke/De-cuong-chi-tiet-Do-an-2-Nhom05.docx` — đề cương đã nộp GVHD (mục tiêu, sơ đồ
   khối kiến trúc, phân công, kế hoạch 15 tuần, tiêu chí nghiệm thu).
3. `docs-thiet-ke/Tong-hop-y-tuong-Zalo-va-dinh-huong-tiep-theo.md` — đối chiếu ý tưởng nhóm với
   phạm vi đã chốt, tránh lạc hướng khỏi mốc nghiệm thu.

## Liên kết với Đồ án 1
Thư mục anh em `mo-phong-s7-1500-smart-lab/` (Đồ án 1, đã nộp) chứa toàn bộ code PLC + Python gốc
được kế thừa. Khi mở rộng Data Block hoặc lớp giao tiếp PLC cho Đồ án 2, luôn đối chiếu lại file
`TONG-HOP-TIEN-DO-VA-KET-QUA.md` trong thư mục đó để không phá vỡ logic đã kiểm thử thành công.

## Quy trình làm việc đề xuất
1. Mỗi tuần cập nhật `HANDOFF_LOG.md` với việc đã làm/vướng mắc.
2. Code từng Agent đặt trong `agents/<ten-agent>/`, có README riêng nếu cần.
3. Không xóa file cũ — chuyển vào `archive-deprecated/` khi thay thế.
