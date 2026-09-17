# TỔNG HỢP Ý TƯỞNG (trao đổi nhóm qua Zalo) VÀ ĐỐI CHIẾU VỚI ĐỊNH HƯỚNG GVHD

> File này gom lại các ý Thành Phát liệt kê trong đoạn chat Zalo ngày 17/09/2026, sắp xếp lại theo
> đúng 4 Agent đã chốt trong đề cương, đối chiếu xem ý nào đã nằm trong phạm vi Đồ án 2 bắt buộc,
> ý nào là mở rộng/tầm nhìn xa hơn — để nhóm không lạc hướng khỏi mốc nghiệm thu.

---

## 1. Các ý đã liệt kê (nguyên văn, gom nhóm lại)

| # | Ý gốc trong Zalo | Thuộc Agent nào | Mức độ so với đề cương đã nộp |
|---|---|---|---|
| 1 | "Trợ lý AI ptn thông minh" | Master Orchestrator Agent (giao diện chung) | ✅ Đã có trong đề cương — đây chính là Master Orchestrator |
| 2 | "Quản lí toàn bộ dữ liệu" | Lab Data Management Agent | ✅ Đã có — CSDL thiết bị/lịch thực hành/mượn trả |
| 3 | "AI chạy toàn bộ trên máy" | Hạ tầng chung (không thuộc riêng Agent nào) | ⚠️ MỞ RỘNG — đề cương chưa ràng buộc chạy Local; xem mục 2 bên dưới |
| 4 | "Toàn bộ thiết bị ptn" | Lab Data Management Agent + Power & Load Agent | ⚠️ MỞ RỘNG phạm vi giám sát — đề cương mới tập trung băng tải/bàn thực hành DOL kế thừa Đồ án 1 |
| 5 | "Thông số chi tiết từng thiết bị (CB, PLC,...)" | Lab Data Management Agent | ✅ Đúng hướng — cần thiết kế CSDL thiết bị chi tiết hơn (xem mục 3) |
| 6 | "Tích hợp điều khiển thiết bị cả phòng" | Power & Load Management Agent | ✅ Đã có trong đề cương (đèn, quạt, công suất) — có thể mở rộng thêm |
| 7 | "Jarvis Chat + voice" | Master Orchestrator Agent (giao diện) | ⚠️ CẢNH BÁO — GVHD đã nói rõ KHÔNG được sao chép mẫu Jarvis-Desktop-Voice-Assistant, chỉ lấy ý tưởng "có Chat + Voice", kiến trúc phải dùng LangGraph/FastAPI/Event Bus |
| 8 | "Up file mới lên" | Lab Data Management Agent | ⚠️ MỞ RỘNG — tính năng upload tài liệu mới (bản vẽ, SOP, thông số thiết bị) vào hệ thống |
| 9 | "Vẽ trên CAD/Inventor" | Ngoài phạm vi 4 Agent — thuộc hướng Digital Twin | ⚠️ MỞ RỘNG LỚN — đây là hướng của **Nhóm 03** (lò sấy), không phải yêu cầu bắt buộc của Nhóm 05 |
| 10 | "Claude ra lệnh thông qua MCP (Model Context Protocol), gửi bản vẽ qua CAD" | Digital Twin Co-Pilot | ⚠️ MỞ RỘNG LỚN — xem mục 4 |
| 11 | "Digital Twin" | Tầm nhìn tương lai (đã ghi trong tài liệu GVHD, mục 3.1 Nhóm 05) | ⚠️ Đúng là hướng tương lai được phép, nhưng KHÔNG phải sản phẩm cốt lõi cần nộp Đồ án 2 |

---

## 2. Về ý "AI chạy toàn bộ trên máy" (Local AI)

Tài liệu định hướng của thầy Trần Trung Khánh khuyến khích **Local SLM (Small Language Model)**
chạy qua Ollama/vLLM cho Nhóm 01 (bảo trì dự đoán động cơ) — lý do: tránh phụ thuộc API ngoài,
kiểm soát chi phí, phù hợp môi trường lab không có Internet ổn định.

**Khuyến nghị cho Nhóm 05:** Master Orchestrator Agent nên dùng một SLM local nhỏ
(`Qwen2.5-3B-Instruct` hoặc `Llama-3.2-3B-Instruct`, quantized 4-bit GGUF) làm bộ não
Intent Recognition + Tutoring, thay vì gọi API Claude/GPT trực tuyến liên tục. Điều này vừa
đúng tinh thần "AI chạy toàn bộ trên máy" nhóm đề xuất, vừa khớp với tiêu chí "Ứng dụng AI có
kiểm soát" mà GVHD nhấn mạnh ở phần mở đầu tài liệu chung.

Việc dùng Claude qua MCP (ý #10) vẫn có thể giữ lại như một **công cụ hỗ trợ lập trình/thiết kế
trong quá trình PHÁT TRIỂN** (ví dụ: nhờ Claude sinh code, viết tài liệu), nhưng **không nên là
thành phần chạy trong hệ thống lab thực tế lúc vận hành** — vì phụ thuộc Internet và tài khoản
Anthropic, không phù hợp với tiêu chí "AI cục bộ" và cũng không phải yêu cầu chính thức từ GVHD.

---

## 3. Về "Toàn bộ thiết bị ptn" + "Thông số chi tiết từng thiết bị"

Đây là mở rộng hợp lý cho Lab Data Management Agent. Đề xuất bổ sung vào thiết kế CSDL (tuần 10
trong kế hoạch): mỗi thiết bị (CB, PLC, contactor, rơ-le nhiệt, biến tần...) có 1 bản ghi gồm:
mã thiết bị, loại, thông số kỹ thuật (dòng định mức, điện áp, công suất), vị trí lắp đặt, ngày
kiểm định gần nhất, trạng thái (đang dùng/hỏng/bảo trì). Đây chính là nền dữ liệu để Safety Agent
tra cứu khi hướng dẫn sinh viên ("rơ-le nhiệt F2 có dòng chỉnh định bao nhiêu?").

---

## 4. Về "Vẽ trên CAD/Inventor" + "Claude MCP gửi bản vẽ qua CAD" + "Digital Twin"

Đây là ý tưởng **rất giống hướng của Nhóm 03** (lò sấy thông minh — mục 2.1 tài liệu GVHD): dùng
Claude MCP kết nối Autodesk Inventor để Co-Pilot đọc dữ liệu quá trình và gợi ý chỉnh sửa mô hình
3D. Tài liệu GVHD **cũng ghi rõ đây là "Tầm nhìn tương lai"** cho Nhóm 05 (mục 3.1: *"Nâng cấp
giao diện thành Bản sao kỹ thuật số 3D hiển thị trực quan toàn bộ phòng lab theo thời gian
thực"*), tức là được phép làm nhưng **không phải tiêu chí nghiệm thu bắt buộc của Đồ án 2**.

**Khuyến nghị:** KHÔNG đưa CAD/Digital Twin 3D vào phạm vi nghiệm thu Đồ án 2 (rủi ro trễ tiến độ
rất cao vì đã có đủ việc với 4 Agent + Safety Interlock). Thay vào đó:
- Ghi nhận ý tưởng này vào phần "Đề xuất phát triển Khóa luận tốt nghiệp" của báo cáo Đồ án 2.
- Nếu muốn thử nghiệm sớm, chỉ làm ở mức proof-of-concept nhỏ, tách riêng khỏi lịch trình 15 tuần
  chính (ví dụ: 1 bản vẽ mặt bằng phòng lab tĩnh trong Inventor, gắn cờ trạng thái đèn/quạt đọc từ
  PLC — chưa cần Claude MCP điều khiển ngược).

---

## 5. Việc cần làm tiếp theo (đã cập nhật theo các ý trên)

1. **Không đổi phạm vi nghiệm thu Đồ án 2** đã ghi trong đề cương (4 Agent + Safety Interlock) —
   giữ đúng tiến độ 15 tuần đã nộp thầy.
2. Bổ sung vào thiết kế Lab Data Management Agent (tuần 10): CSDL thiết bị chi tiết (mục 3) +
   tính năng upload tài liệu mới (ý #8).
3. Chốt sớm (tuần 3-4, khi dựng Master Orchestrator): dùng SLM local (Qwen2.5-3B/Llama-3.2-3B)
   thay vì gọi Claude API trực tuyến cho phần vận hành thật của hệ thống.
4. Ghi ý tưởng CAD/Inventor/Digital Twin + Claude MCP vào mục "Hướng phát triển Khóa luận tốt
   nghiệp" trong báo cáo Đồ án 2, không đưa vào kế hoạch 15 tuần.
5. Trao đổi lại với GVHD (thầy Trần Trung Khánh) để xác nhận việc KHÔNG mở rộng sang CAD/Digital
   Twin ở giai đoạn Đồ án 2 — tránh trường hợp thầy đã ngầm kỳ vọng thêm phần này.

---

*File tổng hợp lúc 17/09/2026, dựa trên ảnh chụp đoạn chat Zalo nhóm (Thành Phát) và đối chiếu với
tài liệu "Định hướng chi tiết Đồ án 2..." của ThS. Trần Trung Khánh (ban hành 14/09/2026).*
