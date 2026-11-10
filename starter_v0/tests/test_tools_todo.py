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


# ---------------- TOOL MỚI: hackernews ----------------
# Mỗi tool mới có: happy path, input xấu từ model, nhánh lỗi (trả error dict, không raise).

hackernews_tool = TOOL_FUNCTIONS["hackernews"]
wikipedia_tool = TOOL_FUNCTIONS["wikipedia"]

HN_HITS = {"hits": [
    {"objectID": "101", "title": "Rust 2.0 released", "url": "https://example.com/rust", "points": 420,
     "num_comments": 88, "created_at": "2026-11-10T01:00:00Z"},
    {"objectID": "102", "title": "Ask HN: Best way to learn Go?", "url": None, "points": 12, "num_comments": 3},
    {"objectID": "103", "title": None, "story_title": None},  # không có tiêu đề: phải bị bỏ qua
]}


def test_hackernews_front_page_maps_stories(fake_http) -> None:
    calls = fake_http(FakeResponse(HN_HITS))

    result = hackernews_tool(limit=5)

    assert calls[0]["url"] == "https://hn.algolia.com/api/v1/search"
    assert calls[0]["params"]["tags"] == "front_page"
    assert [item["title"] for item in result["items"]] == ["Rust 2.0 released", "Ask HN: Best way to learn Go?"]
    assert result["items"][0]["url"] == "https://example.com/rust"
    assert "420 điểm" in result["items"][0]["summary"]
    # bài không có url ngoài thì trỏ về trang thảo luận trên HN
    assert result["items"][1]["url"] == "https://news.ycombinator.com/item?id=102"


def test_hackernews_query_searches_stories_and_latest_uses_date_endpoint(fake_http) -> None:
    calls = fake_http(FakeResponse({"hits": []}))

    hackernews_tool(query="  Rust   async ", sort_by="latest", limit=3)

    assert calls[0]["url"] == "https://hn.algolia.com/api/v1/search_by_date"
    assert calls[0]["params"]["query"] == "Rust async"
    assert calls[0]["params"]["tags"] == "story"
    assert calls[0]["params"]["hitsPerPage"] == 3


def test_hackernews_bad_input_from_model_is_clamped_not_crashed(fake_http) -> None:
    calls = fake_http(FakeResponse({"hits": []}))

    hackernews_tool(sort_by="hottest", limit=999)
    hackernews_tool(limit="abc")
    hackernews_tool(limit=0)

    assert calls[0]["params"]["hitsPerPage"] == 20          # vượt khoảng: ép về 20
    assert calls[0]["params"]["tags"] == "front_page"       # sort_by lạ: về top
    assert calls[1]["params"]["hitsPerPage"] == 5           # không phải số: mặc định 5
    assert calls[2]["params"]["hitsPerPage"] == 1           # 0: ép lên 1


def test_hackernews_http_error_returns_error_dict(fake_http) -> None:
    fake_http(FakeResponse(status_code=503))

    result = hackernews_tool(query="Rust")

    assert result["error"] == "HTTPError"
    assert "items" not in result


# ---------------- TOOL MỚI: wikipedia ----------------

WIKI_PAGE = {"query": {"pages": {"5042481": {
    "title": "Rust (programming language)",
    "extract": "Rust is a general-purpose programming language emphasizing performance and safety.",
}}}}


def test_wikipedia_maps_summary_and_builds_url(fake_http) -> None:
    calls = fake_http(FakeResponse(WIKI_PAGE))

    result = wikipedia_tool(query="Rust language", lang="en")

    assert calls[0]["url"] == "https://en.wikipedia.org/w/api.php"
    assert calls[0]["params"]["gsrsearch"] == "Rust language"
    assert "User-Agent" in calls[0]["headers"]
    item = result["items"][0]
    assert item["title"] == "Rust (programming language)"
    assert item["url"] == "https://en.wikipedia.org/wiki/Rust_%28programming_language%29"
    assert item["source"] == "en.wikipedia.org"
    assert item["summary"].startswith("Rust is a general-purpose")


def test_wikipedia_invalid_lang_falls_back_to_en_and_cannot_change_host(fake_http) -> None:
    calls = fake_http(FakeResponse(WIKI_PAGE))

    wikipedia_tool(query="Rust", lang="evil.com/x?")
    wikipedia_tool(query="Rust", lang="VI")

    assert calls[0]["url"] == "https://en.wikipedia.org/w/api.php"   # lang xấu: về en, không đổi tên miền
    assert calls[1]["url"] == "https://vi.wikipedia.org/w/api.php"   # chữ hoa được chuẩn hóa


def test_wikipedia_truncates_summary_to_max_chars(fake_http) -> None:
    fake_http(FakeResponse({"query": {"pages": {"1": {"title": "X", "extract": "a" * 3000}}}}))

    result = wikipedia_tool(query="X", max_chars=200)

    assert len(result["items"][0]["summary"]) == 200
    assert result["items"][0]["summary"].endswith("...")


def test_wikipedia_empty_query_and_not_found_return_error_dict(fake_http) -> None:
    calls = fake_http(FakeResponse({"batchcomplete": ""}))   # API không có khóa "query" khi không tìm thấy

    empty = wikipedia_tool(query="   ")
    missing = wikipedia_tool(query="zzzxqj no such page")

    assert empty["error"] == "EmptyQuery"
    assert len(calls) == 1               # query rỗng không gọi mạng
    assert missing["error"] == "NotFound"


def test_wikipedia_http_error_returns_error_dict(fake_http) -> None:
    fake_http(FakeResponse(status_code=429))

    assert wikipedia_tool(query="Rust")["error"] == "HTTPError"


# ---------------- TOOL MỚI: math_solve ----------------

math_tool = TOOL_FUNCTIONS["math_solve"]


def test_math_evaluate_returns_exact_and_numeric() -> None:
    assert math_tool(expression="(3+4)*5^2")["result"] == "175"
    root = math_tool(expression="sqrt(2)")
    assert root["result"] == "sqrt(2)"
    assert root["numeric"] == pytest.approx(1.4142135624)


def test_math_solve_equation_returns_all_roots_and_implicit_multiplication() -> None:
    assert math_tool(expression="2x+6=0", task="solve")["solutions"] == ["-3"]
    assert sorted(math_tool(expression="x^2-5x+6=0", task="solve")["solutions"]) == ["2", "3"]


def test_math_derivative_and_integral_use_variable_and_integral_mentions_constant() -> None:
    assert math_tool(expression="x^3", task="derivative")["result"] == "3*x^2"
    integral = math_tool(expression="x^2", task="integral")
    assert integral["result"] == "x^3/3"
    assert "C" in integral["note"]
    assert math_tool(expression="t^2", task="derivative", variable="t")["result"] == "2*t"


def test_math_factor_and_simplify() -> None:
    assert math_tool(expression="x^2-9", task="factor")["result"] == "(x - 3)*(x + 3)"
    assert math_tool(expression="x+x+x", task="simplify")["result"] == "3*x"


@pytest.mark.parametrize("evil", [
    "__import__('os').system('ls')",
    "open('/etc/passwd')",
    "Integer(5)",
    "x.__class__",
    "exec(1)",
    "lambda: 1",
])
def test_math_rejects_code_injection_and_unknown_names(evil: str) -> None:
    result = math_tool(expression=evil)
    assert result["error"] == "InvalidExpression"
    assert "result" not in result


def test_math_blocks_huge_or_nested_powers_and_long_input() -> None:
    assert math_tool(expression="9^9^9")["error"] == "InvalidExpression"
    assert math_tool(expression="2^100000")["error"] == "InvalidExpression"
    assert math_tool(expression="1+" * 200 + "1")["error"] == "InvalidExpression"


def test_math_empty_division_by_zero_and_bad_equation_return_error_dict() -> None:
    assert math_tool(expression="   ")["error"] == "InvalidExpression"
    assert math_tool(expression="1/0")["error"] == "InvalidExpression"
    assert math_tool(expression="1=2=3", task="solve")["error"] == "InvalidExpression"


def test_math_bad_task_and_bad_variable_fall_back_to_defaults() -> None:
    assert math_tool(expression="2+2", task="teleport")["result"] == "4"
    assert math_tool(expression="x^2", task="derivative", variable="xyz")["variable"] == "x"


# ---------------- Phân tầng nguồn uy tín (tools/source_trust.py) ----------------

from tools.source_trust import TRUSTED_DOMAINS, annotate_items, source_tier  # noqa: E402


@pytest.mark.parametrize("url,tier", [
    ("https://www.openai.com/blog/x", "tier1"),
    ("https://arxiv.org/abs/1706.03762", "tier1"),
    ("https://moh.gov.vn/tin-tuc", "tier1"),
    ("https://hust.edu.vn/", "tier1"),
    ("https://www.reuters.com/world/a", "tier2"),
    ("https://vnexpress.net/b", "tier2"),
    ("https://x.com/sama/status/1", "tier3"),
    ("https://news.ycombinator.com/item?id=1", "tier3"),
    ("https://random-blog.xyz/post", "unverified"),
])
def test_source_tier_classifies_primary_news_social_and_unknown(url: str, tier: str) -> None:
    assert source_tier(url) == tier


@pytest.mark.parametrize("url", [
    "https://evilopenai.com/blog",
    "https://openai.com.evil.io/blog",
    "https://fake.gov.evil.com/",
    "https://reuters.com.phish.net/",
])
def test_source_tier_rejects_lookalike_domains(url: str) -> None:
    assert source_tier(url) == "unverified"


def test_source_tier_handles_empty_and_garbage_urls() -> None:
    assert source_tier("") == "unverified"
    assert source_tier("not a url") == "unverified"
    assert source_tier(None) == "unverified"  # type: ignore[arg-type]


def test_annotate_items_adds_tier_and_note_and_force_tier_overrides() -> None:
    items = annotate_items([{"url": "https://reuters.com/a"}])
    assert items[0]["source_tier"] == "tier2"
    assert "uy tín" in items[0]["tier_note"]
    forced = annotate_items([{"url": "https://reuters.com/a"}], force_tier="tier3")
    assert forced[0]["source_tier"] == "tier3"
    assert "chưa xác nhận" in forced[0]["tier_note"]


def test_lookup_labels_each_item_with_its_source_tier(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")
    fake_http(FakeResponse({"results": [
        {"title": "Official", "url": "https://openai.com/index/x", "content": "a", "score": 0.9},
        {"title": "Forum", "url": "https://www.reddit.com/r/x", "content": "b", "score": 0.5},
        {"title": "Unknown", "url": "https://unknown-site.xyz/p", "content": "c", "score": 0.4},
    ]}))

    result = lookup_tool(query="OpenAI")

    assert [item["source_tier"] for item in result["items"]] == ["tier1", "tier3", "unverified"]


def test_lookup_trusted_only_sends_include_domains_only_when_true(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")
    calls = fake_http(FakeResponse({"results": []}))

    lookup_tool(query="x", trusted_only=True)
    lookup_tool(query="x")
    lookup_tool(query="x", trusted_only="true")   # chuỗi từ model không được coi là True

    assert calls[0]["json"]["include_domains"] == TRUSTED_DOMAINS
    assert "reuters.com" in calls[0]["json"]["include_domains"]
    assert "include_domains" not in calls[1]["json"]
    assert "include_domains" not in calls[2]["json"]


def test_social_and_community_tools_are_always_tier3_and_wikipedia_tier2(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "test-key")
    fake_http(FakeResponse({"timeline": [{"tweet_id": "1", "screen_name": "sama", "text": "hi"}]}))
    assert timeline_tool(screenname="sama")["items"][0]["source_tier"] == "tier3"

    fake_http(FakeResponse(HN_HITS))
    assert {i["source_tier"] for i in hackernews_tool()["items"]} == {"tier3"}

    fake_http(FakeResponse(WIKI_PAGE))
    assert wikipedia_tool(query="Rust")["items"][0]["source_tier"] == "tier2"
