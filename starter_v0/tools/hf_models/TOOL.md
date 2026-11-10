---
name: hf_models
track: bonus
kind: live_api
provider: Hugging Face Hub API
requires_env: []
inputs: [query, sort, max_results]
outputs: [items, count]
side_effect: false
---
# hf_models

Searches public AI/ML models on Hugging Face Hub (`https://huggingface.co/api/models`) by keyword, sorted by downloads, likes, or lastModified.
Supports optional `HF_TOKEN` environment variable.

