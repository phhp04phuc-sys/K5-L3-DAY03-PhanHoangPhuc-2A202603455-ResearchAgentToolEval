from __future__ import annotations

from typing import Any

import requests

from tools._shared import TIMEOUT, err

HN_ALGOLIA_URL = "https://hn.algolia.com/api/v1/search"


def search_hacker_news(query: str = "", max_results: int = 5) -> dict[str, Any]:
    """Search tech discussions and stories on Hacker News via Algolia API."""
    cleaned_query = str(query or "").strip()
    if not cleaned_query:
        return err("hn_search", ValueError("query is required and must be non-empty"))

    try:
        parsed_max = int(max_results)
    except (TypeError, ValueError):
        return err("hn_search", ValueError("max_results must be a positive integer"))

    if parsed_max <= 0:
        return err("hn_search", ValueError("max_results must be greater than 0"))

    bounded_max = min(parsed_max, 10)

    try:
        response = requests.get(
            HN_ALGOLIA_URL,
            params={
                "query": cleaned_query,
                "tags": "story",
                "hitsPerPage": bounded_max,
            },
            headers={"Accept": "application/json", "User-Agent": "ResearchAgentToolEval/2.0"},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            return err("hn_search", RuntimeError("Unexpected response format from Hacker News API"))

        raw_hits = payload.get("hits") or []
        items: list[dict[str, Any]] = []
        for hit in raw_hits[:bounded_max]:
            if not isinstance(hit, dict):
                continue
            object_id = str(hit.get("objectID") or "")
            hn_url = f"https://news.ycombinator.com/item?id={object_id}" if object_id else ""
            story_url = str(hit.get("url") or hn_url)
            title = str(hit.get("title") or hit.get("story_title") or "Untitled HN Story").strip()
            points = int(hit.get("points") or 0)
            num_comments = int(hit.get("num_comments") or 0)
            author = str(hit.get("author") or "unknown")
            items.append(
                {
                    "title": title,
                    "url": story_url,
                    "hn_url": hn_url,
                    "source": "Hacker News",
                    "points": points,
                    "num_comments": num_comments,
                    "author": author,
                    "summary": f"{title} ({points} points, {num_comments} comments by {author})",
                }
            )

        return {
            "tool": "hn_search",
            "query": cleaned_query,
            "total_hits": int(payload.get("nbHits", len(items))),
            "items": items,
        }
    except Exception as exc:
        return err("hn_search", exc)
