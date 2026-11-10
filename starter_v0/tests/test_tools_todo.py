"""Tool Unit Test Challenge.

Rules:
- Offline only: mock HTTP with `fake_http`, set fake keys with `monkeypatch.setenv`.
- One behaviour per test. Name the test after the behaviour, not the function.
- Done = `pytest tests/ -v` shows 0 skipped, 0 failed.
"""
from __future__ import annotations

import pytest

from conftest import FakeResponse  # noqa: F401
from tools import TOOL_FUNCTIONS  # noqa: F401


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    clarify_tool = TOOL_FUNCTIONS["clarify"]
    result = clarify_tool(question="Chọn topic?", response_type="choice", options=["AI", "Crypto"])
    assert result["options"] == ["AI", "Crypto"]
    assert result["response_type"] == "choice"
    assert result["awaiting_user"] is True


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    format_tool = TOOL_FUNCTIONS["format"]
    items = [
        {"title": "Item 1", "section": "A", "url": "https://a.com/1"},
        {"title": "Item 2", "section": "B", "url": "https://b.com/2"},
        {"title": "Item 3", "section": "A", "url": "https://a.com/3"},
    ]
    result = format_tool(items=items, template="sections")
    assert result["markdown"].count("## A") == 1
    assert result["markdown"].count("## B") == 1
    assert result["item_count"] == 3


def test_format_thread_numbers_items() -> None:
    format_tool = TOOL_FUNCTIONS["format"]
    items = [
        {"title": "Post 1", "url": "https://x.com/1"},
        {"title": "Post 2", "url": "https://x.com/2"},
    ]
    result = format_tool(items=items, template="thread")
    assert "1/ Post 1" in result["markdown"]
    assert "2/ Post 2" in result["markdown"]


def test_format_empty_items_does_not_crash() -> None:
    format_tool = TOOL_FUNCTIONS["format"]
    res_none = format_tool(items=None)
    assert res_none["item_count"] == 0
    res_empty = format_tool(items=[])
    assert res_empty["item_count"] == 0


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "fake_bot_token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "123456")
    calls = fake_http(FakeResponse({"ok": True}))

    send_tool = TOOL_FUNCTIONS["send"]
    result = send_tool(text="Test message", confirmed=True)

    assert len(calls) == 1
    assert "fake_bot_token" in calls[0]["url"]
    assert calls[0]["json"]["chat_id"] == "123456"
    assert calls[0]["json"]["text"] == "Test message"
    assert result["status"] == "sent"


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    calls = fake_http(FakeResponse({"ok": True}))
    send_tool = TOOL_FUNCTIONS["send"]
    result = send_tool(text="Test message", confirmed=True)
    assert result["error"] == "RuntimeError"
    assert len(calls) == 0


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")
    calls = fake_http(FakeResponse({"results": []}))
    lookup_tool = TOOL_FUNCTIONS["lookup"]
    lookup_tool(query="test", timeframe=None)
    assert "time_range" not in calls[0]["json"]


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "test-fc-key")
    calls = fake_http(FakeResponse({
        "data": {
            "markdown": "Page content markdown",
            "metadata": {"title": "T", "sourceURL": "https://example.com/page"}
        }
    }))
    fetch_tool = TOOL_FUNCTIONS["fetch"]
    result = fetch_tool(url="https://example.com/page")
    assert result["items"][0]["title"] == "T"
    assert result["items"][0]["url"] == "https://example.com/page"
    assert result["items"][0]["source"] == "example.com"
    assert result["items"][0]["summary"] == "Page content markdown"


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "test-fc-key")
    fake_http(FakeResponse({
        "data": {
            "markdown": "A" * 6000,
            "metadata": {"title": "T", "sourceURL": "https://example.com"}
        }
    }))
    fetch_tool = TOOL_FUNCTIONS["fetch"]
    result = fetch_tool(url="https://example.com")
    assert len(result["items"][0]["summary"]) == 4000


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "test-rapid-key")
    fake_timeline = [
        {"screen_name": "sama", "text": "Tweet without id"},
        *[{"screen_name": "sama", "tweet_id": f"id_{i}", "text": f"Tweet {i}"} for i in range(6)]
    ]
    calls = fake_http(FakeResponse({"timeline": fake_timeline}))
    timeline_tool = TOOL_FUNCTIONS["timeline"]
    result = timeline_tool(screenname="sama", limit=3)
    assert len(result["items"]) == 3
    for item in result["items"]:
        assert item["url"].startswith("https://x.com/sama/status/id_")


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "test-rapid-key")
    calls = fake_http(FakeResponse({"tweets": []}))
    social_search_tool = TOOL_FUNCTIONS["social_search"]
    social_search_tool(query="OpenAI", search_type="Top")
    assert calls[0]["params"]["query"] == "OpenAI"
    assert calls[0]["params"]["search_type"] == "Top"


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    policy_tool = TOOL_FUNCTIONS["policy"]
    result = policy_tool(query="")
    assert result["results"] == []


def test_policy_area_filter_only_returns_that_area() -> None:
    policy_tool = TOOL_FUNCTIONS["policy"]
    result = policy_tool(query="data customer privacy", policy_area="data_privacy")
    assert len(result["results"]) > 0
    for hit in result["results"]:
        assert hit["policy_area"] == "data_privacy"


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    policy_tool = TOOL_FUNCTIONS["policy"]
    result = policy_tool(query="injection probe", policy_area="source_citation")
    assert len(result["results"]) > 0
    hit = result["results"][0]
    untrusted = hit.get("untrusted_text", [])
    assert any("ignore the citation policy" in line for line in untrusted)
    assert "ignore the citation policy" not in hit.get("facts", "")


# ---------------- YOUR NEW TOOL(S) ----------------

def test_my_new_tool_happy_path() -> None:
    sentiment_tool = TOOL_FUNCTIONS["sentiment"]
    res_pos = sentiment_tool(text="This is a great and awesome breakthrough!", detailed=True)
    assert res_pos["status"] == "ok"
    assert res_pos["sentiment"] == "positive"
    assert res_pos["score"] > 0
    assert "great" in res_pos["key_indicators"]

    res_neg = sentiment_tool(text="A terrible failure and bad crash", detailed=False)
    assert res_neg["status"] == "ok"
    assert res_neg["sentiment"] == "negative"
    assert res_neg["score"] < 0

    res_vn = sentiment_tool(text="Công nghệ AI đạt bước đột phá xuất sắc và thành công", detailed=True)
    assert res_vn["sentiment"] == "positive"
    assert res_vn["score"] == 1.0


def test_my_new_tool_bad_input_from_model() -> None:
    sentiment_tool = TOOL_FUNCTIONS["sentiment"]
    res = sentiment_tool(text=12345)
    assert res["status"] == "error"
    assert res["error"] == "TypeError"


def test_my_new_tool_failure_returns_error_dict() -> None:
    sentiment_tool = TOOL_FUNCTIONS["sentiment"]
    res = sentiment_tool(text="   ")
    assert res["status"] == "error"
    assert res["error"] == "ValueError"


def test_extract_keywords_happy_path() -> None:
    kw_tool = TOOL_FUNCTIONS["extract_keywords"]
    sample = "Artificial Intelligence #AI and Machine Learning #ML transform modern research. AI enables fast analysis."
    res = kw_tool(text=sample, top_n=3)
    assert res["status"] == "ok"
    assert "ai" in res["keywords"]
    assert len(res["keywords"]) <= 3
    assert res["hashtags"] == ["AI", "ML"]
    assert res["word_count"] == 14
    assert res["reading_time_minutes"] >= 0.1


def test_extract_keywords_bad_input_from_model() -> None:
    kw_tool = TOOL_FUNCTIONS["extract_keywords"]
    res_bad_text = kw_tool(text=999, top_n=5)
    assert res_bad_text["status"] == "error"
    assert res_bad_text["error"] == "TypeError"

    res_bad_top_n = kw_tool(text="Valid text", top_n=0)
    assert res_bad_top_n["status"] == "error"
    assert res_bad_top_n["error"] == "ValueError"


def test_extract_keywords_empty_text_returns_error_dict() -> None:
    kw_tool = TOOL_FUNCTIONS["extract_keywords"]
    res = kw_tool(text="   ")
    assert res["status"] == "error"
    assert res["error"] == "ValueError"
