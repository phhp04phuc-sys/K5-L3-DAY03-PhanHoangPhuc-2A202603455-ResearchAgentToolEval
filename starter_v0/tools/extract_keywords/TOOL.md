---
name: extract_keywords
track: bonus
kind: local_formatter
requires_env: []
inputs: [text, top_n]
outputs: [status, keywords, hashtags, word_count, reading_time_minutes]
side_effect: false
---
# extract_keywords

Trích xuất các từ khóa quan trọng nhất (theo tần suất, loại bỏ stopword), danh sách hashtag (`#tag`),
tổng số từ và thời gian đọc ước tính (phút) từ một bài viết hoặc đoạn văn bản nghiên cứu.
