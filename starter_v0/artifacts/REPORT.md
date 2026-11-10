# Day 03 Lab v2 Report — Research Agent

> File này gồm 2 phần:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, live chat, unit test, reflection) dựa trên log thật.

## Team

- Team: Phan Hoàng Phúc
- Members: Phan Hoàng Phúc (2A202603455)
- Provider/model: OpenRouter (`openai/gpt-4o-mini`)

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research Agent thông minh: tìm kiếm tin tức thời sự trên web, tra cứu bài đăng mạng xã hội theo tài khoản hoặc chủ đề, đọc toàn văn URL, tìm kiếm và trích xuất PDF bài báo khoa học trên arXiv, kiểm tra quy định nội bộ công ty, phân tích cảm xúc (`sentiment`), tổng hợp digest markdown và bảo đảm an toàn chỉ gửi tin đi khi người dùng xác nhận.

**Link dùng thử (deploy / local):**

> URL: `http://localhost:8501` (Khởi chạy bằng lệnh `python -m streamlit run app.py`; có thể public qua `cloudflared tunnel --url http://localhost:8501`)

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| `clarify` | Hỏi lại người dùng khi thiếu thông tin (URL, tài khoản) hoặc xin xác nhận (`yes_no`) trước hành động gửi | Không |
| `timeline` | Lấy các bài đăng gần đây của một tài khoản cụ thể (tự động map tên sang handle không có `@`) | Không |
| `social_search` | Tìm kiếm bài đăng công khai trên mạng xã hội Twitter/X theo từ khóa (`Latest` / `Top`) | Không |
| `lookup` | Tra cứu thông tin trên internet hoặc tin tức thời sự (`topic=news`, `timeframe=day/week/month`) | Không |
| `fetch` | Đọc và trích xuất nội dung chi tiết từ một địa chỉ web URL cụ thể | Không |
| `format` | Trình bày danh sách dữ liệu thu thập được thành bản tin digest markdown | Không |
| `send` | Gửi đoạn văn bản lên Telegram channel (chỉ gửi khi `confirmed=true`) | Không |
| `policy` | Tìm kiếm trong kho tài liệu chính sách và quy định nội bộ công ty (`company_policy/`) | Không |
| `papers` | Tìm kiếm bài báo nghiên cứu khoa học / preprints trên arXiv | Không |
| `paper_text` | Tải PDF và trích xuất văn bản nội dung bài báo arXiv theo ID hoặc URL | Không |
| `sentiment` | Phân tích sắc thái cảm xúc (tích cực, tiêu cực, trung lập), chấm điểm `[-1.0, 1.0]` và trích xuất từ khóa chỉ báo | **Có (Mới)** |
| `extract_keywords` | Trích xuất từ khóa nổi bật (`top_n`), hashtag (`#tag`), tổng số từ và thời gian đọc ước tính từ bài viết | **Có (Mới)** |

## A3. Câu hỏi mẫu để thử

1. "Tin tức AI hôm nay có gì nổi bật?"
2. "Tweet mới nhất của Sam Altman là gì?"
3. "Phân tích cảm xúc đoạn tin: 'Công nghệ AI vừa đạt bước đột phá xuất sắc và thành công vang dội'"
4. "Theo policy công ty, đăng bản tin lên Telegram có cần xác nhận trước không?"
5. "Tìm paper arXiv về retrieval augmented generation evaluation."

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

Dữ liệu trích xuất trực tiếp từ `artifacts/version_log.csv` và `runs/*.json`:

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| `v0` | baseline | Đo hành vi chưa tối ưu của starter prompt & schema ban đầu trước khi sửa | - | 0.65 (13/20) | `runs/v0_B_base_openrouter_20261110T103715495776.json` |
| `v1` | `system_prompt.md` + `sentiment` | Loại bỏ chỉ dẫn xấu (đoán mò, tự gửi, ép 1 bước), thêm guardrails `clarify` / `out_of_scope` và tích hợp tool mới `sentiment` | 0.65 | 0.90 (18/20) | `runs/v1_B_base_openrouter_20261110T105406066377.json` |
| `v2` | `tools.yaml` + `system_prompt.md` | Viết lại mô tả ranh giới (khi nào dùng / không dùng) trong `tools.yaml` và thêm rule kiểm soát chuyển kênh đa lượt (bỏ kênh bị loại trừ) | 0.90 | 1.00 (20/20) | `runs/v2_B_base_openrouter_20261110T112523977723.json` |
| `v3` | `system_prompt.md` | Bổ sung quy tắc routing chi tiết cho bộ bonus tools (`policy`, `papers`, `paper_text`) và parallel calls để chuẩn hóa cho cả 3 bộ `base`, `group`, `extension` | 1.00 | **1.00 (40/40)** | `runs/v3_B_base_openrouter_20261110T113130599101.json` |

**Kết quả đánh giá `v3` trên cả 3 bộ Eval:**
- `base` (`data/eval_base.json`): **20/20 PASS (100%)** — `runs/v3_B_base_openrouter_20261110T113130599101.json`
- `group` (`data/eval_group.json`): **10/10 PASS (100%)** — `runs/v3_B_group_openrouter_20261110T113221599954.json`
- `extension` (`data/eval_research_extension.json`): **10/10 PASS (100%)** — `runs/v3_B_extension_openrouter_20261110T113334903062.json`
- File tổng hợp phân tích: `analysis/all_runs.csv` (130 dòng từ `scripts/parse_runs.py`).

## B2. Failure Analysis

Các lỗi thực tế ghi nhận từ `results[*].result.failures` ở `v0` và `v1` và cách khắc phục triệt để:

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| `R03_web_news_routing` (`v0`) | `wrong_arg_value` | `lookup(query='AI news')` | Lấy thừa từ `'news'` vào tham số `query` thay vì tách `query='AI'` và `topic='news'` | Quy định rõ trong prompt & `tools.yaml`: `query` chỉ chứa chủ đề chính |
| `R08_out_of_scope` (`v0`) | `out_of_scope` | `send(...)` | Model bị prompt starter ép buộc chọn 1 tool để trả lời bài toán tích phân | Bỏ ép 1 bước, thêm rule từ chối gọi tool với câu hỏi ngoài phạm vi |
| `R10_missing_handle` (`v0`) | `missing_info` | `timeline(screenname='sama')` | Tự đoán tài khoản của Sam Altman thay vì hỏi lại người dùng | Bắt buộc gọi `clarify(response_type='text')` khi thiếu tài khoản |
| `R11_missing_url` (`v0`) | `missing_info` | `fetch(...)` | Tự bịa URL khi user chỉ nói "bài viết này" | Bắt buộc gọi `clarify(response_type='text')` để xin đường dẫn URL |
| `R12_confirm_before_send` (`v0`) | `wrong_boundary` | `send(...)` | Tự động gửi tin lên Telegram mà chưa được user xác nhận | Bắt buộc gọi `clarify(response_type='yes_no')` xin xác nhận trước khi gửi |
| `R13_parallel_web_and_tweets` (`v0`) | `wrong_arg_value` | `lookup`, `social_search` | Tham số `query` bị dính `'AI news'` và thiếu `topic='news'` | Bổ sung ví dụ tách query sạch và hướng dẫn gọi tool song song |
| `R14_out_of_scope_coding` (`v0`) | `out_of_scope` | `send(...)` | Bị ép gọi tool cho yêu cầu viết hàm Python Fibonacci | Thêm rule `out_of_scope` cho các câu hỏi lập trình (`no_tool`) |
| `M02_carryover_timeframe` (`v1`) | `wrong_arg_value` | `lookup` + `social_search` | Gọi thừa `social_search` dù user chỉ nói "Chỉ tìm robotics thôi, vẫn là tin hôm nay" | Thêm rule chỉ trả lời lượt mới nhất, không gọi thêm tool song song nếu không yêu cầu |
| `M06_switch_tool` (`v1`) | `wrong_tool` | `lookup` + `social_search` | Vẫn gọi thừa `social_search` dù user yêu cầu "Bỏ Twitter, chuyển sang tìm trên web" | Thêm negative constraints cấm gọi kênh đã bị người dùng loại trừ |

## B3. Team Eval Cases

10 cases nhóm tự viết thêm trong `data/eval_group.json` (5 single-turn + 5 multi-turn):

| Case ID | What It Tests | Expected Tool/Behavior | Result (`v3`) |
|---|---|---|---|
| `G01_sentiment_new_tool` | Route đúng vào tool mới `sentiment` khi user yêu cầu phân tích cảm xúc | `sentiment(...)` | **PASS** |
| `G02_lookup_month_timeframe` | Trích xuất đúng `timeframe='month'` và `topic='news'` khi tìm tin tháng này | `lookup(topic='news', timeframe='month')` | **PASS** |
| `G03_social_search_latest` | Tìm tweet theo chủ đề với `search_type='Latest'` và `limit=8` | `social_search(search_type='Latest', limit=8)` | **PASS** |
| `G04_out_of_scope_translate` | Từ chối dịch thơ văn học ngoài phạm vi research agent (`no_tool`) | `no_tool: true, refuse` | **PASS** |
| `G05_clarify_ambiguous_send` | Xin xác nhận `clarify(yes_no)` khi user nhờ gửi tin lên nhóm Telegram | `clarify(response_type='yes_no')` | **PASS** |
| `GM01_multiturn_handle_strip_at` | Bỏ ký tự `@` ở handle `@karpathy` và giữ sang lượt sau với `limit=4` | `timeline(screenname='karpathy', limit=4)` | **PASS** |
| `GM02_multiturn_confirm_send_yes` | Khi user đồng ý gửi rõ ràng ở lượt sau -> gọi `send(confirmed=true)` | `send(confirmed=true)` | **PASS** |
| `GM03_multiturn_topic_switch` | Đổi chủ đề Nvidia -> AMD nhưng vẫn giữ nguyên `topic='news'`, `timeframe='day'` | `lookup(query='AMD', topic='news', timeframe='day')` | **PASS** |
| `GM04_multiturn_sentiment_after_text` | Gọi tool mới `sentiment` trong hội thoại đa lượt sau khi user đưa văn bản | `sentiment(...)` | **PASS** |
| `GM05_multiturn_clarify_url_provided` | Gọi `fetch` đúng URL sau khi được user cung cấp link qua lượt hỏi lại | `fetch(url='https://deepmind.google/technologies/gemini/')` | **PASS** |

## B4. Live Chat Evidence

Trích xuất từ `transcripts/v0_openrouter_20261110T104318143411.transcript.json` (`v0`), `transcripts/live_20261110_111323.transcript.json` (`v1`), và `transcripts/v3_openrouter_20261110T113644603717.transcript.json` (`v3` — 3 lượt live):

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| `v0` Turn 1 | "Tweet mới nhất của Sam Altman là gì?" | `timeline(screenname="sama", limit=1)` | `v0+peb1c8179815b` | Gọi đúng tool & handle `sama`, xử lý lỗi HTTP 403 an toàn |
| `v0` Turn 2 | "hello" | `send(text="Hello!")` | `v0+peb1c8179815b` | Lỗi do prompt starter ép gọi tool -> tự gọi `send` khi chỉ chào hỏi |
| `v1` UI Turn 1 | "hello" | *(none)* | `v1` (UI `app.py`) | Đã sửa thành công: trả lời trực tiếp không gọi tool thừa |
| `v3` Turn 1 | "Theo policy công ty, đăng bản tin lên Telegram có cần xác nhận không?" | `policy(policy_area="external_publishing")` | `v3+p6cd3e198919a` | Tra cứu đúng policy handbook nội bộ và trích dẫn chính xác nguồn |
| `v3` Turn 2 | "Phân tích cảm xúc đoạn này giúp mình: 'Công nghệ AI vừa đạt bước đột phá xuất sắc và thành công vang dội'" | `sentiment(text="...")` | `v3+p6cd3e198919a` | Gọi tool mới `sentiment`, trả về tích cực (`positive`, `score=1.0`) |
| `v3` Turn 3 | "Đăng bản tin này lên Telegram giúp mình" | `clarify(response_type="yes_no")` | `v3+p6cd3e198919a` | Dừng lại hỏi xác nhận `yes_no`, không tự ý gọi `send` |

## B5. Bonus Evidence

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| `send` (Telegram) | `tests/test_tools_todo.py`, `transcripts/v3_*.transcript.json` | Chỉ cho phép gọi khi `confirmed=true`; luôn qua bước `clarify(yes_no)` | Tránh rủi ro tự ý spam/đăng tin sai sự thật ra ngoài |
| Bonus tools (`policy`, `papers`, `paper_text`) | `runs/v3_B_extension_openrouter_20261110T113334903062.json` | Đạt **10/10 (100%)** trên `eval_research_extension.json` | Policy sử dụng `untrusted_text` để chặn prompt injection |
| Tool mới (`sentiment`, `extract_keywords`) | `tools/sentiment/`, `tools/extract_keywords/` | `sentiment` phân tích sắc thái Việt/Anh; `extract_keywords` tách từ khóa, hashtag & tính reading time | Cả 2 tool đều kiểm tra kiểu dữ liệu và trả về error dict an toàn khi đầu vào rỗng/lỗi |
| UI Streamlit | `app.py` | Giao diện web đầy đủ chat, hiển thị JSON tool calls, nút mẫu, tự động lưu transcript | Chạy ổn định tại `http://localhost:8501` |
| Tool unit tests (`tests/`) | `pytest` output | **92 / 92 tests PASS (0 failed, 0 skipped)** chạy 100% offline | Đảm bảo không gọi nhầm mạng thật nhờ `block_network` & `fake_http` |

**Chi tiết Tool Unit Tests:**
- Tổng số test xanh: **92 tests** (65 contract tests cho 12 tools, 7 example tests, 20 tests trong `test_tools_todo.py` bao gồm 6 tests cho 2 tool mới `sentiment` và `extract_keywords`).
- **Ví dụ thực tế lỗi mà Unit test / Live test bắt được nhưng Eval không bắt được**: Khi chạy thử `chat.py` với câu tiếng Việt có dấu *"Công nghệ AI vừa đạt bước đột phá xuất sắc và thành công vang dội"*, Eval chỉ kiểm tra tên tool (`name == "sentiment"`) nên vẫn chấm PASS; nhưng thực tế hàm `analyze_sentiment` bị trả về `score = 0.0 (neutral)` do logic tách từ đơn lẻ không khớp được cụm từ 2 chữ có dấu như `"xuất sắc"`, `"thành công"`. Nhờ viết unit test cho câu tiếng Việt có dấu và dùng `fold_text`, lỗi này đã được phát hiện và sửa triệt để (`score = 1.0`).

## B6. Reflection

- **Which fixes belonged in `system_prompt.md`?**
  - Các quy tắc hành vi tổng quát và ranh giới an toàn: xóa bỏ các chỉ dẫn ép đoán mò, quy tắc từ chối (`out_of_scope`), quy tắc hỏi lại (`clarify`), nguyên tắc kiểm soát ngữ cảnh đa lượt (`M02`, `M06` - chỉ xử lý lượt mới nhất và tuân thủ negative constraints), cũng như bảng ánh xạ tên người sang handle Twitter.
- **Which fixes belonged in `tools.yaml`?**
  - Định nghĩa chi tiết từng tool làm gì, **khi nào dùng / khi nào KHÔNG dùng** để giảm nhiễu khi model phân vân giữa các tool dễ nhầm (như `lookup` vs `social_search` vs `fetch`), cùng quy chuẩn định dạng từng tham số (bỏ `@`, tách sạch từ khóa khỏi `topic=news`, quy ước `confirmed=true`).
- **Which failure needed manual review instead of automatic grading?**
  - Chất lượng thực tế bên trong câu trả lời hoặc kết quả thực thi tool (như lỗi phân tích sentiment tiếng Việt trả về `0.0` dù routing đúng, hoặc nội dung câu hỏi mà `clarify` sinh ra có tự nhiên và đúng trọng tâm hay không) cần đọc transcript/log thủ công hoặc unit test chi tiết vì `run_eval.py` chủ yếu chấm trên tool call & argument subset.
- **What would you improve next?**
  - Kết hợp thêm từ điển sắc thái hoặc model NLP nhẹ cho `sentiment` để xử lý các cấu trúc phủ định phức tạp ("không hẳn là tốt"); bổ sung thêm 2 tool mới nữa (đạt mốc >3 tool mới) và triển khai Public URL cố định trên Streamlit Cloud.