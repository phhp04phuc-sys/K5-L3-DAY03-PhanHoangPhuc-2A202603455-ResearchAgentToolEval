---
name: hackernews
track: bonus
kind: live_api
provider: Hacker News (Algolia public API)
requires_env: []
inputs: [query, sort_by, limit]
outputs: [items]
side_effect: false
---
# hackernews

Lấy tin công nghệ, lập trình, startup từ Hacker News. Không cần API key.

- Không có `query`, `sort_by=top`: các bài trên trang nhất.
- Không có `query`, `sort_by=latest`: các bài mới nhất.
- Có `query`: tìm bài theo từ khóa (`top` = liên quan nhất, `latest` = mới nhất).
- `limit` được ép về khoảng 1 đến 20; `sort_by` lạ được đổi về `top`.

Dùng khi người dùng nhắc Hacker News, HN, hoặc muốn xem cộng đồng lập trình đang bàn gì.
Không dùng cho tin tức nói chung (dùng `lookup`) hay tweet (dùng `timeline`, `social_search`).
