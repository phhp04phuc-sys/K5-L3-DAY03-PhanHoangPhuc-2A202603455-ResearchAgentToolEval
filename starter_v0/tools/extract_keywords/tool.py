from __future__ import annotations

import re
from collections import Counter
from typing import Any

from tools._shared import fold_text

_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has", "have", "in", "is",
    "it", "of", "on", "or", "that", "the", "this", "to", "was", "were", "will", "with",
    "ban", "cac", "can", "cho", "co", "cua", "da", "de", "den", "duoc", "gi", "giup", "hay",
    "khi", "khong", "la", "lam", "len", "mot", "nay", "nhung", "nhu", "ra", "rat", "sau", "se",
    "tai", "theo", "thi", "trong", "tu", "va", "ve", "voi", "vua",
}


def extract_keywords(text: str = "", top_n: int = 5) -> dict[str, Any]:
    """Extract top keywords, hashtags, word count, and estimated reading time from text."""
    if not isinstance(text, str):
        return {"status": "error", "error": "TypeError", "message": "Text must be a string"}

    if not isinstance(top_n, int) or isinstance(top_n, bool) or top_n < 1:
        return {"status": "error", "error": "ValueError", "message": "top_n must be a positive integer"}

    cleaned = text.strip()
    if not cleaned:
        return {"status": "error", "error": "ValueError", "message": "Text cannot be empty"}

    hashtags = list(dict.fromkeys(re.findall(r"#([A-Za-z0-9_]+)", cleaned)))
    words = cleaned.split()
    word_count = len(words)
    reading_time = round(max(0.1, word_count / 200.0), 2)

    folded = fold_text(cleaned).replace("đ", "d")
    tokens = [
        tok for tok in re.findall(r"[a-z0-9]+", folded)
        if len(tok) >= 2 and tok not in _STOPWORDS
    ]
    top_keywords = [word for word, _count in Counter(tokens).most_common(top_n)]

    return {
        "status": "ok",
        "keywords": top_keywords,
        "hashtags": hashtags,
        "word_count": word_count,
        "reading_time_minutes": reading_time,
    }
