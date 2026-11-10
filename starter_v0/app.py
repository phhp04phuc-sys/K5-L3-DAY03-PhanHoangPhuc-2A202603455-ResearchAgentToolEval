"""Streamlit UI cho Research Agent.

Chạy:  streamlit run app.py
Dùng lại vòng lặp tool của chat.py, nên prompt/tools lấy từ artifacts/ và
mỗi lượt chat được ghi transcript vào transcripts/ làm bằng chứng.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import streamlit as st

from chat import (
    ARTIFACTS_DIR,
    ROOT,
    run_model_tool_loop,
    safe_slug,
    trim_history,
    write_transcript,
)
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

DEFAULT_MODEL = ""  # để trống = dùng model mặc định của provider (gemini-3.5-flash)
SAMPLE_QUESTIONS = [
    "Tin tức AI hôm nay có gì nổi bật?",
    "Tweet mới nhất của Sam Altman là gì?",
    "Mọi người đang bàn gì về GPT-5 trên Twitter?",
    "Tóm tắt bài này giúp mình: https://openai.com/blog/gpt-5",
    "Đăng bản tin này lên Telegram giúp mình",
]

st.set_page_config(page_title="Research Agent", page_icon="✻", layout="wide")

# ---------------- Giao diện kiểu Claude (nền tối, nhấn cam, chữ serif cho lời chào) ----------------
# Dùng font miễn phí gần giống: Inter (UI) và Source Serif 4 (tiêu đề). Không dùng logo/biểu tượng của Anthropic.
CLAUDE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Source+Serif+4:opsz,wght@8..60,400;8..60,500&display=swap');
:root{
  --bg:#1a1a1a; --side:#202020; --panel:#232323; --line:#363636; --hover:#2c2c2c;
  --text:#e8e6e3; --muted:#9a9791; --accent:#d97757;
}
html, body, [class*="css"], .stApp{font-family:'Inter',-apple-system,'Segoe UI',sans-serif;color:var(--text)}
.stApp, [data-testid="stAppViewContainer"]{background:var(--bg)}
header[data-testid="stHeader"]{background:transparent}
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"]{display:none !important}

/* Sidebar */
[data-testid="stSidebar"]{background:var(--side);border-right:1px solid var(--line)}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3{font-weight:500;font-size:.8rem;letter-spacing:.02em;color:var(--muted);text-transform:none}
[data-testid="stSidebar"] .stButton>button{width:100%;text-align:left;justify-content:flex-start;background:transparent;border:0;color:var(--text);
  border-radius:8px;padding:.45rem .6rem;font-size:.9rem;font-weight:400}
[data-testid="stSidebar"] .stButton>button:hover{background:var(--hover);color:var(--text)}
[data-testid="stSidebar"] hr{border-color:var(--line)}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"]{color:var(--muted)}

/* Cột nội dung giữa, rộng vừa phải */
[data-testid="stMainBlockContainer"], .block-container{max-width:760px;padding-top:2.2rem}

/* Lời chào */
.welcome{text-align:center;margin:14vh 0 1.4rem}
.welcome .mark{color:var(--accent);font-size:2.2rem;line-height:1}
.welcome h1{font-family:'Source Serif 4',Georgia,serif;font-weight:400;font-size:2.3rem;letter-spacing:-.01em;margin:.5rem 0 .3rem;color:var(--text)}
.welcome p{color:var(--muted);font-size:.98rem;margin:0}

/* Tin nhắn: người dùng là khối bo tròn, trợ lý là chữ trần, không avatar */
[data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessageAvatarAssistant"]{display:none}
[data-testid="stChatMessage"]{background:transparent;padding:.35rem 0;gap:0}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"]{
  background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:.7rem 1rem;width:fit-content;max-width:90%;margin-left:auto}
[data-testid="stChatMessageContent"] p{line-height:1.65;font-size:1rem}

/* Chi tiết tool */
[data-testid="stExpander"]{border:1px solid var(--line);border-radius:10px;background:transparent}
[data-testid="stExpander"] summary{font-size:.85rem;color:var(--muted)}

/* Ô nhập kiểu Claude */
[data-testid="stChatInput"]{background:var(--panel);border:1px solid var(--line);border-radius:18px}
[data-testid="stChatInput"]:focus-within{border-color:#4a4a4a;box-shadow:0 0 0 1px #4a4a4a}
[data-testid="stChatInput"] textarea{color:var(--text);font-family:'Inter',sans-serif;min-height:48px !important;max-height:180px}
[data-testid="stChatInput"] > div{min-height:0}
[data-testid="stChatInputSubmitButton"]{background:var(--accent) !important;color:#fff !important;border-radius:10px}
[data-testid="stBottom"] > div{background:var(--bg)}

/* Nút chung và ô nhập sidebar */
.stButton>button{border-radius:10px}
[data-baseweb="input"], [data-baseweb="select"] > div{background:var(--panel);border-color:var(--line) !important;border-radius:10px}
.stSpinner > div{color:var(--muted)}
</style>
"""
st.markdown(CLAUDE_CSS, unsafe_allow_html=True)

# ---------------- Sidebar: cấu hình ----------------
with st.sidebar:
    st.header("Cấu hình")
    provider_name = st.selectbox("Provider", ["openrouter", "openai", "anthropic", "gemini", "ollama"], index=3)
    model = st.text_input("Model (để trống = mặc định)", DEFAULT_MODEL)
    version = st.text_input("Version (ghi vào transcript)", "v3")
    max_rounds = st.slider("Số vòng tool tối đa", 1, 8, 4)
    window = st.slider("Số cặp hội thoại giữ lại", 1, 10, 5)
    show_events = st.checkbox("Hiện chi tiết tool", value=True)
    if st.button("Xoá hội thoại"):
        for key in ("history", "log", "transcript_path", "transcript"):
            st.session_state.pop(key, None)
        st.rerun()

    st.divider()
    st.subheader("Câu hỏi mẫu")
    for q in SAMPLE_QUESTIONS:
        if st.button(q, key=f"sample-{q}"):
            st.session_state["pending"] = q

system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
tools_path = ARTIFACTS_DIR / "tools.yaml"
declarations = load_tool_declarations(tools_path)

with st.sidebar:
    st.divider()
    st.subheader(f"Tool ({len(declarations)})")
    for item in declarations:
        st.caption(f"**{item['name']}**: {item.get('description', '')[:90]}")

# ---------------- State ----------------
st.session_state.setdefault("history", [])  # lịch sử gửi cho model
st.session_state.setdefault("log", [])      # lịch sử hiển thị

if not st.session_state["log"]:
    st.markdown(
        '<div class="welcome"><div class="mark">✻</div>'
        "<h1>Hôm nay bạn muốn tìm hiểu gì?</h1>"
        "<p>Research Agent tra tin tức, đọc tweet, mở liên kết và tổng hợp bản tin cho bạn.</p></div>",
        unsafe_allow_html=True,
    )


def render(entry: dict) -> None:
    with st.chat_message(entry["role"]):
        st.markdown(entry["content"])
        if show_events and entry.get("events"):
            for event in entry["events"]:
                with st.expander(f"🔧 {event['tool']}({json.dumps(event.get('args', {}), ensure_ascii=False)})"):
                    st.json(event.get("result", {}), expanded=False)


for entry in st.session_state["log"]:
    render(entry)

user_text = st.chat_input("Nhập yêu cầu...") or st.session_state.pop("pending", None)

if user_text:
    user_entry = {"role": "user", "content": user_text}
    st.session_state["log"].append(user_entry)
    render(user_entry)

    system_prompt = system_prompt_path.read_text(encoding="utf-8")
    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state["history"], window),
        {"role": "user", "content": user_text},
    ]

    # Transcript: tạo khi có lượt đầu tiên
    if "transcript_path" not in st.session_state:
        artifact_version = build_artifact_version(version, system_prompt_path, tools_path)
        stamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
        transcript_id = "_".join([safe_slug(version), safe_slug(provider_name), "ui", stamp])
        st.session_state["transcript_path"] = ROOT / "transcripts" / f"{transcript_id}.transcript.json"
        st.session_state["transcript"] = {
            "transcript_id": transcript_id,
            **artifact_version_dict(artifact_version),
            "provider": provider_name,
            "model": model,
            "source": "streamlit_ui",
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "turns": [],
        }

    turn = {"turn_index": len(st.session_state["transcript"]["turns"]) + 1, "user": user_text}
    with st.chat_message("assistant"):
        with st.spinner("Agent đang xử lý..."):
            try:
                provider = make_provider(provider_name)
                result = run_model_tool_loop(
                    provider=provider,
                    messages=messages,
                    tools=to_openai_tools(declarations),
                    model=model or None,
                    max_tool_rounds=max_rounds,
                )
                answer = result["assistant_text"] or "(không có nội dung)"
                events = result.get("tool_events", [])
                turn.update(result)
                st.session_state["history"] += [
                    {"role": "user", "content": user_text},
                    {"role": "assistant", "content": answer},
                ]
            except Exception as exc:  # lỗi provider là bằng chứng, hiện ra cho người dùng
                answer = f"Lỗi: `{type(exc).__name__}`: {exc}"
                events = []
                turn.update({"status": "provider_error", "error": answer})

        st.markdown(answer)
        if show_events:
            for event in events:
                with st.expander(f"🔧 {event['tool']}({json.dumps(event.get('args', {}), ensure_ascii=False)})"):
                    st.json(event.get("result", {}), expanded=False)

    st.session_state["log"].append({"role": "assistant", "content": answer, "events": events})
    st.session_state["transcript"]["turns"].append(turn)
    write_transcript(Path(st.session_state["transcript_path"]), st.session_state["transcript"])
