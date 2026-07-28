# 📊 BÁO CÁO GIÁM SÁT & ĐÁNH GIÁ (OBSERVABILITY TRACE LOGS)

*Dành cho Role 5: Observability & Reviewer*

---

## 🎯 1. BẢNG CHẤM ĐIỂM AGENTIC FIT (SCORING MATRIX)

| Tiêu chí                       |  Điểm (1-5)  | Lý do đánh giá                                                                                                                                               |
| :------------------------------- | :-------------: | :--------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 🧠**Multi-step Reasoning** |     `5/5`     | Nhận yêu cầu -> Hỏi mã đơn -> Tra cứu đơn hàng -> Kiểm tra điều kiện đổi trả(thời gian, tình trạng đơn hàng) -> Hướng xử lý          |
| 🛠️**Tool Interaction**   |     `5/5`     | Cần dùng công cụ dể tra cứu tình trạng  đơn hàng thực tế để thực hiện hoàn tiền/hủy đơn                                                   |
| 🔀**Dynamic Decision**     |     `5/5`     | Nếu đơn hàng chưa giao -> Hủy đơn. Nếu đã giao nhưng quá thời gian 7 ngày -> Từ chối đổi trả. Nếu đủ điều kiện -> Chấp nhận xử lí. |
| ⏳**Long Horizon**         |     `4/5`     | Quy trình gồm nhiều lượt hỏi đáp để hỏi thông tin tình trạng đơn hàng trước khi đưa ra quyết định cuối cùng                           |
| **TỔNG ĐIỂM FIT**       | **19/20** | **KẾT LUẬN: BÀI TOÁN RẤT NÊN DÙNG REACT AGENT!**                                                                                                    |

---

## 🔍 2. SO SÁNH PHẢN HỒI (TEST CASE DEMO)

**Câu hỏi**: *"Kiểm tra thông tin đơn hàng với mã đơn SPX200"*

### 🤖 Chatbot Baseline (Mốc 2):

* **Phản hồi**: *"Xin lỗi, tôi không thể kiểm tra thông tin đơn hàng từ hệ thống. Bạn vui lòng cung cấp mã đơn hàng chi tiết hơn hoặc liên hệ trực tiếp với bộ phận chăm sóc khách hàng của chúng tôi để được hỗ trợ nhé!"*
* **Nhận xét**: Chatbot thừa nhận không thể truy cập hệ thống thực tế. Nó an toàn nhưng không giải quyết được vấn đề tra cứu của người dùng.
