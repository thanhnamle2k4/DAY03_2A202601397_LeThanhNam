# 📋 SỔ TAY PHÂN CÔNG & CHECKLIST THỰC HÀNH (ZERO-CONFLICT WORKFLOW)

> 💡 **Hướng dẫn**: Mỗi thành viên mở đúng file được phân công trong thư mục dự án và thực hiện checklist theo từng Mốc.

---

## 👥 1. BẢNG PHÂN VAI & FILE ĐẢM NHẬN

| Vai trò (Role)                               | File đảm nhận           | Nhiệm vụ chính                                                                                          | Người đảm nhận  |
| :-------------------------------------------- | :------------------------- | :--------------------------------------------------------------------------------------------------------- | :------------------- |
| **Role 1: Product Architect**           | `config/test_cases.json` | Định hướng bài toán & soạn bộ câu test case                                                       | Nguyễn Phương Nam |
| **Role 2: Tool Engineer**               | `src/tools.py`           | Định nghĩa các công cụ (Tools) cho Agent                                                             | Chu Phú Thành      |
| **Role 3: Prompt Engineer**             | `src/prompts.py`         | Viết ReAct System Prompt & phanh Guardrails                                                               | Phạm Thế Trung     |
| **Role 4: Core Developer / Integrator** | `src/app.py`             | **Đầu mối kéo code/file của nhóm (`git pull`), Vibe Code lắp ráp thành App hoàn chỉnh** | Lê Thành Nam       |
| **Role 5: Observability**               | `docs/trace_eval.md`     | Lập bảng Scoring Matrix & Soi nhật ký Trace Log                                                        | Vũ Thành Dương   |

*Note: Nếu nhóm 6 người, Role 5 tách thành 5A (Trace Analyst) và 5B (Flowchart Architect).*

> 🌟 **VAI TRÒ NÒNG NỐT CỦA ROLE 4 (ĐẦU MỐI LẮP RÁP APP HOÀN CHỈNH)**:
>
> - **Role 4** đóng vai trò là **Tổ trưởng Lắp ráp**: Sau khi các bạn Role 1, 2, 3 đẩy file lên Git, **Role 4 sẽ gõ `git pull`** để gom toàn bộ dữ liệu về máy.
> - **Role 4** sau đó dùng AI (Vibe Code) để kết nối `tools.py`, `prompts.py`, `test_cases.json` vào file `src/app.py`, biến các mảnh ghép thành **một Ứng dụng AI Agent hoàn chỉnh** cho cả nhóm chạy nghiệm thu.

---

## ⏱️ 2. CHECKLIST THỰC HÀNH THEO 4 MỐC

### 📍 MỐC 1: Định hình & Đánh giá độ phù hợp (Agentic Fit) (20 phút)

*Mục tiêu: Chứng minh bài toán này CẦN dùng Agent chứ không chỉ Chatbot.*

- [x] **Role 1 & Cả nhóm**: **Tự do lựa chọn 1 chủ đề bài toán thực tế** mà nhóm hào hứng nhất (Xem 10 đề tài gợi ý tại: [DANH_SACH_DE_TAI.md](file:///c:/Users/Admin/Documents/VinUni/LabCoachVin/LabKeyCoach/Day-3-Lab-Chatbot-vs-react-agent-E402/docs/DANH_SACH_DE_TAI.md)).
- [x] **Role 5**: Điền bảng **Scoring Matrix** (chấm 1–5 điểm cho 4 tiêu chí) vào `docs/trace_eval.md`.
- [x] **Role 2**: Liệt kê tên các công cụ sẽ tạo trong `src/tools.py` phù hợp với chủ đề nhóm đã chọn.
- [x] **Role 3**: Xác định các trường hợp tool có thể bị lỗi (Failure Modes).
- [x] **Role 4**: Mở Terminal gõ `python src/app.py` kiểm tra xem môi trường sẵn sàng chưa.
- [x] 🤝 **Cả nhóm**: Thống nhất chủ đề “Trợ lý tra cứu đơn hàng và xử lý đổi/trả”.
- [x] 🔄 **Đồng bộ Git Mốc 1**: Nội dung Mốc 1 đã có trên nhánh `main`.

---

### 📍 MỐC 2: Baseline Chatbot & Khai báo Tool Specs (30 phút)

*Mục tiêu: Thấy rõ hạn chế của Chatbot gốc và chuẩn hóa công cụ cho Agent.*

- [x] **Role 1**: Viết bộ **Test Cases** vào file `config/test_cases.json` (11 case: đơn giản, multi-step, câu bẫy).
- [x] **Role 2**: Bổ sung Tool Contract, safe wrapper và self-test `17/17` trong `src/tools.py`.
- [x] **Role 3**: Soạn `CHATBOT_BASELINE_PROMPT` trong file `src/prompts.py`.
- [x] **Role 4 (Đầu mối Lắp ráp)**: Nối `run_baseline_chatbot()` trong `src/app.py` và chạy thử.
- [x] **Role 5**: Ghi phản hồi mẫu và ma trận phân loại baseline vào `docs/trace_eval.md`.
- [x] 🔄 **Đồng bộ Git Mốc 2**: Nội dung Mốc 2 đã có trên nhánh `main`.

---

### 📍 MỐC 3: ReAct Loop & Safeguards (60 phút)

*Mục tiêu: Dựng ReAct Agent suy luận Thought -> Action và cài phanh an toàn.*

- [x] **Role 3**: Soạn Agent V2 `REACT_SYSTEM_PROMPT`, `MAX_ITERATIONS`, timeout, repeated-action và privacy guardrails.
- [x] **Role 2**: Mọi tool trả chuỗi Observation, có safe wrapper và không crash khi lỗi.
- [x] **Role 4 (Đầu mối Lắp ráp & Vibe App)**: Lắp ReAct loop, parser recovery, grounded Observation và safe fallback.
- [x] **Role 5**: Ghi successful trace, failed trace, Root Cause và Before/After trong `docs/trace_eval.md`.
- [x] **Role 1**: Edge cases được kiểm tra bằng self-test và regression test offline.
- [x] 🔄 **Đồng bộ Git Mốc 3**: Code và báo cáo Mốc 3 sẵn sàng push lên `main`.

---

### 📍 MỐC 4: Tương tác liên nhóm & Hybrid Flowchart (40 phút)

*Mục tiêu: Thử thách khả năng chịu lỗi trước đòn tấn công từ nhóm khác & Chấm chéo linh hoạt.*

> 💡 **HÌNH THỨC TƯƠNG TÁC (Tùy Giảng viên chỉ định)**:
>
> * 🎲 **Hình thức 1 (Gọi ngẫu nhiên)**: Giảng viên gọi ngẫu nhiên một thành viên đại diện trong bất kỳ nhóm nào lên trình chiếu App, phản biện và trả lời câu hỏi bẫy từ các nhóm khác.
> * 🔄 **Hình thức 2 (Chấm chéo nhóm)**: Giảng viên chỉ định 1 bạn đại diện (VD: Role 1 hoặc Role 5) đi sang nhóm khác để "tấn công" (dùng câu bẫy thử nghiệm Agent nhóm bạn) và chấm điểm chéo.

- [x] ⚔️ **Internal Pre-Audit**: Đã chạy bộ câu tấn công nội bộ và ghi tại `docs/cross_audit.md`.
- [ ] 🤝 **Cross-Audit với nhóm khác**: Điền tên nhóm/người chấm và câu hỏi phát sinh tại buổi học.
- [x] 🛡️ **Đội Phòng Thủ**: Đã kiểm tra tool error, malformed format, repeated action, max iterations và write safety.
- [x] 📊 **Role 5B (hoặc Role 5)**: Vẽ sơ đồ **Hybrid Flowchart** vào file `docs/hybrid_flowchart.mermaid` thể hiện phân luồng:
  - Câu hỏi đơn giản ➔ Đi đường Chatbot path.
  - Câu hỏi phức tạp ➔ Đi đường ReAct Agent path.
- [x] 🔄 **Đồng bộ Git Mốc 4 (phần kỹ thuật)**: Artifact sẵn sàng push; biên bản bên ngoài chờ buổi chấm chéo thực tế.

---

Vì mỗi thành viên giữ đúng 1 file trong các thư mục riêng (`config/`, `src/`, `docs/`), bạn chỉ cần nhớ quy trình :

**Trước khi gõ code**: Kéo code mới của nhóm về:

```bash
   git pull
```

**Đẩy code lên cho nhóm**:

```bash
   git add .
   git commit -m "Role X: cap nhat noi dung"
   git push
```

*(Nếu push bị chặn do bạn khác push trước: Gõ `git pull` rồi `git push` lại là xong!)*
