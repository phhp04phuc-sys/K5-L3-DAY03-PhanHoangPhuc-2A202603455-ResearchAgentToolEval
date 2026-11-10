"""Hai trang xem bằng chứng trong giao diện: Eval (chỉ số từng version) và Transcript.

Dữ liệu đọc thẳng từ các file đã có: runs/*.json, artifacts/version_log.csv, transcripts/*.json.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

ROOT = Path(__file__).parent
RUNS_DIR = ROOT / "runs"
TRANSCRIPTS_DIR = ROOT / "transcripts"
VERSION_LOG = ROOT / "artifacts" / "version_log.csv"

METRICS = ["case_accuracy", "tool_routing_accuracy", "argument_accuracy", "multiturn_accuracy"]


def _version_key(version: str) -> tuple[int, str]:
    match = re.match(r"v(\d+)", str(version))
    return (int(match.group(1)) if match else 99, str(version))


@st.cache_data(ttl=5)
def load_runs() -> list[dict[str, Any]]:
    runs = []
    for path in sorted(RUNS_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        data["_file"] = path.name
        runs.append(data)
    return runs


def _tools_text(calls: list[dict[str, Any]] | None) -> str:
    if not calls:
        return "(không gọi tool)"
    return ", ".join(f"{c.get('name')}({json.dumps(c.get('args', {}), ensure_ascii=False)})" for c in calls)


def _expect_text(expect: dict[str, Any]) -> str:
    if expect.get("no_tool"):
        return "(không gọi tool)"
    return _tools_text(expect.get("tool_calls"))


def render_eval() -> None:
    st.markdown("### Eval: chỉ số từng version")
    runs = load_runs()
    if not runs:
        st.info("Chưa có file nào trong `runs/`. Chạy `python run_eval.py ...` để tạo.")
        return

    rows = []
    for run in runs:
        summary = run.get("summary", {})
        rows.append({
            "version": run.get("version"),
            "suite": run.get("suite"),
            "provider": run.get("provider"),
            "model": run.get("model") or "",
            "cases": summary.get("total_cases"),
            "provider_error": summary.get("provider_error_cases", 0),
            **{name: summary.get(name) for name in METRICS},
            "generated_at": run.get("generated_at"),
            "file": run["_file"],
        })
    table = pd.DataFrame(rows)

    col1, col2, col3 = st.columns(3)
    suites = sorted(table["suite"].dropna().unique())
    providers = sorted(table["provider"].dropna().unique())
    suite = col1.selectbox("Bộ eval", suites, index=suites.index("base") if "base" in suites else 0)
    provider = col2.selectbox("Provider", providers, index=providers.index("gemini") if "gemini" in providers else 0)
    hide_errors = col3.checkbox("Ẩn run có provider_error", value=True,
                                help="Run bị lỗi nhà cung cấp (ví dụ hết hạn mức) có case không đo được, không dùng để so điểm.")

    view = table[(table["suite"] == suite) & (table["provider"] == provider)]
    if hide_errors:
        view = view[view["provider_error"] == 0]
    view = view.sort_values("generated_at").drop_duplicates("version", keep="last")
    view = view.sort_values("version", key=lambda s: s.map(_version_key))

    if view.empty:
        st.warning("Không có run nào khớp bộ lọc.")
    else:
        st.caption("Mỗi version lấy lần chạy mới nhất. Điểm là tỉ lệ case qua trong bộ eval đã chọn.")
        chart = view.set_index("version")[["case_accuracy"]].rename(columns={"case_accuracy": "case accuracy"})
        st.bar_chart(chart, height=260)
        st.dataframe(
            view[["version", "cases", *METRICS, "provider_error", "model", "file"]],
            hide_index=True, width="stretch",
            column_config={name: st.column_config.NumberColumn(format="%.2f") for name in METRICS},
        )

    if VERSION_LOG.exists():
        st.markdown("#### Nhật ký version (`version_log.csv`)")
        log = pd.read_csv(VERSION_LOG)
        st.dataframe(log[["version", "changed_artifact", "reason", "hypothesis", "metric_before", "metric_after"]],
                     hide_index=True, width="stretch")

    st.markdown("#### Chi tiết từng case")
    labels = {f"{r['version']} · {r['suite']} · {r['provider']} · {r['generated_at']}": r for r in runs}
    ordered = sorted(labels, key=lambda k: (_version_key(labels[k]["version"]), labels[k].get("generated_at") or ""), reverse=True)
    choice = st.selectbox("Chọn một lần chạy", ordered)
    run = labels[choice]
    summary = run.get("summary", {})
    cols = st.columns(4)
    for col, name in zip(cols, METRICS):
        value = summary.get(name)
        col.metric(name.replace("_", " "), "-" if value is None else f"{value:.2f}")
    if summary.get("provider_error_cases"):
        st.warning(f"Run này có {summary['provider_error_cases']} case lỗi nhà cung cấp (không đo được); điểm chỉ tính trên các case còn lại.")

    case_rows = []
    for item in run.get("results", []):
        result = item.get("result", {})
        case_rows.append({
            "case": item.get("id"),
            "kết quả": "PASS" if result.get("passed") else ("LỖI NHÀ CUNG CẤP" if result.get("failure_type") == "provider_error" else "FAIL"),
            "loại lỗi": result.get("observed_mismatch") or "",
            "mong đợi": _expect_text(item.get("expect", {})),
            "thực tế": _tools_text(result.get("actual_tool_calls")),
            "chi tiết lỗi": "; ".join(result.get("failures") or []),
        })
    cases = pd.DataFrame(case_rows)
    only_fail = st.checkbox("Chỉ hiện case chưa qua", value=False)
    if only_fail:
        cases = cases[cases["kết quả"] != "PASS"]
    st.dataframe(cases, hide_index=True, width="stretch")
    with st.expander("File chạy (JSON đầy đủ)"):
        st.json(run, expanded=False)
        st.download_button("Tải file JSON", json.dumps(run, ensure_ascii=False, indent=2), file_name=run["_file"], mime="application/json")


def render_transcripts() -> None:
    st.markdown("### Transcript các lượt chat")
    files = sorted(TRANSCRIPTS_DIR.glob("*.json"), reverse=True) if TRANSCRIPTS_DIR.exists() else []
    if not files:
        st.info("Chưa có transcript. Chat ở trang Chat, mỗi lượt sẽ được ghi vào `transcripts/`.")
        return

    def label(path: Path) -> str:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return f"{path.name}  ·  {data.get('provider')}  ·  {len(data.get('turns', []))} lượt"
        except (OSError, json.JSONDecodeError):
            return path.name

    names = {label(p): p for p in files}
    choice = st.selectbox("Chọn transcript", list(names))
    path = names[choice]
    data = json.loads(path.read_text(encoding="utf-8"))

    cols = st.columns(4)
    cols[0].metric("Provider", data.get("provider", "-"))
    cols[1].metric("Model", data.get("model") or "mặc định")
    cols[2].metric("Version", data.get("version", "-"))
    cols[3].metric("Số lượt", len(data.get("turns", [])))
    st.caption(f"artifact: `{data.get('artifact_version', '-')}`")
    st.download_button("Tải file JSON", path.read_bytes(), file_name=path.name, mime="application/json")

    for turn in data.get("turns", []):
        with st.expander(f"Lượt {turn.get('turn_index')}: {turn.get('user', '')[:80]}  [{turn.get('status')}]", expanded=False):
            st.markdown(f"**Người dùng:** {turn.get('user', '')}")
            for rnd in turn.get("rounds", []):
                calls = rnd.get("tool_calls") or []
                if calls:
                    st.markdown(f"Vòng {rnd.get('round')}: gọi " + ", ".join(f"`{c['name']}`" for c in calls))
                for event in rnd.get("tool_results") or []:
                    st.code(json.dumps({"tool": event.get("tool"), "args": event.get("args")}, ensure_ascii=False, indent=2), language="json")
                    st.json(event.get("result", {}), expanded=False)
            if turn.get("error"):
                st.error(turn["error"])
            if turn.get("assistant_text"):
                st.markdown("**Agent:**")
                st.markdown(turn["assistant_text"])
