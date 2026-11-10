from __future__ import annotations

import os
from typing import Any

import requests

from tools._shared import TIMEOUT, err


GITHUB_SEARCH_API_URL = "https://api.github.com/search/repositories"
ALLOWED_SORTS = {"stars", "forks", "updated", "best-match"}


def search_github_repos(
    query: str = "",
    sort: str = "stars",
    max_results: int = 5,
) -> dict[str, Any]:
    try:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string")
        cleaned_query = " ".join(query.strip().split())

        parsed_max = int(max_results) if max_results is not None else 5
        if parsed_max <= 0:
            raise ValueError("max_results must be a positive integer")
        bounded_max = max(1, min(parsed_max, 10))

        normalized_sort = sort if isinstance(sort, str) and sort in ALLOWED_SORTS else "stars"

        params: dict[str, Any] = {
            "q": cleaned_query,
            "per_page": bounded_max,
            "order": "desc",
        }
        if normalized_sort != "best-match":
            params["sort"] = normalized_sort

        headers: dict[str, str] = {
            "Accept": "application/vnd.github+json",
            "User-Agent": os.getenv("GITHUB_USER_AGENT", "AI20k-Day03-Research-Agent/1.0"),
        }
        token = os.getenv("GITHUB_TOKEN", "").strip()
        if token:
            headers["Authorization"] = f"Bearer {token}"

        response = requests.get(
            GITHUB_SEARCH_API_URL,
            params=params,
            headers=headers,
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        payload = response.json()

        raw_items = payload.get("items") or []
        items: list[dict[str, Any]] = []
        for repo in raw_items[:bounded_max]:
            full_name = repo.get("full_name") or repo.get("name") or ""
            html_url = repo.get("html_url") or ""
            description = (repo.get("description") or "").strip()
            items.append({
                "name": full_name,
                "title": full_name,
                "url": html_url,
                "source": "github.com",
                "summary": description,
                "stars": int(repo.get("stargazers_count") or 0),
                "forks": int(repo.get("forks_count") or 0),
                "language": repo.get("language"),
            })

        return {
            "tool": "github_search",
            "query": cleaned_query,
            "sort": normalized_sort,
            "total_count": int(payload.get("total_count", len(items))),
            "items": items,
        }
    except Exception as exc:
        return err("github_search", exc)

