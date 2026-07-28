"""
🛠️ TOOL REGISTRY & SCHEMAS (Dành cho Role 2: Tool & Spec Engineer)
Đề tài: TRỢ LÝ TRA CỨU ĐƠN HÀNG & XỬ LÝ ĐỔI TRẢ

Nơi khai báo tất cả các "món đồ nghề" mà ReAct Agent có thể gọi.

⚠️ NGUYÊN TẮC BẤT BIẾN CỦA FILE NÀY:
    Mọi tool LUÔN trả về chuỗi string, KHÔNG BAO GIỜ raise exception ra ngoài.
    Lỗi nghiệp vụ là DỮ LIỆU để Agent suy luận tiếp, không phải sự cố làm chết chương trình.
"""

import inspect
import sys

# Đảm bảo in ra Tiếng Việt và Emojis không bị lỗi trên Windows Console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


# =============================================================================
# 📦 MOCK DATABASE — 5 ĐƠN HÀNG (Role 1 viết test case phải dùng đúng mã này)
# =============================================================================
# Ghi chú thiết kế: mỗi đơn phục vụ đúng 1 tình huống kiểm thử.
#   DH1001 ✅ đủ điều kiện trả   | DH1002 ❌ chưa giao    | DH1003 ❌ quá hạn
#   DH1004 ❌ nhóm hàng cấm      | DH1005 ❌ đã hoàn trả  | DH9999 🔴 không tồn tại

MOCK_ORDER_DB = {
    "DH1001": {
        "product": "Áo sơ mi Oxford",
        "category": "thời trang",
        "price": 350000,
        "status": "Đã giao",
        "delivered_days_ago": 3,
    },
    "DH1002": {
        "product": "Tai nghe Sony WH-1000XM4",
        "category": "điện tử",
        "price": 5900000,
        "status": "Đang vận chuyển",
        "delivered_days_ago": None,
    },
    "DH1003": {
        "product": "Nồi chiên không dầu Lock&Lock",
        "category": "gia dụng",
        "price": 1290000,
        "status": "Đã giao",
        "delivered_days_ago": 25,
    },
    "DH1004": {
        "product": "Áo lót cotton (hàng sale 50%)",
        "category": "đồ lót",
        "price": 99000,
        "status": "Đã giao",
        "delivered_days_ago": 2,
    },
    "DH1005": {
        "product": "Giày sneaker Bitis Hunter",
        "category": "thời trang",
        "price": 890000,
        "status": "Đã hoàn trả",
        "delivered_days_ago": 10,
    },
}

# Sổ ghi các yêu cầu hoàn trả đã tạo (bằng chứng side-effect của tool số 3)
RETURN_REQUESTS = {}

# 📜 Chính sách đổi trả theo nhóm hàng
RETURN_POLICY = {
    "thời trang": "Đổi trả trong 7 ngày kể từ ngày giao. Sản phẩm còn nguyên tem mác, chưa qua sử dụng. Miễn phí ship hoàn nếu lỗi từ nhà sản xuất.",
    "điện tử": "Đổi trả trong 7 ngày nếu lỗi kỹ thuật. Phải còn đủ hộp và phụ kiện. Sau 7 ngày chuyển sang chế độ bảo hành 12 tháng.",
    "gia dụng": "Đổi trả trong 7 ngày kể từ ngày giao. Sản phẩm chưa qua sử dụng, còn nguyên seal. Phí ship hoàn 30.000đ nếu đổi ý.",
    "đồ lót": "KHÔNG áp dụng đổi trả vì lý do vệ sinh, theo quy định y tế.",
    "hàng sale": "KHÔNG áp dụng đổi trả. Hàng giảm giá trên 30% được bán theo hình thức thanh lý.",
}

# 🛡️ THAM SỐ NGHIỆP VỤ (Role 3 đưa vào prompt, Role 5 dùng để chấm đúng/sai)
RETURN_WINDOW_DAYS = 7                              # R3: hạn đổi trả
NON_RETURNABLE_CATEGORIES = ("đồ lót", "hàng sale")  # R4: nhóm hàng cấm


# =============================================================================
# 🔧 HÀM TIỆN ÍCH NỘI BỘ (không phải tool, Agent không gọi trực tiếp)
# =============================================================================

def _normalize_order_id(raw: str) -> str:
    """Chuẩn hoá mã đơn: bỏ khoảng trắng, dấu nháy, ngoặc và viết hoa."""
    return str(raw).strip().strip("'\"`[]() ").upper()


def _format_price(price: int) -> str:
    """Định dạng giá tiền kiểu Việt Nam: 350000 -> '350.000đ'."""
    return f"{price:,}".replace(",", ".") + "đ"


def _find_order(order_id: str):
    """
    Tìm đơn hàng trong MOCK_ORDER_DB.

    Returns:
        tuple: (mã_đơn_chuẩn_hoá, dict_đơn_hàng) nếu tìm thấy,
               (mã_đơn_chuẩn_hoá, None) nếu không tồn tại.
    """
    oid = _normalize_order_id(order_id)
    return oid, MOCK_ORDER_DB.get(oid)


# =============================================================================
# 🛠️ TOOL 1 — get_order_status  (READ-ONLY)
# =============================================================================

def get_order_status(order_id: str) -> str:
    """
    Tra cứu trạng thái và thông tin chi tiết của một đơn hàng.

    Name          : get_order_status
    Purpose       : Dùng khi khách hỏi "đơn hàng của tôi tới đâu rồi", hoặc làm
                    BƯỚC ĐẦU TIÊN bắt buộc trước mọi thao tác đổi/trả hàng.
                    KHÔNG dùng để hỏi chính sách chung (dùng get_return_policy).
    Input schema  : order_id (str, bắt buộc) — mã đơn định dạng 'DHxxxx'.
    Output schema : Chuỗi mô tả đơn gồm sản phẩm, nhóm hàng, giá, trạng thái và
                    số ngày kể từ khi giao.
    Error semantics: Mã đơn không tồn tại hoặc để trống -> trả về chuỗi bắt đầu
                    bằng 'LỖI:' kèm gợi ý định dạng đúng. Không raise exception.
    Side effect   : KHÔNG — chỉ đọc dữ liệu.
    Example       : get_order_status('DH1001')
                    -> "📦 Đơn DH1001 | Áo sơ mi Oxford | Nhóm hàng: thời trang | ..."
    Safety        : Bọc toàn bộ trong try/except, mọi sự cố đều trả chuỗi 'LỖI:'.
    """
    try:
        if not str(order_id).strip():
            return "LỖI: Thiếu mã đơn hàng. Cú pháp đúng: get_order_status[DH1001]"

        oid, order = _find_order(order_id)
        if order is None:
            return (
                f"LỖI: Không tìm thấy đơn hàng '{oid}'. "
                f"Vui lòng kiểm tra lại mã đơn (định dạng DHxxxx)."
            )

        if order["delivered_days_ago"] is None:
            thoi_gian = "Chưa giao hàng"
        else:
            thoi_gian = f"Đã giao cách đây {order['delivered_days_ago']} ngày"

        return (
            f"📦 Đơn {oid} | {order['product']} "
            f"| Nhóm hàng: {order['category']} "
            f"| Giá: {_format_price(order['price'])} "
            f"| Trạng thái: {order['status']} "
            f"| {thoi_gian}."
        )
    except Exception as e:
        return f"LỖI: Sự cố khi tra cứu đơn hàng ({type(e).__name__}: {e})."


# =============================================================================
# 🛠️ TOOL 2 — check_return_eligibility  (READ-ONLY)
# =============================================================================

def check_return_eligibility(order_id: str) -> str:
    """
    Kiểm tra một đơn hàng có đủ điều kiện đổi/trả hay không theo 5 luật nghiệp vụ.

    Name          : check_return_eligibility
    Purpose       : Bắt buộc gọi TRƯỚC create_return_request. Agent không được tự
                    phán đoán đủ/không đủ điều kiện thay cho tool này.
    Input schema  : order_id (str, bắt buộc) — mã đơn định dạng 'DHxxxx'.
    Output schema : "ĐỦ ĐIỀU KIỆN: ..." hoặc "TỪ CHỐI: <lý do cụ thể>".
    Error semantics: Mã đơn không tồn tại -> chuỗi 'LỖI: Không tìm thấy đơn hàng...'.
                    Vi phạm luật nghiệp vụ -> chuỗi 'TỪ CHỐI: ...' (đây là kết quả
                    hợp lệ, không phải lỗi hệ thống).
    Side effect   : KHÔNG — chỉ đọc dữ liệu.
    Example       : check_return_eligibility('DH1003')
                    -> "TỪ CHỐI: Đơn DH1003 đã giao 25 ngày, quá hạn 7 ngày..."
    Safety        : Bọc try/except toàn hàm.

    Thứ tự kiểm tra (đặt theo mức độ ưu tiên của thông báo gửi khách):
        R1. Đơn phải tồn tại.
        R5. Đơn chưa từng được hoàn trả.
        R2. Trạng thái phải là 'Đã giao'.
        R4. Nhóm hàng không thuộc danh sách cấm (đồ lót, hàng sale).
        R3. Còn trong hạn RETURN_WINDOW_DAYS ngày kể từ ngày giao.
    """
    try:
        if not str(order_id).strip():
            return "LỖI: Thiếu mã đơn hàng. Cú pháp đúng: check_return_eligibility[DH1001]"

        oid, order = _find_order(order_id)

        # R1 — Đơn phải tồn tại
        if order is None:
            return (
                f"LỖI: Không tìm thấy đơn hàng '{oid}'. "
                f"Vui lòng kiểm tra lại mã đơn (định dạng DHxxxx)."
            )

        # R5 — Đơn đã có yêu cầu hoàn trả đang được xử lý
        existing_request = next(
            (
                rma_code
                for rma_code, request in RETURN_REQUESTS.items()
                if request["order_id"] == oid
            ),
            None,
        )
        if existing_request is not None:
            return (
                f"TỪ CHỐI: Đơn {oid} đã có yêu cầu {existing_request} "
                f"đang được xử lý, không thể tạo yêu cầu mới."
            )

        # R5 — Chống hoàn trả 2 lần
        if order["status"] == "Đã hoàn trả":
            return (
                f"TỪ CHỐI: Đơn {oid} đã được hoàn trả trước đó, "
                f"không thể tạo yêu cầu mới."
            )

        # R2 — Phải giao xong mới được trả
        if order["status"] != "Đã giao":
            return (
                f"TỪ CHỐI: Đơn {oid} đang ở trạng thái '{order['status']}', "
                f"chưa thể tạo yêu cầu đổi trả."
            )

        # R4 — Nhóm hàng cấm đổi trả
        if order["category"] in NON_RETURNABLE_CATEGORIES:
            return (
                f"TỪ CHỐI: Đơn {oid} thuộc nhóm hàng '{order['category']}' "
                f"không áp dụng đổi trả (đồ lót / hàng sale)."
            )

        # R3 — Còn trong hạn đổi trả
        days = order["delivered_days_ago"]
        if days is None or days > RETURN_WINDOW_DAYS:
            return (
                f"TỪ CHỐI: Đơn {oid} đã giao {days} ngày, "
                f"quá hạn {RETURN_WINDOW_DAYS} ngày theo chính sách."
            )

        con_lai = RETURN_WINDOW_DAYS - days
        return (
            f"ĐỦ ĐIỀU KIỆN: Đơn {oid} ({order['product']}) đã giao {days} ngày, "
            f"còn {con_lai} ngày trong hạn đổi trả. Có thể tạo yêu cầu hoàn trả."
        )
    except Exception as e:
        return f"LỖI: Sự cố khi kiểm tra điều kiện đổi trả ({type(e).__name__}: {e})."


# =============================================================================
# 🛠️ TOOL 3 — create_return_request  (⚠️ CÓ SIDE-EFFECT: GHI DỮ LIỆU)
# =============================================================================

def create_return_request(order_id: str, reason: str) -> str:
    """
    Tạo yêu cầu hoàn trả cho một đơn hàng và sinh mã RMA.

    Name          : create_return_request
    Purpose       : Thực hiện HÀNH ĐỘNG hoàn trả sau khi khách xác nhận muốn trả
                    hàng. Đây là tool duy nhất làm THAY ĐỔI TRẠNG THÁI hệ thống.
    Input schema  : order_id (str, bắt buộc) — mã đơn 'DHxxxx'.
                    reason  (str, bắt buộc) — lý do khách đưa ra.
    Output schema : "THÀNH CÔNG: Đã tạo yêu cầu RMA-xxxx cho đơn DHxxxx..."
    Error semantics: Thiếu lý do -> 'LỖI: ...'. Đơn không đủ điều kiện -> 'TỪ CHỐI: ...'
                    và KHÔNG tạo RMA.
    Side effect   : ⚠️ CÓ — ghi vào RETURN_REQUESTS và đổi trạng thái đơn sang
                    'Đang xử lý hoàn trả'.
    Example       : create_return_request('DH1001', 'Áo bị lỗi đường chỉ')
                    -> "THÀNH CÔNG: Đã tạo yêu cầu RMA-1001 cho đơn DH1001..."
    Safety        : Tool TỰ GỌI LẠI check_return_eligibility để tái kiểm tra, KHÔNG
                    tin vào phán đoán của Agent. Nguyên tắc: tool có side-effect
                    không bao giờ tin tầng gọi nó.
    """
    try:
        if not str(order_id).strip():
            return (
                "LỖI: Thiếu mã đơn hàng. Cú pháp đúng: "
                "create_return_request[DH1001, lý do trả hàng]"
            )
        if not str(reason).strip():
            return (
                "LỖI: Thiếu lý do hoàn trả. Vui lòng hỏi khách hàng lý do trước. "
                "Cú pháp đúng: create_return_request[DH1001, Áo bị lỗi đường chỉ]"
            )

        oid = _normalize_order_id(order_id)

        # 🛡️ Tái kiểm tra điều kiện — không tin lời Agent
        eligibility = check_return_eligibility(oid)
        if not eligibility.startswith("ĐỦ ĐIỀU KIỆN"):
            return f"{eligibility} (Không tạo được yêu cầu hoàn trả.)"

        order = MOCK_ORDER_DB[oid]
        rma_code = f"RMA-{oid[2:]}"

        # ⚠️ SIDE-EFFECT: ghi dữ liệu
        RETURN_REQUESTS[rma_code] = {
            "order_id": oid,
            "product": order["product"],
            "reason": str(reason).strip(),
            "refund_amount": order["price"],
        }
        order["status"] = "Đang xử lý hoàn trả"

        return (
            f"THÀNH CÔNG: Đã tạo yêu cầu {rma_code} cho đơn {oid} "
            f"({order['product']}). Lý do: {str(reason).strip()}. "
            f"Số tiền hoàn dự kiến: {_format_price(order['price'])}. "
            f"Shipper sẽ liên hệ lấy hàng trong 24h."
        )
    except Exception as e:
        return f"LỖI: Sự cố khi tạo yêu cầu hoàn trả ({type(e).__name__}: {e})."


# =============================================================================
# 🛠️ TOOL 4 — get_return_policy  (READ-ONLY)
# =============================================================================

def get_return_policy(category: str) -> str:
    """
    Tra cứu chính sách đổi trả áp dụng cho một nhóm hàng.

    Name          : get_return_policy
    Purpose       : Dùng khi khách hỏi về quy định chung của một nhóm hàng, KHÔNG
                    gắn với đơn cụ thể. Nếu khách đưa mã đơn thì dùng
                    check_return_eligibility thay vì tool này.
    Input schema  : category (str, bắt buộc) — một trong:
                    thời trang | điện tử | gia dụng | đồ lót | hàng sale
    Output schema : Chuỗi mô tả chính sách (số ngày, điều kiện, phí ship hoàn).
    Error semantics: Nhóm hàng không hợp lệ -> chuỗi 'LỖI:' kèm danh sách nhóm hàng
                    hợp lệ để Agent tự sửa ở bước sau.
    Side effect   : KHÔNG — chỉ đọc dữ liệu.
    Example       : get_return_policy('điện tử')
                    -> "📜 Chính sách nhóm hàng 'điện tử': Đổi trả trong 7 ngày..."
    Safety        : Bọc try/except, có so khớp gần đúng cho tên không dấu.
    """
    try:
        raw = str(category).strip().strip("'\"`[]() ").lower()
        if not raw:
            return (
                "LỖI: Thiếu tên nhóm hàng. Các nhóm hàng hợp lệ: "
                f"[{', '.join(RETURN_POLICY.keys())}]"
            )

        # Khớp chính xác trước, sau đó khớp gần đúng (chịu được viết không dấu/thiếu chữ)
        if raw in RETURN_POLICY:
            return f"📜 Chính sách nhóm hàng '{raw}': {RETURN_POLICY[raw]}"

        aliases = {
            "thoi trang": "thời trang", "quần áo": "thời trang", "quan ao": "thời trang",
            "dien tu": "điện tử", "do dien tu": "điện tử",
            "gia dung": "gia dụng",
            "do lot": "đồ lót",
            "hang sale": "hàng sale", "sale": "hàng sale", "giảm giá": "hàng sale",
        }
        if raw in aliases:
            key = aliases[raw]
            return f"📜 Chính sách nhóm hàng '{key}': {RETURN_POLICY[key]}"

        return (
            f"LỖI: Không có chính sách cho nhóm hàng '{category}'. "
            f"Các nhóm hàng hợp lệ: [{', '.join(RETURN_POLICY.keys())}]"
        )
    except Exception as e:
        return f"LỖI: Sự cố khi tra cứu chính sách ({type(e).__name__}: {e})."


# =============================================================================
# 📋 TOOL REGISTRY — Danh sách tool được đăng ký cho Agent sử dụng
# =============================================================================

AVAILABLE_TOOLS = {
    "get_order_status": get_order_status,
    "check_return_eligibility": check_return_eligibility,
    "create_return_request": create_return_request,
    "get_return_policy": get_return_policy,
}

# Mô tả tool dạng text — Role 3 nhúng thẳng vào REACT_SYSTEM_PROMPT,
# Role 4 gọi get_tools_description() để prompt luôn khớp với registry.
TOOL_DESCRIPTIONS = """1. get_order_status[order_id]: Tra trạng thái và thông tin chi tiết 1 đơn hàng. Luôn gọi tool này TRƯỚC mọi thao tác đổi trả.
2. check_return_eligibility[order_id]: Kiểm tra đơn có đủ điều kiện đổi/trả không. BẮT BUỘC gọi trước khi tạo yêu cầu hoàn trả.
3. create_return_request[order_id, reason]: Tạo yêu cầu hoàn trả và sinh mã RMA. CHỈ gọi khi đã có kết quả "ĐỦ ĐIỀU KIỆN" và khách đã nêu lý do.
4. get_return_policy[category]: Tra chính sách đổi trả theo nhóm hàng (thời trang | điện tử | gia dụng | đồ lót | hàng sale)."""


def get_tools_description() -> str:
    """Trả về mô tả các tool để Role 3/Role 4 chèn vào System Prompt."""
    return TOOL_DESCRIPTIONS


# =============================================================================
# 🚦 DISPATCHER AN TOÀN — Role 4 chỉ cần gọi đúng 1 dòng: run_tool(name, args)
# =============================================================================

def run_tool(tool_name: str, args_str: str = "") -> str:
    """
    Gọi một tool theo tên, tự tách tham số và bọc lỗi an toàn.

    Dành cho Role 4: sau khi parse được dòng `Action: tên_tool[tham_số]`,
    truyền thẳng tên tool và phần trong ngoặc vuông vào đây.

    Args:
        tool_name (str): Tên tool, ví dụ 'get_order_status'.
        args_str (str) : Chuỗi tham số thô, ví dụ 'DH1001, Áo bị lỗi đường chỉ'.

    Returns:
        str: Kết quả tool (dùng làm Observation), hoặc chuỗi 'LỖI:' mô tả sự cố.
             KHÔNG BAO GIỜ raise exception — Agent luôn có cái để đọc và suy luận tiếp.

    Ví dụ:
        run_tool("get_order_status", "DH1001")
        run_tool("create_return_request", "DH1001, Áo bị lỗi đường chỉ")
        run_tool("search_product", "abc")  -> "LỖI: Tool 'search_product' không tồn tại..."
    """
    try:
        name = str(tool_name).strip().strip("'\"`[]() ")

        # ❌ Failure Mode 1: Unknown Tool
        if name not in AVAILABLE_TOOLS:
            return (
                f"LỖI: Tool '{name}' không tồn tại. "
                f"Các tool hợp lệ: [{', '.join(AVAILABLE_TOOLS.keys())}]"
            )

        func = AVAILABLE_TOOLS[name]
        expected = len(inspect.signature(func).parameters)
        raw = str(args_str).strip().strip("[]").strip()

        # ❌ Failure Mode 2: Malformed Args (thiếu tham số)
        if expected > 0 and not raw:
            return (
                f"LỖI: Tool '{name}' cần {expected} tham số nhưng không nhận được tham số nào. "
                f"Cú pháp đúng: {name}[{', '.join(inspect.signature(func).parameters)}]"
            )

        # Tách tham số: chỉ split đúng (expected - 1) lần để dấu phẩy trong
        # lý do hoàn trả không làm vỡ tham số cuối.
        if expected <= 1:
            args = [raw] if expected == 1 else []
        else:
            args = [a.strip().strip("'\"") for a in raw.split(",", expected - 1)]

        if len(args) < expected:
            return (
                f"LỖI: Tool '{name}' cần {expected} tham số, nhận được {len(args)}. "
                f"Cú pháp đúng: {name}[{', '.join(inspect.signature(func).parameters)}]"
            )

        return func(*args)
    except Exception as e:
        return f"LỖI: Không thực thi được tool '{tool_name}' ({type(e).__name__}: {e})."


# =============================================================================
# 🧪 SELF-TEST — Chạy độc lập: python src/tools.py
# =============================================================================

if __name__ == "__main__":
    print("=" * 62)
    print("🧪 SELF-TEST TOOL REGISTRY — TRỢ LÝ ĐƠN HÀNG & ĐỔI TRẢ")
    print("=" * 62)

    cases = [
        ("✅ Tra đơn hợp lệ",              "get_order_status", "DH1001"),
        ("🔴 Tra đơn không tồn tại",       "get_order_status", "DH9999"),
        ("✅ R3 còn hạn — đủ điều kiện",   "check_return_eligibility", "DH1001"),
        ("❌ R2 chưa giao",                "check_return_eligibility", "DH1002"),
        ("❌ R3 quá hạn 7 ngày",           "check_return_eligibility", "DH1003"),
        ("❌ R4 nhóm hàng cấm",            "check_return_eligibility", "DH1004"),
        ("❌ R5 đã hoàn trả",              "check_return_eligibility", "DH1005"),
        ("🔴 Kiểm tra đơn ma",             "check_return_eligibility", "DH9999"),
        ("⚠️ Tạo yêu cầu hợp lệ",          "create_return_request", "DH1001, Áo bị lỗi đường chỉ"),
        ("🛡️ Chặn tạo yêu cầu quá hạn",    "create_return_request", "DH1003, Không thích nữa"),
        ("🛡️ Chặn tạo yêu cầu nhóm cấm",   "create_return_request", "DH1004, Mặc không vừa"),
        ("❌ Thiếu lý do hoàn trả",        "create_return_request", "DH1002"),
        ("✅ Tra chính sách hợp lệ",       "get_return_policy", "điện tử"),
        ("✅ Tra chính sách viết không dấu", "get_return_policy", "thoi trang"),
        ("🔴 Nhóm hàng không hợp lệ",      "get_return_policy", "xe cộ"),
        ("🔴 Tool không tồn tại",          "search_product", "áo sơ mi"),
        ("🔴 Gọi tool thiếu tham số",      "get_order_status", ""),
    ]

    for label, tool, args in cases:
        print(f"\n{label}")
        print(f"   Action     : {tool}[{args}]")
        print(f"   Observation: {run_tool(tool, args)}")

    print("\n" + "=" * 62)
    print("🛡️ KIỂM TRA CHỐNG HOÀN TRẢ 2 LẦN (gọi lại đơn DH1001 vừa tạo RMA)")
    print(f"   Observation: {run_tool('create_return_request', 'DH1001, Đổi ý')}")

    print("\n" + "=" * 62)
    print(f"📒 SỔ YÊU CẦU HOÀN TRẢ ĐÃ TẠO (bằng chứng side-effect): {list(RETURN_REQUESTS.keys())}")
    print(f"✅ Đã đăng ký {len(AVAILABLE_TOOLS)} tool: {list(AVAILABLE_TOOLS.keys())}")
    print("✅ Không có exception nào thoát ra ngoài — toàn bộ lỗi đều trả về dạng chuỗi.")
    print("=" * 62)