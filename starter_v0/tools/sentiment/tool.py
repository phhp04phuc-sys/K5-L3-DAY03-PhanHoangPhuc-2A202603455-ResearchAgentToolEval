from __future__ import annotations

import re
from typing import Any

from tools._shared import fold_text

POSITIVE_WORDS = {
    "tuyet voi", "xuat sac", "tot", "thanh cong", "tang truong", "tich cuc", "rat hay", "ung ho", "dot pha", "vuot bac",
    "great", "good", "excellent", "awesome", "positive", "success", "growth", "best", "love", "breakthrough",
}

NEGATIVE_WORDS = {
    "te", "kem", "that bai", "giam manh", "tieu cuc", "loi", "nguy hiem", "sup do", "sap nguon",
    "bad", "terrible", "fail", "failure", "crash", "drop", "negative", "poor", "error", "risk", "worst",
}


def analyze_sentiment(text: str = "", detailed: bool = False) -> dict[str, Any]:
    if not isinstance(text, str):
        return {"status": "error", "error": "TypeError", "message": "Text must be a string"}

    cleaned_text = text.strip()
    if not cleaned_text:
        return {"status": "error", "error": "ValueError", "message": "Text cannot be empty"}

    folded = fold_text(cleaned_text).replace("đ", "d")
    pos_found = [w for w in POSITIVE_WORDS if re.search(rf"\b{re.escape(w)}\b", folded)]
    neg_found = [w for w in NEGATIVE_WORDS if re.search(rf"\b{re.escape(w)}\b", folded)]

    pos_count = len(pos_found)
    neg_count = len(neg_found)
    total = pos_count + neg_count

    if total == 0:
        score = 0.0
        sentiment = "neutral"
    else:
        score = (pos_count - neg_count) / total
        if score > 0.15:
            sentiment = "positive"
        elif score < -0.15:
            sentiment = "negative"
        else:
            sentiment = "neutral"

    result: dict[str, Any] = {
        "status": "ok",
        "sentiment": sentiment,
        "score": round(score, 2),
    }
    if detailed:
        result["key_indicators"] = sorted(pos_found + neg_found)
    return result
