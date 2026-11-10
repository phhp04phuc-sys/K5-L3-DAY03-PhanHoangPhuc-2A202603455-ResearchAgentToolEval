from __future__ import annotations

import re
from typing import Any
from urllib.parse import quote

import requests

from tools._shared import TIMEOUT, err

USER_AGENT = "AI20k-Day03-Research-Agent/1.0 (educational lab)"
LANG_RE = re.compile(r"^[a-z]{2,3}(-[a-z]{2,8})?$")


def _clean_lang(lang: str) -> str:
    """lang đi vào tên miền, nên chỉ nhận mã ngôn ngữ hợp lệ; còn lại dùng 'en'."""
    value = (lang or "").strip().lower()
    return value if LANG_RE.match(value) else "en"


def _clean_max_chars(max_chars: Any, default: int = 1200) -> int:
    try:
        value = int(max_chars)
    except (TypeError, ValueError):
        return default
    return max(100, min(value, 5000))


def get_wikipedia_summary(query: str = "", lang: str = "en", max_chars: int = 1200) -> dict[str, Any]:
    """Tóm tắt phần mở đầu của trang Wikipedia khớp nhất với `query`. Không cần key."""
    try:
        text = " ".join((query or "").split())
        if not text:
            return {"tool": "get_wikipedia_summary", "error": "EmptyQuery", "message": "query is empty"}
        code = _clean_lang(lang)
        limit = _clean_max_chars(max_chars)
        response = requests.get(
            f"https://{code}.wikipedia.org/w/api.php",
            params={
                "action": "query", "format": "json", "generator": "search", "gsrsearch": text, "gsrlimit": 1,
                "prop": "extracts", "exintro": 1, "explaintext": 1, "redirects": 1,
            },
            headers={"User-Agent": USER_AGENT},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        pages = (response.json().get("query") or {}).get("pages") or {}
        if not pages:
            return {"tool": "get_wikipedia_summary", "error": "NotFound", "message": f"No Wikipedia page for '{text}'"}
        page = next(iter(pages.values()))
        title = page.get("title") or text
        extract = (page.get("extract") or "").strip()
        if len(extract) > limit:
            extract = extract[: limit - 3] + "..."
        url = f"https://{code}.wikipedia.org/wiki/{quote(title.replace(' ', '_'))}"
        return {"tool": "get_wikipedia_summary", "query": text, "lang": code, "items": [{
            "title": title, "url": url, "source": f"{code}.wikipedia.org", "summary": extract,
        }]}
    except Exception as exc:
        return err("get_wikipedia_summary", exc)
