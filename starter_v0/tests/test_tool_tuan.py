from __future__ import annotations

import io
import re
import urllib.request
from typing import Any

from pypdf import PdfReader

# Dạng mới: 2401.00001 hoặc 2401.00001v2. Dạng cũ: hep-th/9901001
ID_RE = re.compile(r"^(\d{4}\.\d{4,5}|[a-z\-]+(\.[A-Z]{2})?/\d{7})(v\d+)?$")


def _normalize_id(value: str) -> str:
    value = value.strip().removeprefix("arXiv:")
    for marker in ("/abs/", "/pdf/"):
        if marker in value:
            value = value.split(marker, 1)[1]
    return value.removesuffix(".pdf").strip("/")


def get_paper_text(arxiv_id: str, max_chars: int = 8000, page_limit: int = 10) -> dict[str, Any]:
    arxiv_id = _normalize_id(arxiv_id)
    if not ID_RE.match(arxiv_id):
        return {"error": "ValueError", "message": f"invalid arXiv id: {arxiv_id}"}

    max_chars = max(500, min(int(max_chars), 30000))
    page_limit = max(1, min(int(page_limit), 30))

    req = urllib.request.Request(
        f"https://arxiv.org/pdf/{arxiv_id}",
        headers={"User-Agent": "research-agent-lab/1.0"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read()

    reader = PdfReader(io.BytesIO(data))
    pages = reader.pages[:page_limit]
    text = "\n".join((page.extract_text() or "") for page in pages)
    text = re.sub(r"[ \t]+", " ", text).strip()

    return {
        "tool": "get_paper_text",
        "arxiv_id": arxiv_id,
        "num_pages": len(reader.pages),
        "pages_read": len(pages),
        "text": text[:max_chars],
        "truncated": len(text) > max_chars,
    }