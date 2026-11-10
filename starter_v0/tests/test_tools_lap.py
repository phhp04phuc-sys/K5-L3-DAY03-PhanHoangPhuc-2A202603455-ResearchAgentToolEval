"""Offline unit tests for Ly Thanh Lap's new tools (github_search, hf_models)."""
from __future__ import annotations

from conftest import FakeResponse
from tools import TOOL_FUNCTIONS

github_search_tool = TOOL_FUNCTIONS["github_search"]
hf_models_tool = TOOL_FUNCTIONS["hf_models"]


# ---------------- github_search ----------------

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


# ---------------- hf_models ----------------

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
