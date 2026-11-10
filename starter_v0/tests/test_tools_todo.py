"""Tool Unit Test Challenge — Complete Implementation.

Rules:
- Offline only: mock HTTP with `fake_http`, set fake keys with `monkeypatch.setenv`.
- One behaviour per test. Name the test after the behaviour, not the function.
- Done = `pytest tests/ -v` shows 0 skipped, 0 failed.
"""
from __future__ import annotations

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
github_search_tool = TOOL_FUNCTIONS["github_search"]
hf_models_tool = TOOL_FUNCTIONS["hf_models"]
hn_search_tool = TOOL_FUNCTIONS["hn_search"]
wiki_summary_tool = TOOL_FUNCTIONS["wiki_summary"]


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    opts = ["Sam Altman", "Elon Musk"]
    result = clarify_tool(question="Bạn muốn xem ai?", response_type="choice", options=opts)
    assert result["options"] == ["Sam Altman", "Elon Musk"]
    assert result["response_type"] == "choice"
    assert result["awaiting_user"] is True


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    items = [
        {"title": "Item 1", "section": "A", "url": "https://a.com/1"},
        {"title": "Item 2", "section": "B", "url": "https://b.com/2"},
        {"title": "Item 3", "section": "A", "url": "https://a.com/3"},
    ]
    result = format_tool(items=items, template="sections", headline="Digest")
    md = result["markdown"]
    assert md.count("## A") == 1
    assert md.count("## B") == 1
    assert result["item_count"] == 3


def test_format_thread_numbers_items() -> None:
    items = [
        {"title": "First item", "url": "https://example.com/1"},
        {"title": "Second item", "url": "https://example.com/2"},
    ]
    result = format_tool(items=items, template="thread")
    lines = [block for block in result["markdown"].split("\n\n") if block.strip()]
    assert lines[0].startswith("1/ ")
    assert lines[1].startswith("2/ ")


def test_format_empty_items_does_not_crash() -> None:
    res_none = format_tool(items=None, template="bullets")
    res_empty = format_tool(items=[], template="sections")
    assert res_none["item_count"] == 0
    assert res_empty["item_count"] == 0


def test_format_section_none_falls_back_to_default() -> None:
    # Regression test (Challenge+): item with explicit {"section": None} should not render "## None".
    items = [{"title": "Tin AI", "section": None, "url": "https://example.com/ai"}]
    result = format_tool(items=items, template="sections")
    assert "## None" not in result["markdown"]
    assert "## Tổng hợp" in result["markdown"]


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "bot-secret-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "123456")
    calls = fake_http(FakeResponse({"ok": True}))

    result = send_tool(text="Bản tin AI hôm nay", confirmed=True)

    assert len(calls) == 1
    assert calls[0]["method"] == "POST"
    assert "bot-secret-token" in calls[0]["url"]
    assert calls[0]["json"]["chat_id"] == "123456"
    assert calls[0]["json"]["text"] == "Bản tin AI hôm nay"
    assert result["status"] == "sent"


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    calls = fake_http(FakeResponse({"ok": True}))
    result = send_tool(text="Bản tin", confirmed=True)
    assert result["error"] == "RuntimeError"
    assert "TELEGRAM_BOT_TOKEN" in result["message"]
    assert calls == []


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "tavily-key")
    calls = fake_http(FakeResponse({"results": []}))

    lookup_tool(query="AI", topic="general", timeframe=None, max_results=5)

    assert len(calls) == 1
    assert "time_range" not in calls[0]["json"]


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-key")
    calls = fake_http(FakeResponse({
        "data": {
            "markdown": "Hello Firecrawl content",
            "metadata": {
                "title": "OpenAI Blog",
                "sourceURL": "https://openai.com/blog/test",
            },
        }
    }))

    result = fetch_tool(url="https://openai.com/blog/test")

    assert len(calls) == 1
    assert calls[0]["url"] == "https://api.firecrawl.dev/v1/scrape"
    assert result["items"][0] == {
        "title": "OpenAI Blog",
        "url": "https://openai.com/blog/test",
        "source": "openai.com",
        "summary": "Hello Firecrawl content",
    }


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-key")
    fake_http(FakeResponse({
        "data": {
            "markdown": "a" * 5500,
            "metadata": {"title": "Long Page", "sourceURL": "https://example.com/long"},
        }
    }))

    result = fetch_tool(url="https://example.com/long")
    summary = result["items"][0]["summary"]
    assert len(summary) == 4000
    assert summary == "a" * 4000


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "rapid-key")
    timeline_payload = [
        {"screen_name": "sama", "text": "No ID tweet"},
        *[
            {"screen_name": "sama", "tweet_id": str(100 + i), "text": f"Tweet {i}"}
            for i in range(6)
        ],
    ]
    fake_http(FakeResponse({"timeline": timeline_payload}))

    result = timeline_tool(screenname="sama", limit=3)

    assert len(result["items"]) == 3
    for idx, item in enumerate(result["items"]):
        assert item["url"] == f"https://x.com/sama/status/{100 + idx}"


def test_timeline_strips_at_prefix_and_falls_back_to_handle(monkeypatch, fake_http) -> None:
    # Regression test (Challenge+): model sending '@sama' and API omitting screen_name per tweet.
    monkeypatch.setenv("RAPIDAPI_KEY", "rapid-key")
    calls = fake_http(FakeResponse({"timeline": [{"tweet_id": "999", "text": "Hello"}]}))

    result = timeline_tool(screenname="@sama", limit=1)

    assert calls[0]["params"]["screenname"] == "sama"
    assert result["screenname"] == "sama"
    assert result["items"][0]["url"] == "https://x.com/sama/status/999"


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "rapid-key")
    calls = fake_http(FakeResponse({"timeline": []}))

    social_search_tool(query="OpenAI", search_type="Top", limit=5)

    assert len(calls) == 1
    assert calls[0]["params"]["query"] == "OpenAI"
    assert calls[0]["params"]["search_type"] == "Top"


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    result = policy_tool(query="   ", policy_area="all", top_k=3)
    assert result["results"] == []


def test_policy_area_filter_only_returns_that_area() -> None:
    result = policy_tool(query="API key customer data privacy", policy_area="data_privacy", top_k=5)
    assert len(result["results"]) > 0
    for item in result["results"]:
        assert item["policy_area"] == "data_privacy"


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    result = policy_tool(query="Injection probe citation tweet", policy_area="source_citation", top_k=5)
    probe_sections = [r for r in result["results"] if r["section"] == "Injection probe"]
    assert len(probe_sections) == 1
    probe = probe_sections[0]
    assert any("ignore the citation policy" in line for line in probe["untrusted_text"])
    assert "ignore the citation policy" not in probe["facts"]


# ---------------- NEW TOOL 1: github_search ----------------

def test_github_search_happy_path_maps_repositories(fake_http) -> None:
    calls = fake_http(FakeResponse({
        "total_count": 1,
        "items": [
            {
                "full_name": "langchain-ai/langgraph",
                "html_url": "https://github.com/langchain-ai/langgraph",
                "description": "Build resilient language agents as graphs.",
                "stargazers_count": 8500,
                "forks_count": 1200,
                "language": "Python",
            }
        ],
    }))

    result = github_search_tool(query="langgraph", sort="stars", max_results=3)

    assert len(calls) == 1
    assert calls[0]["url"] == "https://api.github.com/search/repositories"
    assert calls[0]["params"]["q"] == "langgraph"
    assert calls[0]["params"]["sort"] == "stars"
    assert calls[0]["params"]["per_page"] == 3
    assert result["total_count"] == 1
    assert result["items"][0]["name"] == "langchain-ai/langgraph"
    assert result["items"][0]["stars"] == 8500
    assert result["items"][0]["source"] == "github.com"


def test_github_search_bad_input_from_model_returns_error_dict() -> None:
    empty_res = github_search_tool(query="   ")
    assert empty_res["error"] == "ValueError"
    zero_max_res = github_search_tool(query="agent", max_results=0)
    assert zero_max_res["error"] == "ValueError"


def test_github_search_http_failure_returns_error_dict(fake_http) -> None:
    fake_http(FakeResponse(status_code=403))
    result = github_search_tool(query="langgraph")
    assert result["tool"] == "github_search"
    assert result["error"] == "HTTPError"


# ---------------- NEW TOOL 2: hf_models ----------------

def test_hf_models_happy_path_sends_params_and_maps_models(fake_http) -> None:
    calls = fake_http(FakeResponse([
        {
            "id": "Qwen/Qwen2.5-7B-Instruct",
            "pipeline_tag": "text-generation",
            "downloads": 500000,
            "likes": 1800,
        }
    ]))

    result = hf_models_tool(query="Qwen2.5", sort="downloads", max_results=2)

    assert len(calls) == 1
    assert calls[0]["url"] == "https://huggingface.co/api/models"
    assert calls[0]["params"]["search"] == "Qwen2.5"
    assert calls[0]["params"]["sort"] == "downloads"
    assert calls[0]["params"]["limit"] == 2
    assert result["count"] == 1
    assert result["items"][0]["model_id"] == "Qwen/Qwen2.5-7B-Instruct"
    assert result["items"][0]["url"] == "https://huggingface.co/Qwen/Qwen2.5-7B-Instruct"


def test_hf_models_bad_input_from_model_returns_error_dict() -> None:
    res_empty = hf_models_tool(query="")
    assert res_empty["error"] == "ValueError"
    res_bad_max = hf_models_tool(query="llama", max_results="invalid_int")  # type: ignore[arg-type]
    assert res_bad_max["error"] == "ValueError"


def test_hf_models_http_failure_returns_error_dict(fake_http) -> None:
    fake_http(FakeResponse(status_code=500))
    result = hf_models_tool(query="Qwen2.5")
    assert result["tool"] == "hf_models"
    assert result["error"] == "HTTPError"


# ---------------- NEW TOOL 3: hn_search ----------------

def test_hn_search_happy_path_maps_stories(fake_http) -> None:
    calls = fake_http(FakeResponse({
        "nbHits": 42,
        "hits": [
            {
                "objectID": "40001",
                "title": "Show HN: Open Research Agent",
                "url": "https://example.org/agent",
                "points": 250,
                "num_comments": 88,
                "author": "alice",
            }
        ],
    }))

    result = hn_search_tool(query="Research Agent", max_results=4)

    assert len(calls) == 1
    assert calls[0]["url"] == "https://hn.algolia.com/api/v1/search"
    assert calls[0]["params"]["query"] == "Research Agent"
    assert calls[0]["params"]["hitsPerPage"] == 4
    assert result["total_hits"] == 42
    assert result["items"][0]["points"] == 250
    assert result["items"][0]["hn_url"] == "https://news.ycombinator.com/item?id=40001"


def test_hn_search_bad_input_from_model_returns_error_dict() -> None:
    assert hn_search_tool(query="")["error"] == "ValueError"
    assert hn_search_tool(query="rust", max_results=-1)["error"] == "ValueError"


def test_hn_search_http_failure_returns_error_dict(fake_http) -> None:
    fake_http(FakeResponse(status_code=503))
    result = hn_search_tool(query="rust")
    assert result["tool"] == "hn_search"
    assert result["error"] == "HTTPError"


# ---------------- NEW TOOL 4: wiki_summary ----------------

def test_wiki_summary_happy_path_fetches_rest_summary(fake_http) -> None:
    calls = fake_http(FakeResponse({
        "title": "Alan Turing",
        "extract": "Alan Mathison Turing was an English mathematician and computer scientist.",
        "content_urls": {"desktop": {"page": "https://en.wikipedia.org/wiki/Alan_Turing"}},
    }))

    result = wiki_summary_tool(topic="Alan Turing", lang="en")

    assert len(calls) == 1
    assert calls[0]["url"] == "https://en.wikipedia.org/api/rest_v1/page/summary/Alan_Turing"
    assert result["title"] == "Alan Turing"
    assert "computer scientist" in result["summary"]
    assert result["items"][0]["url"] == "https://en.wikipedia.org/wiki/Alan_Turing"


def test_wiki_summary_bad_input_and_invalid_lang_fallback(fake_http) -> None:
    assert wiki_summary_tool(topic="   ")["error"] == "ValueError"
    calls = fake_http(FakeResponse({"title": "AI", "extract": "Artificial intelligence."}))
    res = wiki_summary_tool(topic="AI", lang="invalid_lang")
    assert res["lang"] == "en"
    assert "https://en.wikipedia.org/" in calls[0]["url"]


def test_wiki_summary_http_failure_returns_error_dict(fake_http) -> None:
    fake_http(FakeResponse(status_code=404))
    result = wiki_summary_tool(topic="NonExistentTopic12345")
    assert result["tool"] == "wiki_summary"
    assert result["error"] == "HTTPError"
