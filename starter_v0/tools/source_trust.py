"""Phân tầng độ tin cậy của nguồn theo company_policy/source-citation-policy.md.

Tầng 1: nguồn gốc (blog chính thức, tài liệu, paper, cơ quan nhà nước/giáo dục).
Tầng 2: báo chí uy tín, thường dẫn về nguồn gốc.
Tầng 3: mạng xã hội, diễn đàn, nội dung do người dùng tạo: chỉ là tín hiệu, chưa xác nhận.
Còn lại: chưa xác minh.

Đây là heuristic theo tên miền, nằm trong code để model không tự sửa được. Nó cho biết độ tin cậy
ước lượng của NGUỒN, không bảo đảm nội dung đúng.
"""
from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

TIER1_DOMAINS = {
    "arxiv.org", "openai.com", "anthropic.com", "deepmind.google", "ai.google", "blog.google", "research.google",
    "microsoft.com", "meta.com", "nature.com", "science.org", "who.int", "un.org", "w3.org", "ietf.org",
    "europa.eu", "nih.gov", "ieee.org", "acm.org",
}
TIER1_SUFFIXES = (".gov", ".gov.vn", ".edu", ".edu.vn", ".ac.uk", ".gov.uk")
TIER2_DOMAINS = {
    "reuters.com", "apnews.com", "bbc.com", "bbc.co.uk", "nytimes.com", "wsj.com", "ft.com", "theguardian.com",
    "bloomberg.com", "economist.com", "cnbc.com", "techcrunch.com", "theverge.com", "wired.com", "arstechnica.com",
    "technologyreview.com", "vnexpress.net", "tuoitre.vn", "thanhnien.vn", "nhandan.vn", "vtv.vn", "vietnamnet.vn",
}
TIER3_DOMAINS = {
    "x.com", "twitter.com", "reddit.com", "facebook.com", "instagram.com", "tiktok.com", "youtube.com", "youtu.be",
    "news.ycombinator.com", "medium.com", "substack.com", "quora.com", "linkedin.com", "t.me", "discord.com",
}

# Danh sách gửi lên Tavily khi lookup(trusted_only=true).
TRUSTED_DOMAINS = sorted(TIER1_DOMAINS | TIER2_DOMAINS)

NOTES = {
    "tier1": "Tầng 1: nguồn gốc (blog chính thức, paper, tài liệu, cơ quan nhà nước/giáo dục).",
    "tier2": "Tầng 2: báo chí uy tín; nên đối chiếu nguồn gốc khi là số liệu quan trọng.",
    "tier3": "Tầng 3: mạng xã hội/diễn đàn; chỉ là tín hiệu, chưa xác nhận. Không trình bày như sự thật đã kiểm chứng.",
    "unverified": "Chưa xác minh: nguồn không có trong danh sách tin cậy; cần cẩn trọng và nói rõ là chưa xác minh.",
}


def _host(url: str) -> str:
    try:
        host = (urlparse(url if "//" in (url or "") else f"//{url}").hostname or "").lower().strip(".")
    except ValueError:
        return ""
    return host[4:] if host.startswith("www.") else host


def _matches(host: str, domains: set[str]) -> bool:
    # Khớp đúng tên miền hoặc tên miền con. "evilopenai.com" và "openai.com.evil.io" KHÔNG khớp "openai.com".
    return any(host == d or host.endswith("." + d) for d in domains)


def source_tier(url: str) -> str:
    host = _host(url)
    if not host:
        return "unverified"
    if _matches(host, TIER3_DOMAINS):
        return "tier3"
    if _matches(host, TIER1_DOMAINS) or host.endswith(TIER1_SUFFIXES):
        return "tier1"
    if _matches(host, TIER2_DOMAINS):
        return "tier2"
    return "unverified"


def annotate_items(items: list[dict[str, Any]], *, force_tier: str | None = None) -> list[dict[str, Any]]:
    """Thêm `source_tier` và `tier_note` vào từng item (sửa tại chỗ và trả về chính danh sách đó)."""
    for item in items:
        tier = force_tier or source_tier(item.get("url", ""))
        item["source_tier"] = tier
        item["tier_note"] = NOTES[tier]
    return items
