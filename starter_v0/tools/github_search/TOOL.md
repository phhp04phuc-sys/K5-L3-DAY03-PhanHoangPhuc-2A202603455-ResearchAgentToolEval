---
name: github_search
track: bonus
kind: live_api
provider: GitHub REST API
requires_env: []
inputs: [query, sort, max_results]
outputs: [items, total_count]
side_effect: false
---
# github_search

Searches public GitHub repositories by keyword using the official GitHub REST API (`https://api.github.com/search/repositories`).
Supports optional `GITHUB_TOKEN` environment variable for higher rate limits.

