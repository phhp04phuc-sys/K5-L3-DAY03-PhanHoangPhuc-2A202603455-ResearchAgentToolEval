from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

_APP_DIR = Path(__file__).resolve().parent
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))

from chat import (
    ARTIFACTS_DIR,
    ROOT,
    now_iso,
    run_model_tool_loop,
    safe_slug,
    trim_history,
    write_transcript,
)
from env_loader import load_lab_env
from providers import make_provider
from tools import TOOL_FUNCTIONS, load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

load_lab_env(ROOT)

st.set_page_config(
    page_title="Research Agent — Tool Eval Studio",
    page_icon="🔬",
    layout="wide",
)

SAMPLE_PROMPTS = [
    ("🐦 Tweet cá nhân (timeline)", "Tweet mới nhất của Sam Altman là gì?"),
    ("🔍 Xu hướng X/Twitter (social_search)", "Cho mình các tweet phổ biến (top) nhất về OpenAI"),
    ("📰 Tin tức Web hôm nay (lookup)", "Tin tức AI hôm nay có gì nổi bật?"),
    ("⚡ Đa nguồn song song (lookup + social)", "Tìm trên web tin AI hôm nay và tìm thêm tweet về AI."),
    ("🐙 Tìm repo GitHub (github_search)", "Tìm giúp mình 5 GitHub repository nhiều sao (stars) nhất về langgraph"),
    ("🤗 Tìm model Hugging Face (hf_models)", "Tìm 3 model trên Hugging Face về Qwen2.5 được tải nhiều nhất"),
    ("🟧 Thảo luận Hacker News (hn_search)", "Trên Hacker News đang thảo luận gì về Rust?"),
    ("🌐 Tóm tắt Wikipedia (wiki_summary)", "Tra cứu tóm tắt Wikipedia tiếng Anh về Alan Turing giúp mình"),
    ("❓ Thiếu thông tin (clarify text)", "Tóm tắt 5 tweet mới nhất giúp mình"),
    ("🛡️ Gửi Telegram cần xác nhận (clarify yes_no)", "Đăng bản tin này lên Telegram giúp mình"),
    ("📜 Chính sách nội bộ (policy)", "Theo policy công ty, đăng bản tin lên Telegram channel có cần xác nhận trước không?"),
    ("📄 Tìm & đọc arXiv (paper_text)", "Đọc giúp mình paper arXiv 1706.03762, lấy text 2 trang đầu."),
    ("🚫 Ngoài phạm vi (out_of_scope)", "Giải giúp mình bài toán tích phân: nguyên hàm của x^2 là gì?"),
]


def init_session_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "history" not in st.session_state:
        st.session_state.history = []
    if "turn_index" not in st.session_state:
        st.session_state.turn_index = 0
    if "transcript_id" not in st.session_state:
        st.session_state.transcript_id = None
    if "transcript_path" not in st.session_state:
        st.session_state.transcript_path = None
    if "transcript" not in st.session_state:
        st.session_state.transcript = None
    if "pending_prompt" not in st.session_state:
        st.session_state.pending_prompt = None


def ensure_transcript(
    *,
    version: str,
    provider_name: str,
    selected_model: str | None,
    system_prompt_path: Path,
    tools_path: Path,
    history_window: int,
    max_tool_rounds: int,
) -> tuple[Path, dict[str, Any]]:
    artifact_ver = build_artifact_version(version, system_prompt_path, tools_path)
    if st.session_state.transcript is None or st.session_state.transcript_path is None:
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
        transcript_id = "_".join([safe_slug(version), safe_slug(provider_name), timestamp])
        transcript_path = ROOT / "transcripts" / f"{transcript_id}.transcript.json"
        transcript: dict[str, Any] = {
            "transcript_id": transcript_id,
            **artifact_version_dict(artifact_ver),
            "provider": provider_name,
            "model": selected_model,
            "system_prompt": str(system_prompt_path),
            "tools": str(tools_path),
            "history_window": history_window,
            "max_tool_rounds": max_tool_rounds,
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "turns": [],
        }
        st.session_state.transcript_id = transcript_id
        st.session_state.transcript_path = transcript_path
        st.session_state.transcript = transcript
    else:
        st.session_state.transcript.update({
            **artifact_version_dict(artifact_ver),
            "provider": provider_name,
            "model": selected_model,
            "history_window": history_window,
            "max_tool_rounds": max_tool_rounds,
        })
    return st.session_state.transcript_path, st.session_state.transcript


def reset_conversation() -> None:
    st.session_state.messages = []
    st.session_state.history = []
    st.session_state.turn_index = 0
    st.session_state.transcript_id = None
    st.session_state.transcript_path = None
    st.session_state.transcript = None
    st.session_state.pending_prompt = None


def render_tool_trace(rounds: list[dict[str, Any]], tool_events: list[dict[str, Any]]) -> None:
    if not tool_events:
        st.caption("⚪ `no_tool` — Trả lời trực tiếp không gọi tool.")
        return

    tool_badges = " → ".join(f"`{ev['tool']}`" for ev in tool_events)
    st.caption(f"🔧 **Tool trace ({len(tool_events)} call):** {tool_badges}")
    with st.expander(f"Xem chi tiết {len(tool_events)} tool call & kết quả", expanded=False):
        for r in rounds:
            st.markdown(f"**Round {r.get('round', 1)}**")
            for idx, ev in enumerate(r.get("tool_results", []), start=1):
                st.markdown(f"- **Tool #{idx}:** `{ev['tool']}`")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("*Arguments:*")
                    st.json(ev.get("args", {}))
                with col2:
                    st.markdown("*Result:*")
                    st.json(ev.get("result", {}))


def handle_user_turn(
    user_text: str,
    *,
    provider_name: str,
    model_name: str | None,
    version_label: str,
    system_prompt_path: Path,
    tools_path: Path,
    history_window: int,
    max_tool_rounds: int,
) -> None:
    system_prompt = system_prompt_path.read_text(encoding="utf-8")
    tool_declarations = load_tool_declarations(tools_path)
    openai_tools = to_openai_tools(tool_declarations)
    provider = make_provider(provider_name)
    selected_model = (model_name or "").strip() or getattr(provider, "default_model", None)

    transcript_path, transcript = ensure_transcript(
        version=version_label,
        provider_name=provider_name,
        selected_model=selected_model,
        system_prompt_path=system_prompt_path,
        tools_path=tools_path,
        history_window=history_window,
        max_tool_rounds=max_tool_rounds,
    )

    st.session_state.turn_index += 1
    turn_index = st.session_state.turn_index
    st.session_state.messages.append({"role": "user", "content": user_text})

    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state.history, history_window),
        {"role": "user", "content": user_text},
    ]

    turn_record: dict[str, Any] = {
        "turn_index": turn_index,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }

    try:
        result = run_model_tool_loop(
            provider=provider,
            messages=messages,
            tools=openai_tools,
            model=selected_model,
            max_tool_rounds=max_tool_rounds,
        )
        turn_record.update(result)
        assistant_text = result["assistant_text"]
        st.session_state.history.append({"role": "user", "content": user_text})
        st.session_state.history.append({"role": "assistant", "content": assistant_text})

        # Check if last tool event is awaiting user confirmation/clarification
        clarify_meta: dict[str, Any] | None = None
        if result.get("status") == "waiting_for_user" and result.get("tool_events"):
            last_ev = result["tool_events"][-1]
            res_dict = last_ev.get("result", {}) if isinstance(last_ev.get("result"), dict) else {}
            clarify_meta = {
                "response_type": res_dict.get("response_type") or last_ev.get("args", {}).get("response_type", "text"),
                "options": res_dict.get("options") or last_ev.get("args", {}).get("options", []),
            }

        st.session_state.messages.append({
            "role": "assistant",
            "content": assistant_text,
            "status": result.get("status", "answered"),
            "rounds": result.get("rounds", []),
            "tool_events": result.get("tool_events", []),
            "clarify_meta": clarify_meta,
        })
    except Exception as exc:
        err_msg = f"{type(exc).__name__}: {str(exc)}"
        turn_record.update({
            "status": "provider_error",
            "error": err_msg,
        })
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"❌ **Provider Error:** `{err_msg}`",
            "status": "provider_error",
            "rounds": [],
            "tool_events": [],
            "clarify_meta": None,
        })

    turn_record["ended_at"] = now_iso()
    transcript["turns"].append(turn_record)
    write_transcript(transcript_path, transcript)


def main() -> None:
    init_session_state()

    system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_path = ARTIFACTS_DIR / "tools.yaml"

    # ---------------- Sidebar ----------------
    with st.sidebar:
        st.title("🔬 Research Agent")
        st.caption("Evidence-Driven Tool Evaluation & Live Chat")

        provider_name = st.selectbox(
            "Provider",
            options=["openrouter", "openai", "gemini", "anthropic", "ollama"],
            index=0,
        )
        default_models = {
            "openrouter": "openai/gpt-4o-mini",
            "openai": "gpt-4o-mini",
            "gemini": "gemini-2.5-flash",
            "anthropic": "claude-3-5-haiku-latest",
            "ollama": "qwen2.5:7b",
        }
        model_name = st.text_input(
            "Model (để trống dùng mặc định)",
            value=default_models.get(provider_name, ""),
        )
        version_label = st.text_input("Artifact Version Label", value="v3")

        col_a, col_b = st.columns(2)
        with col_a:
            history_window = st.number_input("History Window", min_value=1, max_value=15, value=5)
        with col_b:
            max_tool_rounds = st.number_input("Max Tool Rounds", min_value=1, max_value=8, value=4)

        artifact_ver = build_artifact_version(version_label, system_prompt_path, tools_path)
        st.markdown("---")
        st.markdown("**Artifact Hashes**")
        st.code(
            f"version : {artifact_ver.artifact_version}\n"
            f"prompt  : {artifact_ver.prompt_hash[:12]}\n"
            f"tools   : {artifact_ver.tools_hash[:12]}",
            language="text",
        )

        if st.button("🗑️ Làm mới hội thoại (New Transcript)", use_container_width=True):
            reset_conversation()
            st.rerun()

        if st.session_state.transcript_path and Path(st.session_state.transcript_path).exists():
            st.success(f"Transcript: `{Path(st.session_state.transcript_path).name}`")
            transcript_bytes = Path(st.session_state.transcript_path).read_bytes()
            st.download_button(
                "⬇️ Tải Transcript JSON",
                data=transcript_bytes,
                file_name=Path(st.session_state.transcript_path).name,
                mime="application/json",
                use_container_width=True,
            )

        st.markdown("---")
        st.markdown("**💡 Câu hỏi mẫu (Click để chạy thử)**")
        for label, prompt_text in SAMPLE_PROMPTS:
            if st.button(label, key=f"sample_{label}", use_container_width=True):
                st.session_state.pending_prompt = prompt_text
                st.rerun()

    # ---------------- Main Tabs ----------------
    tab_chat, tab_eval, tab_artifacts = st.tabs([
        "💬 Live Research Chat",
        "📊 Eval Runs & Version Log",
        "🛠️ Prompt & Tool Declarations",
    ])

    # ================ TAB 1: LIVE CHAT ================
    with tab_chat:
        st.subheader("💬 Interactive Multi-Round Research Agent")
        st.caption(
            "Hỗ trợ định tuyến đa công cụ (`timeline`, `social_search`, `lookup`, `fetch`, `format`, `policy`, `papers`, `paper_text`), "
            "hỏi lại khi thiếu thông tin (`clarify`), và xác nhận trước khi gửi Telegram (`send`)."
        )

        if not st.session_state.messages:
            st.info(
                "👋 Chào bạn! Hãy nhập yêu cầu nghiên cứu bên dưới hoặc chọn một **Câu hỏi mẫu** ở thanh bên trái để bắt đầu."
            )

        for msg_idx, msg in enumerate(st.session_state.messages):
            with st.chat_message(msg["role"]):
                if msg["role"] == "assistant" and msg.get("status") == "waiting_for_user":
                    st.warning(f"❓ **Cần bạn xác nhận / bổ sung thông tin:**\n\n{msg['content']}")
                else:
                    st.markdown(msg["content"])

                if msg["role"] == "assistant":
                    render_tool_trace(msg.get("rounds", []), msg.get("tool_events", []))

                    # Render interactive buttons for the latest clarification turn
                    is_latest = msg_idx == len(st.session_state.messages) - 1
                    clarify_meta = msg.get("clarify_meta")
                    if is_latest and msg.get("status") == "waiting_for_user" and clarify_meta:
                        rtype = clarify_meta.get("response_type", "text")
                        options = clarify_meta.get("options") or []
                        if rtype == "yes_no":
                            c1, c2, _ = st.columns([1, 1, 2])
                            with c1:
                                if st.button("✅ Đồng ý, gửi ngay!", key=f"yes_{msg_idx}", type="primary", use_container_width=True):
                                    st.session_state.pending_prompt = "Đồng ý, xác nhận gửi lên Telegram nhé (confirmed=true)."
                                    st.rerun()
                            with c2:
                                if st.button("❌ Huỷ, không gửi", key=f"no_{msg_idx}", use_container_width=True):
                                    st.session_state.pending_prompt = "Không gửi nữa, huỷ giúp mình."
                                    st.rerun()
                        elif rtype == "choice" and options:
                            cols = st.columns(min(len(options), 4))
                            for opt_i, opt_val in enumerate(options):
                                with cols[opt_i % len(cols)]:
                                    if st.button(str(opt_val), key=f"opt_{msg_idx}_{opt_i}", use_container_width=True):
                                        st.session_state.pending_prompt = str(opt_val)
                                        st.rerun()

        chat_input_val = st.chat_input("Nhập câu hỏi nghiên cứu hoặc phản hồi cho Agent...")
        active_prompt = st.session_state.pending_prompt or chat_input_val
        if active_prompt:
            st.session_state.pending_prompt = None
            with st.spinner("Đang suy luận và thực thi công cụ..."):
                handle_user_turn(
                    active_prompt,
                    provider_name=provider_name,
                    model_name=model_name,
                    version_label=version_label,
                    system_prompt_path=system_prompt_path,
                    tools_path=tools_path,
                    history_window=int(history_window),
                    max_tool_rounds=int(max_tool_rounds),
                )
            st.rerun()

    # ================ TAB 2: EVAL RUNS & VERSION LOG ================
    with tab_eval:
        st.subheader("📈 Version Log (`artifacts/version_log.csv`)")
        version_log_path = ARTIFACTS_DIR / "version_log.csv"
        if version_log_path.exists():
            import csv

            with version_log_path.open("r", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            if rows:
                st.dataframe(rows, width="stretch")
            else:
                st.info("`version_log.csv` hiện chỉ có dòng tiêu đề.")
        else:
            st.warning("Chưa tìm thấy `artifacts/version_log.csv`.")

        st.markdown("---")
        st.subheader("🧪 Run JSON Inspector (`runs/*.json`)")
        runs_dir = ROOT / "runs"
        run_files = sorted(runs_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True) if runs_dir.exists() else []

        if not run_files:
            st.info("Chưa có file log nào trong `runs/`.")
        else:
            selected_run_file = st.selectbox(
                "Chọn file Run JSON",
                options=run_files,
                format_func=lambda p: p.name,
            )
            if selected_run_file:
                run_data = json.loads(selected_run_file.read_text(encoding="utf-8"))
                summary = run_data.get("summary", {})

                m1, m2, m3, m4, m5 = st.columns(5)
                m1.metric("Version", run_data.get("version", "-"))
                m2.metric("Case Accuracy", f"{summary.get('case_accuracy', 0.0):.0%}", f"{summary.get('passed_cases', 0)}/{summary.get('measured_cases', 0)} cases")
                m3.metric("Routing Accuracy", f"{summary.get('tool_routing_accuracy', 0.0):.0%}")
                m4.metric("Argument Accuracy", f"{summary.get('argument_accuracy', 0.0):.0%}")
                mt_acc = summary.get("multiturn_accuracy")
                m5.metric("Multi-turn Accuracy", f"{mt_acc:.0%}" if mt_acc is not None else "N/A")

                st.caption(
                    f"**Artifact Version:** `{run_data.get('artifact_version')}` | "
                    f"**Model:** `{run_data.get('provider')}:{run_data.get('model')}` | "
                    f"**Suite:** `{run_data.get('suite')}` | "
                    f"**Generated:** `{run_data.get('generated_at')}`"
                )

                filter_status = st.radio(
                    "Lọc kết quả:",
                    options=["Tất cả", "Chỉ FAIL", "Chỉ PASS"],
                    horizontal=True,
                )

                results_list = run_data.get("results", [])
                table_rows = []
                for item in results_list:
                    res = item.get("result", {})
                    passed = bool(res.get("passed"))
                    if filter_status == "Chỉ FAIL" and passed:
                        continue
                    if filter_status == "Chỉ PASS" and not passed:
                        continue

                    exp = item.get("expect", {})
                    if exp.get("no_tool"):
                        exp_tools = "no_tool"
                    else:
                        exp_tools = ", ".join(
                            f"{c['name']}({json.dumps(c.get('args', {}), ensure_ascii=False)})"
                            for c in exp.get("tool_calls", [])
                        )
                    act_calls = res.get("actual_tool_calls", [])
                    act_tools = (
                        ", ".join(
                            f"{c['name']}({json.dumps(c.get('args', {}), ensure_ascii=False)})"
                            for c in act_calls
                        )
                        if act_calls
                        else "no_tool"
                    )

                    table_rows.append({
                        "Case ID": item.get("id"),
                        "Status": "✅ PASS" if passed else "❌ FAIL",
                        "Failure Type": res.get("failure_type") or item.get("failure_type") or "",
                        "Observed Mismatch": res.get("observed_mismatch") or "",
                        "Expected": exp_tools,
                        "Actual": act_tools,
                        "Failures": "; ".join(res.get("failures", [])),
                    })

                st.dataframe(table_rows, width="stretch")

                with st.expander("🔍 Xem chi tiết từng Case JSON"):
                    case_ids = [r.get("id") for r in results_list]
                    chosen_case_id = st.selectbox("Chọn Case ID", options=case_ids)
                    chosen_case = next((r for r in results_list if r.get("id") == chosen_case_id), None)
                    if chosen_case:
                        st.json(chosen_case)

    # ================ TAB 3: ARTIFACTS & TOOLS ================
    with tab_artifacts:
        col_left, col_right = st.columns(2)
        with col_left:
            st.subheader("📝 `artifacts/system_prompt.md`")
            current_prompt = system_prompt_path.read_text(encoding="utf-8") if system_prompt_path.exists() else ""
            edited_prompt = st.text_area("Nội dung System Prompt", value=current_prompt, height=450)
            if st.button("💾 Lưu `system_prompt.md`", use_container_width=True):
                system_prompt_path.write_text(edited_prompt, encoding="utf-8")
                st.success("Đã lưu `artifacts/system_prompt.md`!")
                st.rerun()

        with col_right:
            st.subheader("🧰 `artifacts/tools.yaml`")
            current_tools_yaml = tools_path.read_text(encoding="utf-8") if tools_path.exists() else ""
            edited_tools_yaml = st.text_area("Nội dung Tools YAML", value=current_tools_yaml, height=450)
            if st.button("💾 Lưu `tools.yaml`", use_container_width=True):
                tools_path.write_text(edited_tools_yaml, encoding="utf-8")
                st.success("Đã lưu `artifacts/tools.yaml`!")
                st.rerun()

        st.markdown("---")
        st.subheader(f"🔌 Danh sách Tools đã đăng ký ({len(TOOL_FUNCTIONS)} tools)")
        declarations = load_tool_declarations(tools_path)
        tool_summary_rows = [
            {
                "Tool Name": d.get("name"),
                "Implemented in Code": "✅ Yes" if d.get("name") in TOOL_FUNCTIONS else "❌ Missing",
                "Required Params": ", ".join(d.get("parameters", {}).get("required", [])),
                "All Params": ", ".join(d.get("parameters", {}).get("properties", {}).keys()),
                "Description": d.get("description", ""),
            }
            for d in declarations
        ]
        st.dataframe(tool_summary_rows, width="stretch")


if __name__ == "__main__":
    main()
