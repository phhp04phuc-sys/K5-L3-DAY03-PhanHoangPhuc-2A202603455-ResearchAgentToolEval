from __future__ import annotations

import re
from typing import Any


ALLOWED_STYLES = {"markdown", "apa", "bibtex"}


def format_citation(
    title: str = "",
    url: str = "",
    author: str = "",
    year: str = "",
    style: str = "markdown",
) -> dict[str, Any]:
    clean_title = title.strip()
    clean_url = url.strip()
    clean_author = author.strip() or "Unknown Author"
    clean_year = str(year).strip() or "n.d."
    clean_style = style.strip().lower() or "markdown"

    if not clean_title:
        return {"error": "invalid_input", "message": "title is required"}
    if not clean_url or not clean_url.startswith(("http://", "https://")):
        return {"error": "invalid_input", "message": "a valid http(s) url is required"}
    if clean_style not in ALLOWED_STYLES:
        return {"error": "invalid_style", "message": f"style must be one of {sorted(ALLOWED_STYLES)}"}

    if clean_style == "markdown":
        formatted = f"[{clean_title}]({clean_url}) — {clean_author} ({clean_year})"
    elif clean_style == "apa":
        formatted = f"{clean_author} ({clean_year}). {clean_title}. Retrieved from {clean_url}"
    else:
        slug_author = re.sub(r"[^a-z0-9]+", "", clean_author.lower().split()[0]) or "source"
        slug_year = re.sub(r"[^0-9]+", "", clean_year) or "nd"
        cite_key = f"{slug_author}{slug_year}"
        formatted = (
            f"@misc{{{cite_key},\n"
            f"  author = {{{clean_author}}},\n"
            f"  title = {{{clean_title}}},\n"
            f"  year = {{{clean_year}}},\n"
            f"  url = {{{clean_url}}}\n"
            f"}}"
        )

    return {
        "style": clean_style,
        "title": clean_title,
        "url": clean_url,
        "author": clean_author,
        "year": clean_year,
        "citation": formatted,
    }

