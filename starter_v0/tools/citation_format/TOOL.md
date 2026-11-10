---
name: citation_format
category: processing
implementation: tools.citation_format.tool:format_citation
needs_api_key: none
---

# Tool `citation_format`

Format a research source (title, URL, author, year) into a standardized citation string (`markdown`, `apa`, or `bibtex`).

## Parameters

- `title`: title of the paper, article, or post (required).
- `url`: full `http://` or `https://` source URL (required).
- `author`: author or organization name (optional).
- `year`: publication year (optional).
- `style`: citation style (`markdown`, `apa`, or `bibtex`, default `markdown`).

