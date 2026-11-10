---
name: wiki_summary
track: bonus
kind: live_api
provider: Wikipedia REST API
requires_env: []
inputs: [topic, lang]
outputs: [items, title, summary]
side_effect: false
---
# wiki_summary

Fetches an encyclopedia summary for a given concept or entity from the Wikipedia REST API (`https://<lang>.wikipedia.org/api/rest_v1/page/summary/<topic>`).
