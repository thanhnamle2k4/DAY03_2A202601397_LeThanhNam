"""
🚀 CORE AGENT APP (Dành cho Role 4: Core Agent Developer)
File chính ghép nối tất cả các thành phần: Tools + Prompts + Test Cases + Multi-Provider.
"""

import json
import os
import re
import sys
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
from tools import AVAILABLE_TOOLS, run_tool, get_tools_description
from prompts import CHATBOT_BASELINE_PROMPT, REACT_SYSTEM_PROMPT, MAX_ITERATIONS
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


def run_baseline_chatbot(user_query: str, provider):
    """
    Dựng Chatbot gốc (Baseline) không có công cụ.
    """
    print(f"\n💬 [CHATBOT BASELINE] Câu hỏi: {user_query}")
    print(f"⚙️ System Prompt: {CHATBOT_BASELINE_PROMPT.strip()}")
    
    # Gọi LLM Provider thực hiện sinh câu trả lời
    response = provider.generate(user_query, system_prompt=CHATBOT_BASELINE_PROMPT)
    print(f"🤖 Chatbot trả lời:\n{response}")


def run_react_agent(user_query: str, provider):
    """
    Dựng vòng lặp ReAct Agent (Thought -> Action -> Observation) có Guardrails.
    """
    print(f"\n🤖 [REACT AGENT] Câu hỏi: {user_query}")
    step = 0
    history = f"Question: {user_query}"
    
    while step < MAX_ITERATIONS:
        step += 1
        print(f"\n--- 🔄 Vòng lặp ReAct (Step {step}/{MAX_ITERATIONS}) ---")
        
        # Gọi LLM sinh suy luận (truyền lịch sử chat)
        llm_response = provider.generate(history, system_prompt=REACT_SYSTEM_PROMPT)
        
        # 1. Trích xuất Final Answer (Nếu có thì xong)
        final_answer_match = re.search(r"Final Answer:\s*(.+)", llm_response, re.IGNORECASE | re.DOTALL)
        if final_answer_match:
            print(f"🏁 Final Answer: {final_answer_match.group(1).strip()}")
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
            
            print(f"🛠️ Action: {tool_name}[{tool_args_str}]")
            
            # Thực thi tool thông qua dispatcher an toàn
            obs = run_tool(tool_name, tool_args_str)
            print(f"👁️ Observation: {obs}")
            
            # Dán kết quả vào lịch sử cho vòng lặp tiếp theo
            history += f"\n{llm_response}\nObservation: {obs}\n"
        else:
            print("⚠️ Cảnh báo: LLM không trả về Action hợp lệ hoặc Format sai.")
            print("Raw LLM:\n", llm_response)
            break
            
    if step >= MAX_ITERATIONS:
        print(f"🛡️ GUARDRAIL TRIGGERED: Đã đạt giới hạn tối đa {MAX_ITERATIONS} bước. Ngắt lặp an toàn!")


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

