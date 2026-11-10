from __future__ import annotations

import os
from typing import Any

import requests

from tools._shared import TIMEOUT, err


HF_MODELS_API_URL = "https://huggingface.co/api/models"
ALLOWED_HF_SORTS = {"downloads", "likes", "lastModified"}


def search_hf_models(
    query: str = "",
    sort: str = "downloads",
    max_results: int = 5,
) -> dict[str, Any]:
    try:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string")
        cleaned_query = " ".join(query.strip().split())

        parsed_max = int(max_results) if max_results is not None else 5
        if parsed_max <= 0:
            raise ValueError("max_results must be a positive integer")
        bounded_max = max(1, min(parsed_max, 10))

        normalized_sort = sort if isinstance(sort, str) and sort in ALLOWED_HF_SORTS else "downloads"

        params: dict[str, Any] = {
            "search": cleaned_query,
            "sort": normalized_sort,
            "direction": "-1",
            "limit": bounded_max,
        }

        headers: dict[str, str] = {
            "Accept": "application/json",
            "User-Agent": os.getenv("HF_USER_AGENT", "AI20k-Day03-Research-Agent/1.0"),
        }
        token = os.getenv("HF_TOKEN", "").strip()
        if token:
            headers["Authorization"] = f"Bearer {token}"

        response = requests.get(
            HF_MODELS_API_URL,
            params=params,
            headers=headers,
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        payload = response.json()

        raw_list = payload.get("models", []) if isinstance(payload, dict) else (payload or [])
        items: list[dict[str, Any]] = []
        for entry in raw_list[:bounded_max]:
            if not isinstance(entry, dict):
                continue
            model_id = (entry.get("id") or entry.get("modelId") or "").strip()
            if not model_id:
                continue
            pipeline_tag = (entry.get("pipeline_tag") or "").strip()
            downloads = int(entry.get("downloads") or 0)
            likes = int(entry.get("likes") or 0)
            items.append({
                "model_id": model_id,
                "title": model_id,
                "url": f"https://huggingface.co/{model_id}",
                "source": "huggingface.co",
                "pipeline_tag": pipeline_tag,
                "downloads": downloads,
                "likes": likes,
                "summary": f"Task: {pipeline_tag or 'unspecified'} | Downloads: {downloads} | Likes: {likes}",
            })

        return {
            "tool": "hf_models",
            "query": cleaned_query,
            "sort": normalized_sort,
            "count": len(items),
            "items": items,
        }
    except Exception as exc:
        return err("hf_models", exc)

