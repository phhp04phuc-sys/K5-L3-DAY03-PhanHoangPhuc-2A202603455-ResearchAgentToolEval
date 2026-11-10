from __future__ import annotations

from typing import Any
from urllib.parse import quote

import requests

from tools._shared import TIMEOUT, err


def get_wikipedia_summary(topic: str = "", lang: str = "en") -> dict[str, Any]:
    """Fetch a concise Wikipedia encyclopedia summary for a given topic or concept."""
    cleaned_topic = str(topic or "").strip()
    if not cleaned_topic:
        return err("wiki_summary", ValueError("topic is required and must be non-empty"))

    normalized_lang = str(lang or "en").strip().lower()
    if normalized_lang not in {"en", "vi"}:
        normalized_lang = "en"

    slug = quote(cleaned_topic.replace(" ", "_"), safe="")
    url = f"https://{normalized_lang}.wikipedia.org/api/rest_v1/page/summary/{slug}"

    try:
        response = requests.get(
            url,
            headers={"Accept": "application/json", "User-Agent": "ResearchAgentToolEval/2.0"},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            return err("wiki_summary", RuntimeError("Unexpected response format from Wikipedia API"))

        title = str(payload.get("title") or cleaned_topic)
        extract = str(payload.get("extract") or payload.get("description") or "").strip()
        content_urls = payload.get("content_urls") or {}
        desktop_url = (
            (content_urls.get("desktop") or {}).get("page")
            if isinstance(content_urls, dict)
            else None
        ) or f"https://{normalized_lang}.wikipedia.org/wiki/{slug}"

        item = {
            "title": title,
            "url": str(desktop_url),
            "source": f"Wikipedia ({normalized_lang})",
            "description": str(payload.get("description") or ""),
            "summary": extract[:2000],
        }
        return {
            "tool": "wiki_summary",
            "topic": cleaned_topic,
            "lang": normalized_lang,
            "title": title,
            "summary": extract[:2000],
            "items": [item],
        }
    except Exception as exc:
        return err("wiki_summary", exc)
