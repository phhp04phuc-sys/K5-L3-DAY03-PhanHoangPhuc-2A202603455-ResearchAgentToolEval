---
name: sentiment
track: bonus
kind: local_formatter
requires_env: []
inputs: [text, detailed]
outputs: [status, sentiment, score, key_indicators]
side_effect: false
---
# sentiment

Phân tích cảm xúc và sắc thái (tích cực, tiêu cực, trung lập) của một đoạn văn bản hoặc bài đăng mạng xã hội.
Nhận diện mức độ cảm xúc (score từ -1.0 đến 1.0) và trích xuất các từ khóa chỉ báo cảm xúc.
