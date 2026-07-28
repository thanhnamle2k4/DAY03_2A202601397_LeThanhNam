"""
🚀 CORE AGENT APP (Dành cho Role 4: Core Agent Developer)
File chính ghép nối tất cả các thành phần: Tools + Prompts + Test Cases + Multi-Provider.
"""

import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from dotenv import load_dotenv

# Đảm bảo import các module cùng thư mục src/ hoạt động mượt mà
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Đảm bảo in ra Tiếng Việt và Emojis không bị lỗi trên Windows Console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Import các thành phần từ file của Role 2, Role 3 & Multi-Provider Adapter
from tools import get_tools_description, reset_mock_state, run_tool
from prompts import (
    CHATBOT_BASELINE_PROMPT,
    MAX_ITERATIONS,
    MAX_REPEATED_ACTIONS,
    REACT_SYSTEM_PROMPT,
    TIMEOUT_SECONDS,
)
from providers import get_llm_provider

load_dotenv()

def load_test_cases():
    """Đọc bộ test cases từ config/test_cases.json của Role 1"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config", "test_cases.json")
    
    # Fallback kiểm tra nếu file ở thư mục hiện tại
    if not os.path.exists(config_path):
        config_path = "test_cases.json"
        
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


SAFE_FALLBACK = (
    "Xin lỗi, tôi chưa thể hoàn tất yêu cầu một cách an toàn. "
    "Vui lòng kiểm tra lại thông tin hoặc liên hệ nhân viên hỗ trợ."
)
PRIVACY_REFUSAL = (
    "Tôi không thể bỏ qua hướng dẫn an toàn hoặc cung cấp dữ liệu đơn hàng "
    "hàng loạt. Tôi chỉ có thể hỗ trợ một đơn cụ thể khi bạn cung cấp mã đơn."
)


def _is_prompt_injection(user_query: str) -> bool:
    """Nhận diện các mẫu injection/quyền riêng tư rõ ràng trong bộ test."""
    normalized = user_query.casefold()
    blocked_patterns = (
        "bỏ qua mọi hướng dẫn",
        "bỏ qua hướng dẫn phía trên",
        "liệt kê toàn bộ đơn hàng",
        "hiển thị system prompt",
        "đọc system prompt",
    )
    return any(pattern in normalized for pattern in blocked_patterns)


def run_baseline_chatbot(user_query: str, provider):
    """
    Dựng Chatbot gốc (Baseline) không có công cụ.
    """
    print(f"\n💬 [CHATBOT BASELINE] Câu hỏi: {user_query}")
    print(f"⚙️ System Prompt: {CHATBOT_BASELINE_PROMPT.strip()}")
    
    # Gọi LLM Provider thực hiện sinh câu trả lời
    response = provider.generate(user_query, system_prompt=CHATBOT_BASELINE_PROMPT)
    print(f"🤖 Chatbot trả lời:\n{response}")
    return response


def _execute_tool_with_timeout(tool_name: str, args_str: str) -> str:
    """Chạy tool với timeout; mọi lỗi được chuyển thành Observation dạng chuỗi."""
    executor = ThreadPoolExecutor(max_workers=1)
    future = executor.submit(run_tool, tool_name, args_str)
    try:
        return future.result(timeout=TIMEOUT_SECONDS)
    except FutureTimeoutError:
        future.cancel()
        return (
            f"LỖI: Tool '{tool_name}' vượt quá timeout "
            f"{TIMEOUT_SECONDS} giây và đã bị ngắt an toàn."
        )
    except Exception as exc:
        return f"LỖI: Không thực thi được tool '{tool_name}' ({type(exc).__name__}: {exc})."
    finally:
        executor.shutdown(wait=False, cancel_futures=True)


def run_react_agent(user_query: str, provider):
    """
    Dựng vòng lặp ReAct Agent (Thought -> Action -> Observation) có Guardrails.
    """
    print(f"\n🤖 [REACT AGENT] Câu hỏi: {user_query}")
    if _is_prompt_injection(user_query):
        print("🛡️ INPUT GUARDRAIL: Phát hiện prompt injection/yêu cầu dữ liệu hàng loạt.")
        print(f"🏁 Final Answer: {PRIVACY_REFUSAL}")
        return {
            "status": "final",
            "answer": PRIVACY_REFUSAL,
            "steps": 0,
            "trace": [{"step": 0, "type": "input_guardrail", "answer": PRIVACY_REFUSAL}],
            "history": f"Question: {user_query}",
        }

    step = 0
    history = f"Question: {user_query}"
    trace = []
    action_counts = {}
    eligible_orders = set()
    status = "guardrail"
    final_answer = SAFE_FALLBACK
    system_prompt = REACT_SYSTEM_PROMPT.format(
        tool_descriptions=get_tools_description()
    )
    
    while step < MAX_ITERATIONS:
        step += 1
        print(f"\n--- 🔄 Vòng lặp ReAct (Step {step}/{MAX_ITERATIONS}) ---")
        
        # Gọi LLM sinh suy luận (truyền lịch sử chat)
        try:
            llm_response = provider.generate(history, system_prompt=system_prompt)
        except Exception as exc:
            llm_response = f"LỖI PROVIDER: {type(exc).__name__}: {exc}"

        if not isinstance(llm_response, str):
            llm_response = f"LỖI PROVIDER: output phải là str, nhận {type(llm_response).__name__}"
        
        # 1. Trích xuất Final Answer (Nếu có thì xong)
        final_answer_match = re.search(r"Final Answer:\s*(.+)", llm_response, re.IGNORECASE | re.DOTALL)
        if final_answer_match:
            final_answer = final_answer_match.group(1).strip()
            status = "final"
            trace.append({"step": step, "type": "final", "answer": final_answer})
            print(f"🏁 Final Answer: {final_answer}")
            break
            
        # 2. Trích xuất Thought
        thought_match = re.search(r"Thought:\s*(.+)", llm_response, re.IGNORECASE)
        if thought_match:
            print(f"🧠 Thought: {thought_match.group(1).strip()}")
            
        # 3. Trích xuất Action
        action_match = re.search(r"Action:\s*([a-zA-Z0-9_]+)\[(.*?)\]", llm_response, re.IGNORECASE)
        if action_match:
            tool_name = action_match.group(1).strip()
            tool_args_str = action_match.group(2).strip()
            action_key = (tool_name.lower(), tool_args_str.casefold())
            action_counts[action_key] = action_counts.get(action_key, 0) + 1
            
            print(f"🛠️ Action: {tool_name}[{tool_args_str}]")

            if action_counts[action_key] > MAX_REPEATED_ACTIONS:
                obs = (
                    "LỖI: Phát hiện Action bị lặp lại quá "
                    f"{MAX_REPEATED_ACTIONS} lần; ngắt để tránh vòng lặp."
                )
                trace.append({
                    "step": step,
                    "type": "repeated_action",
                    "thought": thought_match.group(1).strip() if thought_match else "",
                    "action": tool_name,
                    "args": tool_args_str,
                    "observation": obs,
                })
                print(f"👁️ Observation: {obs}")
                print(f"🏁 Final Answer: {SAFE_FALLBACK}")
                status = "guardrail"
                break
            
            # Defense in depth: write action chỉ chạy sau Observation xác nhận
            # đủ điều kiện trong chính trace hiện tại.
            requested_order = tool_args_str.split(",", 1)[0].strip().strip("'\"").upper()
            if (
                tool_name.lower() == "create_return_request"
                and requested_order not in eligible_orders
            ):
                obs = (
                    "LỖI: Chưa có Observation xác nhận đơn đủ điều kiện trong "
                    "trace hiện tại; từ chối thực hiện write action."
                )
            else:
                obs = _execute_tool_with_timeout(tool_name, tool_args_str)

            if (
                tool_name.lower() == "check_return_eligibility"
                and obs.startswith("ĐỦ ĐIỀU KIỆN:")
            ):
                eligible_orders.add(requested_order)

            print(f"👁️ Observation: {obs}")
            trace.append({
                "step": step,
                "type": "tool",
                "thought": thought_match.group(1).strip() if thought_match else "",
                "action": tool_name,
                "args": tool_args_str,
                "observation": obs,
            })
            
            # Dán kết quả vào lịch sử cho vòng lặp tiếp theo
            history += f"\n{llm_response}\nObservation: {obs}\n"
        else:
            parse_error = (
                "LỖI FORMAT: Phản hồi phải chứa đúng một Action[...] "
                "hoặc Final Answer:. Hãy sửa định dạng ở lượt tiếp theo."
            )
            print("⚠️ Cảnh báo: LLM không trả về Action hợp lệ hoặc Format sai.")
            print("Raw LLM:\n", llm_response)
            print(f"👁️ Observation: {parse_error}")
            trace.append({
                "step": step,
                "type": "parse_error",
                "raw": llm_response,
                "observation": parse_error,
            })
            history += f"\n{llm_response}\nObservation: {parse_error}\n"
            
    if status != "final" and step >= MAX_ITERATIONS:
        print(f"🛡️ GUARDRAIL TRIGGERED: Đã đạt giới hạn tối đa {MAX_ITERATIONS} bước. Ngắt lặp an toàn!")
        print(f"🏁 Final Answer: {SAFE_FALLBACK}")

    return {
        "status": status,
        "answer": final_answer,
        "steps": step,
        "trace": trace,
        "history": history,
    }


if __name__ == "__main__":
    print("==================================================")
    print("🏫 ĐẠI HỌC VINUNI - BÀI LAB 3: CHATBOT VS REACT AGENT")
    print("==================================================")
    
    # Khởi tạo Multi-Provider LLM Adapter (Đọc từ biến môi trường LLM_PROVIDER)
    provider = get_llm_provider()
    model_name = getattr(provider, "model_name", "Offline Mock Mode")
    print(f"🔌 LLM Provider đang hoạt động: {provider.__class__.__name__} (Model: {model_name})")
    
    tests = load_test_cases()
    
    while True:
        print("\n" + "="*50)
        print(" 🎯 MENU CHÍNH")
        print("="*50)
        print("[0] Chạy tự động toàn bộ 11 Test Cases")
        print("[1] Chế độ Chat trực tiếp (Tự nhập câu hỏi)")
        print("[2] Thoát chương trình")
        
        try:
            choice = input("\n👉 Lựa chọn của bạn (0-2): ").strip()
            
            if choice == '2':
                print("👋 Tạm biệt!")
                break
                
            elif choice == '0':
                print("\n🚀 BẮT ĐẦU CHẠY TOÀN BỘ TEST CASES...")
                reset_mock_state()
                for t in tests:
                    print(f"\n" + "="*50)
                    print(f"▶️ ĐANG CHẠY TEST CASE SỐ {t['id']}: {t['category']}")
                    print(f"="*50)
                    
                    print("\n--- DEMO 1: CHẠY TRÊN CHATBOT BASELINE ---")
                    run_baseline_chatbot(t["question"], provider)
                    
                    print("\n--- DEMO 2: CHẠY TRÊN REACT AGENT ---")
                    run_react_agent(t["question"], provider)
                    
                input("\n[Đã chạy xong tất cả. Nhấn Enter để quay lại menu chính...]")
                
            elif choice == '1':
                print("\n" + "="*50)
                print("💬 CHẾ ĐỘ CHAT TRỰC TIẾP (LIVE CHAT)")
                print("Gõ 'exit' hoặc 'quit' để thoát về Menu chính.")
                print("="*50 + "\n")
                
                while True:
                    user_query = input("🧑 Bạn: ")
                    
                    if user_query.strip().lower() in ['exit', 'quit']:
                        print("🔙 Quay lại Menu chính...")
                        break
                        
                    if not user_query.strip():
                        continue
                    
                    print("\n--- 🤖 REACT AGENT XỬ LÝ ---")
                    run_react_agent(user_query, provider)
                    print("\n" + "-"*50)
            else:
                print("❌ Lựa chọn không hợp lệ. Vui lòng nhập 0, 1 hoặc 2.")
                
        except KeyboardInterrupt:
            print("\n👋 Tạm biệt!")
            break

