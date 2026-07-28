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

**Câu hỏi**: *"Đơn hàng DH1002 của tôi giờ tới đâu rồi?"*

### 🤖 Chatbot Baseline (Mốc 2):

* **Phản hồi**: *"Rất tiếc, tôi không thể tra cứu trạng thái đơn hàng cụ thể mà không có quyền truy cập vào hệ thống thực tế. Tuy nhiên, bạn có thể kiểm tra trạng thái đơn hàng DH1002 bằng cách đăng nhập vào tài khoản của mình trên trang web của chúng tôi hoặc liên hệ trực tiếp với bộ phận chăm sóc khách hàng để được hỗ trợ."*
* **Nhận xét**: Chatbot thừa nhận không thể truy cập hệ thống thực tế. Nó an toàn nhưng không giải quyết được vấn đề tra cứu của người dùng.
