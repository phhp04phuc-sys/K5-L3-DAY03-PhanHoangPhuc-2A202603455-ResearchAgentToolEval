from __future__ import annotations

from typing import Any

import requests

from tools._shared import TIMEOUT, err
from tools.source_trust import annotate_items

HN_ALGOLIA = "https://hn.algolia.com/api/v1"
MAX_LIMIT = 20


def _clean_limit(limit: Any, default: int = 5) -> int:
    """Model hay gửi số dạng chuỗi hoặc ngoài khoảng: ép về 1..MAX_LIMIT thay vì lỗi."""
    try:
        value = int(limit)
    except (TypeError, ValueError):
        return default
    return max(1, min(value, MAX_LIMIT))


def _story_item(hit: dict[str, Any]) -> dict[str, Any]:
    object_id = hit.get("objectID") or ""
    hn_url = f"https://news.ycombinator.com/item?id={object_id}" if object_id else ""
    points = hit.get("points") or 0
    comments = hit.get("num_comments") or 0
    return {
        "title": (hit.get("title") or hit.get("story_title") or "").strip(),
        "url": hit.get("url") or hn_url,
        "source": "news.ycombinator.com",
        "summary": f"{points} điểm, {comments} bình luận. Thảo luận: {hn_url}" if hn_url else f"{points} điểm, {comments} bình luận",
        "date": hit.get("created_at"),
    }


def search_hacker_news(query: str = "", sort_by: str = "top", limit: int = 5) -> dict[str, Any]:
    """Tin từ Hacker News. Không có query: trang nhất (top) hoặc bài mới nhất (latest).
    Có query: tìm bài theo từ khóa. Dùng API Algolia công khai, không cần key."""
    try:
        sort = (sort_by or "top").strip().lower()
        if sort not in {"top", "latest"}:
            sort = "top"
        n = _clean_limit(limit)
        text = " ".join((query or "").split())
        params: dict[str, Any] = {"hitsPerPage": n}
        if text:
            params.update({"query": text, "tags": "story"})
            endpoint = "search" if sort == "top" else "search_by_date"
        elif sort == "top":
            params["tags"] = "front_page"
            endpoint = "search"
        else:
            params["tags"] = "story"
            endpoint = "search_by_date"
        response = requests.get(f"{HN_ALGOLIA}/{endpoint}", params=params, timeout=TIMEOUT)
        response.raise_for_status()
        hits = response.json().get("hits", [])
        items = [_story_item(hit) for hit in hits if hit.get("title") or hit.get("story_title")]
        return {"tool": "search_hacker_news", "query": text, "sort_by": sort, "items": annotate_items(items[:n], force_tier="tier3")}
    except Exception as exc:
        return err("search_hacker_news", exc)
