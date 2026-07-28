"""
🛠️ TOOL REGISTRY & SCHEMAS (Dành cho Role 2: Tool & Spec Engineer)
Đề tài: Trợ Lý Tra Cứu Đơn Hàng & Xử Lý Đổi Trả
"""

from datetime import datetime, timedelta

# ============================================================
# 📦 DATABASE GIẢ LẬP — 5 đơn hàng mẫu
# ============================================================

ORDERS_DB = {
    "ORD001": {
        "order_id":            "ORD001",
        "customer_name":       "Nguyễn Văn An",
        "product_name":        "Áo sơ mi nam (Size L)",
        "quantity":            1,
        "total_price":         350_000,
        "status":              "delivered",   # pending | shipping | delivered | cancelled
        "order_date":          "2026-07-15",
        "delivery_date":       "2026-07-20",
        "carrier":             "Giao Hàng Nhanh",
        "return_deadline_days": 7,
    },
    "ORD002": {
        "order_id":            "ORD002",
        "customer_name":       "Trần Thị Bích",
        "product_name":        "Giày thể thao nữ (Size 37)",
        "quantity":            1,
        "total_price":         890_000,
        "status":              "shipping",
        "order_date":          "2026-07-25",
        "delivery_date":       None,          # chưa giao
        "carrier":             "Viettel Post",
        "return_deadline_days": 7,
    },
    "ORD003": {
        "order_id":            "ORD003",
        "customer_name":       "Lê Minh Khoa",
        "product_name":        "Tai nghe Sony WH-1000XM5",
        "quantity":            1,
        "total_price":         6_500_000,
        "status":              "delivered",
        "order_date":          "2026-07-01",
        "delivery_date":       "2026-07-05",  # đã quá hạn đổi trả
        "carrier":             "GHTK",
        "return_deadline_days": 7,
    },
    "ORD004": {
        "order_id":            "ORD004",
        "customer_name":       "Phạm Thị Lan",
        "product_name":        "Bộ mỹ phẩm dưỡng da (combo 3 món)",
        "quantity":            1,
        "total_price":         1_200_000,
        "status":              "cancelled",
        "order_date":          "2026-07-22",
        "delivery_date":       None,
        "carrier":             "J&T Express",
        "return_deadline_days": 0,
    },
    "ORD005": {
        "order_id":            "ORD005",
        "customer_name":       "Hoàng Đức Thịnh",
        "product_name":        "Bàn phím cơ AKKO 3087 (Switch Blue)",
        "quantity":            2,
        "total_price":         2_400_000,
        "status":              "delivered",
        "order_date":          "2026-07-22",
        "delivery_date":       "2026-07-26",  # còn trong hạn đổi trả
        "carrier":             "Giao Hàng Nhanh",
        "return_deadline_days": 7,
    },
}

RETURN_REQUESTS_DB = {}  # lưu yêu cầu đổi trả đã tạo


# ============================================================
# 🔧 TOOL 1: Tra cứu thông tin đơn hàng
# ============================================================

def get_order_info(order_id: str) -> str:
    """
    Tra cứu thông tin chi tiết và trạng thái của một đơn hàng.

    Args:
        order_id (str): Mã đơn hàng. Ví dụ: 'ORD001', 'ORD002'

    Returns:
        str: Thông tin đơn hàng đầy đủ, hoặc thông báo lỗi nếu không tìm thấy.
    """
    order = ORDERS_DB.get(order_id.upper())
    if not order:
        return f"LỖI: Không tìm thấy đơn hàng '{order_id}'. Vui lòng kiểm tra lại mã đơn."

    status_map = {
        "pending":   "⏳ Chờ xác nhận",
        "shipping":  "🚚 Đang vận chuyển",
        "delivered": "✅ Đã giao thành công",
        "cancelled": "❌ Đã huỷ",
    }
    status_label  = status_map.get(order["status"], order["status"])
    delivery_info = (
        f"Ngày nhận hàng: {order['delivery_date']}"
        if order["delivery_date"]
        else "Chưa giao hàng"
    )

    return (
        f"📦 THÔNG TIN ĐƠN HÀNG #{order['order_id']}\n"
        f"  • Khách hàng  : {order['customer_name']}\n"
        f"  • Sản phẩm    : {order['product_name']} x{order['quantity']}\n"
        f"  • Tổng tiền   : {order['total_price']:,} VNĐ\n"
        f"  • Trạng thái  : {status_label}\n"
        f"  • Ngày đặt    : {order['order_date']}\n"
        f"  • {delivery_info}\n"
        f"  • Vận chuyển  : {order['carrier']}"
    )


# ============================================================
# 🔧 TOOL 2: Kiểm tra điều kiện đổi/trả
# ============================================================

def check_return_eligibility(order_id: str) -> str:
    """
    Kiểm tra xem đơn hàng có đủ điều kiện để yêu cầu đổi/trả hay không.

    Args:
        order_id (str): Mã đơn hàng. Ví dụ: 'ORD001'

    Returns:
        str: Kết quả kiểm tra kèm lý do chi tiết.
    """
    order = ORDERS_DB.get(order_id.upper())
    if not order:
        return f"LỖI: Không tìm thấy đơn hàng '{order_id}'."

    if order["status"] == "cancelled":
        return f"❌ KHÔNG ĐỦ ĐIỀU KIỆN: Đơn #{order_id} đã bị huỷ, không thể đổi/trả."

    if order["status"] in ("pending", "shipping"):
        return (
            f"❌ KHÔNG ĐỦ ĐIỀU KIỆN: Đơn #{order_id} đang '{order['status']}', "
            f"chỉ được đổi/trả sau khi nhận hàng thành công."
        )

    # Đã giao — kiểm tra thời hạn
    delivery_date = datetime.strptime(order["delivery_date"], "%Y-%m-%d")
    deadline      = delivery_date + timedelta(days=order["return_deadline_days"])
    today         = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    days_left     = (deadline - today).days

    if days_left < 0:
        return (
            f"❌ KHÔNG ĐỦ ĐIỀU KIỆN: Đơn #{order_id} đã quá hạn đổi/trả "
            f"(nhận hàng {order['delivery_date']}, hạn {order['return_deadline_days']} ngày). "
            f"Đã quá {abs(days_left)} ngày."
        )

    return (
        f"✅ ĐỦ ĐIỀU KIỆN ĐỔI/TRẢ: Đơn #{order_id} ({order['product_name']}) "
        f"còn {days_left} ngày trong thời hạn (hạn cuối: {deadline.strftime('%Y-%m-%d')})."
    )


# ============================================================
# 🔧 TOOL 3: Tạo yêu cầu đổi/trả
# ============================================================

def create_return_request(order_id: str, reason: str) -> str:
    """
    Tạo yêu cầu đổi/trả hàng cho đơn hàng đủ điều kiện.

    Args:
        order_id (str): Mã đơn hàng. Ví dụ: 'ORD001'
        reason   (str): Lý do đổi/trả. Ví dụ: 'Sản phẩm bị lỗi', 'Sai kích cỡ'

    Returns:
        str: Xác nhận tạo thành công kèm mã vận đơn trả hàng, hoặc thông báo lỗi.
    """
    eligibility = check_return_eligibility(order_id)
    if "KHÔNG ĐỦ ĐIỀU KIỆN" in eligibility or "LỖI" in eligibility:
        return f"Không thể tạo yêu cầu. {eligibility}"

    order       = ORDERS_DB[order_id.upper()]
    return_code = f"RET-{order_id.upper()}-{len(RETURN_REQUESTS_DB) + 1:04d}"

    RETURN_REQUESTS_DB[return_code] = {
        "return_code": return_code,
        "order_id":    order_id.upper(),
        "reason":      reason,
        "created_at":  datetime.now().strftime("%Y-%m-%d %H:%M"),
        "status":      "pending_pickup",
    }

    return (
        f"✅ TẠO YÊU CẦU ĐỔI/TRẢ THÀNH CÔNG!\n"
        f"  • Mã yêu cầu  : {return_code}\n"
        f"  • Đơn hàng    : #{order_id.upper()} — {order['product_name']}\n"
        f"  • Lý do       : {reason}\n"
        f"  • Trạng thái  : Chờ lấy hàng\n"
        f"  • Hướng dẫn   : Đóng gói và chờ {order['carrier']} đến lấy trong 1-2 ngày làm việc."
    )


# ============================================================
# 🔧 TOOL 4: Tra cứu chính sách đổi/trả
# ============================================================

def get_return_policy(category: str = "general") -> str:
    """
    Tra cứu chính sách đổi/trả hàng theo danh mục sản phẩm.

    Args:
        category (str): Danh mục sản phẩm. Hỗ trợ: 'general', 'fashion', 'electronics'.
                        Mặc định là 'general'.

    Returns:
        str: Nội dung chính sách đổi/trả chi tiết.
    """
    cat = category.lower().strip()

    if any(k in cat for k in ["điện tử", "electronic", "tech", "tai nghe", "máy", "thiết bị", "bàn phím"]):
        return (
            "📋 CHÍNH SÁCH ĐỔI/TRẢ — ĐIỆN TỬ:\n"
            "  • Thời hạn   : 7 ngày kể từ ngày nhận (lỗi kỹ thuật do NSX).\n"
            "  • Điều kiện  : Còn đủ bộ, nguyên seal/hộp, kèm hóa đơn.\n"
            "  • Không áp dụng: Đã tháo seal, va đập vật lý, ngấm nước.\n"
            "  • Bảo hành   : Theo chính sách riêng của nhà sản xuất."
        )
    elif any(k in cat for k in ["thời trang", "fashion", "quần áo", "giày", "áo", "váy"]):
        return (
            "📋 CHÍNH SÁCH ĐỔI/TRẢ — THỜI TRANG:\n"
            "  • Thời hạn   : 7 ngày kể từ ngày nhận hàng.\n"
            "  • Điều kiện  : Còn nguyên tem mác, chưa giặt, không có mùi lạ.\n"
            "  • Đổi size   : Miễn phí 1 lần nếu còn hàng.\n"
            "  • Hàng sale  : Không áp dụng trừ trường hợp hàng lỗi."
        )
    else:
        return (
            "📋 CHÍNH SÁCH ĐỔI/TRẢ CHUNG:\n"
            "  • Thời hạn   : 7 ngày kể từ ngày nhận hàng.\n"
            "  • Điều kiện  : Còn nguyên tem mác, chưa qua sử dụng, đủ phụ kiện.\n"
            "  • Phí ship   : Shop chịu nếu lỗi do shop; khách chịu nếu đổi ý.\n"
            "  • Hoàn tiền  : Trong 3-5 ngày làm việc sau khi nhận lại hàng."
        )


# ============================================================
# 📋 ĐĂNG KÝ TOOL VÀO REGISTRY
# ============================================================

AVAILABLE_TOOLS = {
    "get_order_info":           get_order_info,
    "check_return_eligibility": check_return_eligibility,
    "create_return_request":    create_return_request,
    "get_return_policy":        get_return_policy,
}
