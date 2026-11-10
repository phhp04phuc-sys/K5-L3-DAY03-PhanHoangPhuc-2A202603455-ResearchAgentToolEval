from __future__ import annotations

from typing import Any
from urllib.parse import urlparse


TIER1_DOMAINS = {
    "arxiv.org",
    "openai.com",
    "anthropic.com",
    "deepmind.google",
    "ai.meta.com",
    "nature.com",
    "science.org",
    "ieee.org",
    "acm.org",
}

TIER3_DOMAINS = {
    "x.com",
    "twitter.com",
    "reddit.com",
    "t.me",
    "medium.com",
}


def validate_research_url(url: str = "") -> dict[str, Any]:
    cleaned = url.strip()
    if not cleaned:
        return {"error": "invalid_input", "message": "url is required"}

    parsed = urlparse(cleaned)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return {"error": "invalid_url", "message": "url must start with http:// or https:// and include a valid domain"}

    host = parsed.netloc.lower()
    if host.startswith("www."):
        host = host[4:]

    if any(host == d or host.endswith("." + d) for d in TIER1_DOMAINS):
        source_tier = "tier_1"
        credibility = "primary_or_academic"
    elif any(host == d or host.endswith("." + d) for d in TIER3_DOMAINS):
        source_tier = "tier_3"
        credibility = "social_or_unverified_signal"
    else:
        source_tier = "tier_2"
        credibility = "general_web_or_reporting"

    return {
        "valid": True,
        "url": cleaned,
        "scheme": parsed.scheme,
        "domain": host,
        "path": parsed.path or "/",
        "source_tier": source_tier,
        "credibility": credibility,
    }

