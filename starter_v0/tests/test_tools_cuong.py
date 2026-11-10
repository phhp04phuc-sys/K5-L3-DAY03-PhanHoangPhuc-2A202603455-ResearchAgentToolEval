"""Offline unit tests for Nguyen Tien Cuong's new tools (sentiment, extract_keywords)."""
from __future__ import annotations

from tools import TOOL_FUNCTIONS


# ---------------- sentiment ----------------

def test_sentiment_happy_path_english_and_vietnamese() -> None:
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


def test_sentiment_bad_input_type_returns_error_dict() -> None:
    sentiment_tool = TOOL_FUNCTIONS["sentiment"]
    res = sentiment_tool(text=12345)  # type: ignore[arg-type]
    assert res["status"] == "error"
    assert res["error"] == "TypeError"


def test_sentiment_empty_input_returns_error_dict() -> None:
    sentiment_tool = TOOL_FUNCTIONS["sentiment"]
    res = sentiment_tool(text="   ")
    assert res["status"] == "error"
    assert res["error"] == "ValueError"


# ---------------- extract_keywords ----------------

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
    res_bad_text = kw_tool(text=999, top_n=5)  # type: ignore[arg-type]
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
