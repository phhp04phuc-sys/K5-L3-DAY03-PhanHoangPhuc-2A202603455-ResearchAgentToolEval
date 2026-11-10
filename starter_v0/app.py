from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

import streamlit as st

from env_loader import load_lab_env
from providers import make_provider
from providers.base import ToolCall
from tools import TOOL_FUNCTIONS, load_tool_declarations, to_openai_tools

ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"
TRANSCRIPTS_DIR.mkdir(exist_ok=True, parents=True)
load_lab_env(ROOT)

st.set_page_config(
    page_title="Research Agent v3 UI",
    page_icon="🔎",
    layout="wide",
)


@st.cache_data
def get_system_prompt() -> str:
    return (ARTIFACTS_DIR / "system_prompt.md").read_text(encoding="utf-8")


@st.cache_data
def get_tools_declarations():
    return load_tool_declarations(ARTIFACTS_DIR / "tools.yaml")


def execute_tool_call(call: ToolCall) -> dict:
    func = TOOL_FUNCTIONS.get(call.name)
    if not func:
        return {
            "tool": call.name,
            "args": call.args,
            "result": {"error": "unknown_tool", "message": f"No implementation for {call.name}"},
        }
    try:
        result = func(**call.args)
    except Exception as exc:
        result = {"error": type(exc).__name__, "message": str(exc)}
    return {"tool": call.name, "args": call.args, "result": result}


def run_chat_turn(provider, history_messages, tools, model, max_tool_rounds=4):
    system_prompt = get_system_prompt()
    working_messages = [{"role": "system", "content": system_prompt}] + list(history_messages)
    all_tool_events = []

    for round_idx in range(1, max_tool_rounds + 1):
        response = provider.complete(working_messages, tools, model=model, temperature=0.0)
        calls = response.tool_calls

        if not calls:
            return {
                "status": "answered",
                "text": response.text or "",
                "tool_events": all_tool_events,
            }

        call_summary = [{"name": c.name, "args": c.args} for c in calls]
        working_messages.append({
            "role": "assistant",
            "content": f"{response.text or 'Calling tools...'}\n\nTOOL_CALLS_JSON:\n{json.dumps(call_summary, ensure_ascii=False)}",
        })

        non_clarify_events = []
        for call in calls:
            event = execute_tool_call(call)
            all_tool_events.append(event)

            res = event.get("result", {})
            if isinstance(res, dict) and res.get("awaiting_user"):
                question = res.get("question") or call.args.get("question") or "Vui lòng cung cấp thêm thông tin."
                return {
                    "status": "waiting_for_user",
                    "text": question,
                    "tool_events": all_tool_events,
                }
            non_clarify_events.append(event)

        working_messages.append({
            "role": "user",
            "content": f"TOOL_RESULTS_JSON:\n{json.dumps(non_clarify_events, ensure_ascii=False, indent=2)}\n\nUse these tool results to formulate the final answer or format as requested.",
        })

    return {
        "status": "max_rounds",
        "text": f"Đã dừng sau {max_tool_rounds} vòng gọi tool.",
        "tool_events": all_tool_events,
    }


# ----------------- UI SIDEBAR -----------------
with st.sidebar:
    st.header("⚙️ Cấu hình Agent")
    DEFAULT_MODELS = {
        "gemini": os.getenv("GEMINI_MODEL", "gemini-3.5-flash"),
        "openrouter": os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
        "openai": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        "anthropic": os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-latest"),
        "ollama": os.getenv("OLLAMA_MODEL", "qwen2.5:7b"),
    }
    provider_name = st.selectbox("Provider", ["gemini", "openrouter", "openai", "anthropic", "ollama"], index=0)
    model_name = st.text_input("Model ID", value=DEFAULT_MODELS[provider_name])
    max_rounds = st.slider("Max Tool Rounds", min_value=1, max_value=6, value=4)

    st.divider()
    st.markdown("### 📊 Metrics")
    st.info("Phiên bản hiện tại: **v3**\n\nPass Rate: **100%** (40/40: base, group & extension)")

    st.markdown("### 🛠️ Danh sách Tools (12 tools)")
    declarations = get_tools_declarations()
    tool_names = [d["name"] for d in declarations]
    st.caption(", ".join(tool_names))

    st.divider()
    if st.button("🗑️ Xóa lịch sử Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.transcripts = []
        st.rerun()

# ----------------- UI MAIN -----------------
st.title("🤖 Research Agent (v3) — Live Demo")
st.caption("Agent nghiên cứu thông minh: tìm tin tức thời sự, theo dõi bài viết chuyên gia, đọc toàn văn URL, phân tích cảm xúc (sentiment), tổng hợp digest và bảo đảm an toàn với hành động ghi.")

# Quick samples
col1, col2, col3, col4 = st.columns(4)
sample_prompt = None
with col1:
    if st.button("📰 Tin tức AI hôm nay", use_container_width=True):
        sample_prompt = "Tin tức AI hôm nay có gì nổi bật?"
with col2:
    if st.button("🐦 Tweet Sam Altman", use_container_width=True):
        sample_prompt = "Tweet mới nhất của Sam Altman là gì?"
with col3:
    if st.button("📊 Phân tích cảm xúc", use_container_width=True):
        sample_prompt = "Phân tích cảm xúc đoạn tin: 'Công nghệ AI vừa đạt được bước đột phá xuất sắc và thành công vang dội'"
with col4:
    if st.button("📄 Tóm tắt URL", use_container_width=True):
        sample_prompt = "Tóm tắt bài này giúp mình: https://openai.com/blog/gpt-5"

if "messages" not in st.session_state:
    st.session_state.messages = []
if "transcripts" not in st.session_state:
    st.session_state.transcripts = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "tool_events" in msg and msg["tool_events"]:
            with st.expander("🛠️ Chi tiết Tool Calls & Results"):
                st.json(msg["tool_events"])

user_input = st.chat_input("Nhập câu hỏi hoặc yêu cầu nghiên cứu của bạn...")
prompt = sample_prompt or user_input

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        provider = make_provider(provider_name)
        openai_tools = to_openai_tools(declarations)

        history_for_agent = []
        for m in st.session_state.messages:
            history_for_agent.append({"role": m["role"], "content": m["content"]})

        with st.chat_message("assistant"):
            with st.spinner("Agent đang xử lý và phân tích..."):
                turn_result = run_chat_turn(
                    provider=provider,
                    history_messages=history_for_agent,
                    tools=openai_tools,
                    model=model_name,
                    max_tool_rounds=max_rounds,
                )
                answer_text = turn_result["text"]
                tool_events = turn_result["tool_events"]

                st.markdown(answer_text)
                if tool_events:
                    with st.expander("🛠️ Chi tiết Tool Calls & Results"):
                        st.json(tool_events)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer_text,
            "tool_events": tool_events,
        })

        ts_filename = f"live_{datetime.now().strftime('%Y%m%d_%H%M%S')}.transcript.json"
        ts_path = TRANSCRIPTS_DIR / ts_filename
        transcript_record = {
            "version": "v3",
            "timestamp": datetime.now().isoformat(),
            "messages": st.session_state.messages,
        }
        ts_path.write_text(json.dumps(transcript_record, ensure_ascii=False, indent=2), encoding="utf-8")

    except Exception as exc:
        st.error(f"Lỗi: {exc}")
