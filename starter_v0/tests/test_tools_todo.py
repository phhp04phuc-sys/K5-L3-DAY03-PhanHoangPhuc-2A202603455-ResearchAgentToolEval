"""Unit tests cho các tool có sẵn (Tool Unit Test Challenge).

Quy tắc:
- Offline: HTTP được mock bằng `fake_http`, key giả đặt bằng `monkeypatch.setenv`.
- Mỗi test kiểm tra một hành vi, tên test mô tả hành vi đó.
- Test cho tool MỚI của nhóm nằm ở cuối file (còn skip cho tới khi tool được viết).
"""
from __future__ import annotations

import pytest

from conftest import FakeResponse
from tools import TOOL_FUNCTIONS

clarify_tool = TOOL_FUNCTIONS["clarify"]
format_tool = TOOL_FUNCTIONS["format"]
send_tool = TOOL_FUNCTIONS["send"]
lookup_tool = TOOL_FUNCTIONS["lookup"]
fetch_tool = TOOL_FUNCTIONS["fetch"]
timeline_tool = TOOL_FUNCTIONS["timeline"]
social_search_tool = TOOL_FUNCTIONS["social_search"]
policy_tool = TOOL_FUNCTIONS["policy"]

TODO = "TODO(student): viết sau khi nhóm có tool mới"


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    result = clarify_tool(question="Chọn một", response_type="choice", options=["A", "B"])

    assert result["options"] == ["A", "B"]
    assert result["response_type"] == "choice"
    assert result["awaiting_user"] is True


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    items = [
        {"title": "1", "section": "A"},
        {"title": "2", "section": "B"},
        {"title": "3", "section": "A"},
    ]
    markdown = format_tool(items=items, template="sections")["markdown"]

    assert markdown.count("## A") == 1
    assert markdown.count("## B") == 1


def test_format_thread_numbers_items() -> None:
    items = [{"title": "đầu"}, {"title": "hai"}, {"title": "ba"}]
    markdown = format_tool(items=items, template="thread")["markdown"]

    assert markdown.startswith("1/")
    assert "\n\n2/" in markdown
    assert "\n\n3/" in markdown


def test_format_empty_items_does_not_crash() -> None:
    assert format_tool(items=None, template="sections")["item_count"] == 0
    assert format_tool(items=[], template="brief")["item_count"] == 0


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "tok123")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "@kenh_test")
    calls = fake_http(FakeResponse({"ok": True}))

    result = send_tool(text="Bản tin sáng", confirmed=True)

    assert len(calls) == 1
    assert calls[0]["method"] == "POST"
    assert "tok123" in calls[0]["url"]
    assert calls[0]["json"]["chat_id"] == "@kenh_test"
    assert calls[0]["json"]["text"] == "Bản tin sáng"
    assert result["status"] == "sent"


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    calls = fake_http(FakeResponse({"ok": True}))

    result = send_tool(text="Bản tin", confirmed=True)

    assert result["error"] == "RuntimeError"
    assert "TELEGRAM_BOT_TOKEN" in result["message"]
    assert calls == []


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")
    calls = fake_http(FakeResponse({"results": []}))

    lookup_tool(query="AI", topic="general", timeframe=None)

    assert "time_range" not in calls[0]["json"]


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")
    calls = fake_http(FakeResponse({"data": {
        "markdown": "# Nội dung",
        "metadata": {"title": "Tiêu đề", "sourceURL": "https://www.example.com/a"},
    }}))

    result = fetch_tool(url="https://www.example.com/a")

    assert calls[0]["url"] == "https://api.firecrawl.dev/v1/scrape"
    assert calls[0]["json"]["url"] == "https://www.example.com/a"
    item = result["items"][0]
    assert item["title"] == "Tiêu đề"
    assert item["url"] == "https://www.example.com/a"
    assert item["source"] == "example.com"
    assert item["summary"] == "# Nội dung"


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")
    fake_http(FakeResponse({"data": {"markdown": "x" * 5000, "metadata": {}}}))

    result = fetch_tool(url="https://example.com/long")

    assert len(result["items"][0]["summary"]) == 4000


# ---------------- timeline / social_search ----------------

def _raw_tweets(valid: int) -> list[dict]:
    broken = {"screen_name": "sama", "text": "không có id"}
    good = [{"tweet_id": str(100 + i), "screen_name": "sama", "text": f"tweet {i}"} for i in range(valid)]
    return [broken, *good]


def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "test-key")
    fake_http(FakeResponse({"timeline": _raw_tweets(valid=6)}))

    result = timeline_tool(screenname="sama", limit=3)

    assert len(result["items"]) == 3
    for item in result["items"]:
        assert item["url"].startswith("https://x.com/sama/status/")
        assert item["source"] == "@sama"


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "test-key")
    calls = fake_http(FakeResponse({"timeline": []}))

    social_search_tool(query="OpenAI", search_type="Top")

    assert calls[0]["params"] == {"query": "OpenAI", "search_type": "Top"}
    assert calls[0]["headers"]["x-rapidapi-key"] == "test-key"


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    assert policy_tool(query="")["results"] == []
    assert policy_tool(query="   ")["results"] == []


def test_policy_area_filter_only_returns_that_area() -> None:
    result = policy_tool(query="privacy customer data", policy_area="data_privacy")

    assert result["results"], "phải có ít nhất một kết quả"
    assert all(hit["policy_area"] == "data_privacy" for hit in result["results"])


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    result = policy_tool(query="injection probe", policy_area="source_citation")

    probe = [hit for hit in result["results"] if hit["section"] == "Injection probe"]
    assert probe, "section 'Injection probe' phải được tìm thấy"
    assert any("ignore the citation policy" in line.lower() for line in probe[0]["untrusted_text"])
    assert "ignore" not in probe[0]["facts"].lower()


# ---------------- YOUR NEW TOOL(S) ----------------
# Mỗi tool mới của nhóm cần >= 3 test:
#   1. happy path (mock HTTP nếu gọi API)
#   2. input xấu từ model (chuỗi rỗng, sai kiểu, ngoài enum)
#   3. nhánh lỗi (thiếu key, HTTP error, timeout) -> trả error dict, không raise
# Thay các stub dưới đây khi tool mới đã được đăng ký trong tools/__init__.py.

def test_my_new_tool_happy_path() -> None:
    pytest.skip(TODO)


def test_my_new_tool_bad_input_from_model() -> None:
    pytest.skip(TODO)


def test_my_new_tool_failure_returns_error_dict() -> None:
    pytest.skip(TODO)
