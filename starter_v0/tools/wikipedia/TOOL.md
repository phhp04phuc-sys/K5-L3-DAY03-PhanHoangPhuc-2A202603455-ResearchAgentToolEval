---
name: wikipedia
track: bonus
kind: live_api
provider: Wikipedia (MediaWiki public API)
requires_env: []
inputs: [query, lang, max_chars]
outputs: [items]
side_effect: false
---
# wikipedia

Tóm tắt phần mở đầu của trang Wikipedia khớp nhất với `query`. Không cần API key.

- `lang`: mã ngôn ngữ (`en`, `vi`...). Giá trị không hợp lệ được đổi về `en` (vì `lang` đi vào tên miền).
- `max_chars`: ép về khoảng 100 đến 5000, mặc định 1200.
- Không tìm thấy trang thì trả về `error: NotFound`.

Dùng khi cần định nghĩa hoặc bối cảnh về một khái niệm, người, tổ chức.
Không dùng cho tin tức mới (dùng `lookup`) hay đọc một URL cụ thể (dùng `fetch`).
