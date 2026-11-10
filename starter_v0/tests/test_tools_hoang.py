"""Unit tests for tools contributed by Le Van Hoang (citation_format, url_check).
All tests run offline without network access.
"""
from __future__ import annotations

import pytest
from tools.citation_format.tool import format_citation
from tools.url_check.tool import validate_research_url


# --- citation_format tests ---

def test_citation_format_happy_path_markdown_apa_bibtex():
    """format_citation formats citations correctly into markdown, apa, and bibtex."""
    md = format_citation(
        title="Attention Is All You Need",
        url="https://arxiv.org/abs/1706.03762",
        author="Vaswani et al.",
        year="2017",
        style="markdown",
    )
    apa = format_citation(
        title="Attention Is All You Need",
        url="https://arxiv.org/abs/1706.03762",
        author="Vaswani et al.",
        year="2017",
        style="apa",
    )
    bib = format_citation(
        title="Attention Is All You Need",
        url="https://arxiv.org/abs/1706.03762",
        author="Vaswani et al.",
        year="2017",
        style="bibtex",
    )
    assert "[Attention Is All You Need](https://arxiv.org/abs/1706.03762)" in md["citation"]
    assert "Retrieved from https://arxiv.org/abs/1706.03762" in apa["citation"]
    assert "@misc{vaswani2017," in bib["citation"]


def test_citation_format_bad_input_from_model():
    """Missing title or non-http URL should return error dict."""
    err_title = format_citation(title="", url="https://arxiv.org/abs/1706.03762")
    err_url = format_citation(title="Paper", url="not-a-valid-url")
    assert "error" in err_title
    assert "error" in err_url


def test_citation_format_invalid_style():
    """Unsupported citation style returns error dict."""
    out = format_citation(
        title="Paper",
        url="https://arxiv.org/abs/1706.03762",
        style="invalid_style",
    )
    assert "error" in out
    assert out["error"] == "invalid_style"


# --- url_check tests ---

def test_url_check_happy_path_classifies_tiers():
    """validate_research_url classifies arxiv into tier_1, twitter into tier_3, others into tier_2."""
    tier1 = validate_research_url(url="https://arxiv.org/abs/1706.03762")
    tier3 = validate_research_url(url="https://x.com/sama/status/123456")
    tier2 = validate_research_url(url="https://techcrunch.com/2026/06/01/ai-news/")

    assert tier1["valid"] is True and tier1["source_tier"] == "tier_1"
    assert tier3["valid"] is True and tier3["source_tier"] == "tier_3"
    assert tier2["valid"] is True and tier2["source_tier"] == "tier_2"


def test_url_check_bad_input_from_model():
    """Empty or non-string url returns error dict."""
    out = validate_research_url(url="   ")
    assert "error" in out
    assert out["error"] == "invalid_input"


def test_url_check_rejects_non_http_or_malformed_url():
    """Non-http(s) schemes return error dict."""
    out = validate_research_url(url="ftp://files.example.com/data.pdf")
    assert "error" in out
    assert out["error"] == "invalid_url"
