# Day 03 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. **Xong trước 16:30** để làm tài liệu phụ trợ khi demo.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. **Hoàn thiện sau buổi debate để nộp bài.**

## Team

- Team: Nhomnhom (lớp L3A)
- Members: Phan Hoàng Phúc (2A202603455), kegacua, cuong-sadboi, lythanhlap, hoanglv2k9 (họ tên và MSSV các bạn: xem `TEAM.md`)
- Provider/model: Google Gemini, `gemini-3.5-flash` (cùng một model cho cả 4 version để so điểm công bằng)

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research agent: nhận yêu cầu bằng tiếng Việt, chọn đúng tool, gọi tool thật rồi trả lời theo kết quả. Agent tìm tin tức trên web, đọc tweet theo tài khoản hoặc theo từ khóa, đọc nội dung một URL, tìm và đọc paper arXiv, tra chính sách nội bộ, và gửi bản tin lên Telegram **chỉ sau khi người dùng xác nhận**. Khi thiếu thông tin (không nói tài khoản nào, URL nào) agent hỏi lại thay vì đoán. Câu hỏi ngoài phạm vi research thì từ chối.

**Link dùng thử (deploy):**

> URL: (chưa có — chạy `streamlit run app.py` rồi `cloudflared tunnel --url http://localhost:8501`, dán link vào đây)

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng một câu: thiếu thông tin (text) hoặc xác nhận trước khi gửi (yes_no) | không |
| timeline | lấy các bài đăng gần đây của MỘT tài khoản X/Twitter | không |
| social_search | tìm bài đăng X/Twitter theo từ khóa (Latest hoặc Top) | không |
| lookup | tìm web, nhất là tin tức (topic news/general, timeframe day/week/month/year) | không |
| fetch | đọc nội dung đầy đủ của MỘT URL | không |
| format | dựng bản tin markdown từ các item đã thu thập | không |
| send | gửi tin lên Telegram, chỉ khi đã được xác nhận (`confirmed=true`) | không |
| policy | tra chính sách công ty (trích nguồn, quyền riêng tư, đăng bài ngoài, quy trình research) | không |
| papers | tìm paper trên arXiv | không |
| paper_text | tải một paper arXiv và trích text | không |
| hackernews | tin công nghệ, lập trình, startup từ Hacker News (trang nhất, mới nhất hoặc tìm theo từ khóa); không cần key | **có** |
| wikipedia | tóm tắt phần mở đầu một trang Wikipedia (vi hoặc en) để lấy định nghĩa, bối cảnh; không cần key | **có** |
| math_solve | giải toán bằng sympy chạy cục bộ: tính, rút gọn, phân tích, giải phương trình, đạo hàm, nguyên hàm; đầu vào được lọc chặt chống chạy mã lạ | **có** |

## A3. Câu hỏi mẫu để thử

1. `Tin tức AI hôm nay có gì nổi bật?` (dùng `lookup`, topic news, timeframe day)
2. `Tweet mới nhất của Sam Altman là gì?` (dùng `timeline`, handle `sama`)
3. `Tóm tắt 5 tweet mới nhất giúp mình` (agent phải hỏi lại là của ai, không đoán)
4. `Đăng bản tin này lên Telegram giúp mình` (agent hỏi xác nhận yes/no trước, không gửi ngay)
5. `Đọc giúp mình paper arXiv 1706.03762, lấy 2 trang đầu` (dùng `paper_text`)
6. `Hôm nay Hacker News có gì hot?` (tool mới `hackernews`)
7. `Alan Turing là ai?` (tool mới `wikipedia`, `lang=vi`)
8. `Giải giúp mình phương trình x^2 - 5x + 6 = 0` (tool mới `math_solve`)

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

Mọi số liệu dưới đây lấy từ `artifacts/version_log.csv` và `runs/*.json`. Eval base: 20 case (14 một lượt, 6 nhiều lượt), model `gemini-3.5-flash`, `temperature=0`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Đo hành vi chưa tối ưu | — | 0.55 | `runs/v0_B_base_gemini_20261110T110240587901.json` |
| v1 | `system_prompt.md` | Starter bảo agent đoán và gửi ngay; bỏ chỉ dẫn xấu và thêm rule hỏi lại, xác nhận thì các case thiếu thông tin, ngoài phạm vi, ranh giới gửi sẽ qua | 0.55 | 0.75 | `runs/v1_B_base_gemini_20261110T110803143950.json` |
| v2 | `tools.yaml` | Mô tả tool mơ hồ làm `query` dài và chọn sai tham số; viết rõ khi nào dùng, khi nào không, và quy ước tham số thì lỗi `wrong_arg_value` giảm | 0.75 | 0.90 | `runs/v2_B_base_gemini_20261110T111045753944.json` |
| v3 | `system_prompt.md` | R12 còn lỗi vì agent hỏi nội dung (text) thay vì xác nhận; thêm rule policy "đăng/gửi chưa xác nhận thì hỏi yes_no" sẽ sửa | 0.90 | 1.00 | `runs/v3_B_base_gemini_20261110T111239861829.json` |

Các chỉ số chi tiết:

| Version | case_accuracy | tool_routing | argument | multiturn |
|---|---:|---:|---:|---:|
| v0 | 0.55 | 0.65 | 0.55 | 0.83 |
| v1 | 0.75 | 0.90 | 0.75 | 0.83 |
| v2 | 0.90 | 0.95 | 0.90 | 1.00 |
| v3 | 1.00 | 1.00 | 1.00 | 1.00 |
| v4 | 1.00 | 1.00 | 1.00 | 1.00 |
| v5 | 0.95 | 0.95 | 0.95 | 1.00 |

| v4 | `tools.yaml` + 2 tool mới | Thêm `hackernews` và `wikipedia` với mô tả rõ thì agent route đúng tool mới mà không làm hỏng 20 case base | 1.00 | 1.00 | `runs/v4_B_base_gemini_20261110T115949550316.json` |

| v5 | `system_prompt.md` + `tools.yaml` + tool `math_solve` | Thêm tool toán và đưa giải tích vào phạm vi thì 3 case toán mới qua; điểm base chỉ mất R08 | 1.00 | **0.95** | `runs/v5_B_base_gemini_20261110T121605353594.json` |

Ghi chú độ tin cậy:
- Chạy v0 hai lần trên Gemini cho kết quả giống hệt nhau (0.55, không case nào đổi kết quả).
- **v5 giảm từ 1.00 xuống 0.95 là chủ ý, không phải hồi quy:** case base R08 ("nguyên hàm của x^2") mong đợi agent từ chối, nhưng nhóm quyết định hỗ trợ giải toán gồm cả giải tích, nên agent gọi `math_solve` và R08 lệch với đáp án mẫu. Bài cấm sửa case base nên nhóm giữ nguyên và ghi nhận ở đây. 19 case còn lại vẫn qua, kể cả R14 (từ chối viết code).
- Mỗi version chỉ chạy một lần, mỗi bước chênh một đến vài case trên 20 case. Điểm v3 = 1.00 là đạt benchmark base; rule thêm ở v3 lấy từ chính sách `external-publishing-policy.md` và gần với case R12.
- Trước khi chuyển sang Gemini, nhóm chạy v0 (0.80) và v1 (0.85) trên model miễn phí `nvidia/nemotron-3-ultra-550b-a55b:free` (OpenRouter). v2 trên model này bị hết hạn mức ngày (5 case lỗi 429) nên không đo đủ. Các dòng này giữ trong `version_log.csv` với tên `v0-nemotron`, `v1-nemotron`, không so với bảng trên vì khác model.

## B2. Failure Analysis

Lỗi thật của v0 (từ `results[*].result.failures`, model Gemini). Cột "Fix" ghi version đã sửa.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R08_out_of_scope | out_of_scope | `format` | Câu tích phân ngoài phạm vi nhưng agent vẫn gọi tool | v1: thêm mục "Stay in scope" |
| R14_out_of_scope_coding | out_of_scope | `send` | Yêu cầu viết code Fibonacci, agent gọi `send` (tệ hơn cả gọi thừa vì có tác dụng phụ) | v1 |
| R09_no_tool_capability | unnecessary_tool | `policy` | "Bạn là gì và làm được gì" không cần tool | v1 |
| R10_missing_handle | missing_info | `timeline` | Không nói tài khoản nào mà agent tự đoán handle | v1: "Never guess missing information" |
| R11_missing_url | missing_info | `fetch` | "Tóm tắt bài này" không có URL, agent vẫn gọi `fetch` | v1 |
| R12_confirm_before_send | wrong_boundary | `send` | "Đăng lên Telegram" mà agent gửi ngay, không xác nhận. Ở v1 và v2 đã hỏi xác nhận nhưng sai kiểu (`text` thay vì `yes_no`) | v1 (không gửi nữa), v3 (đúng `yes_no`) |
| R03_web_news_routing | wrong_tool (arg) | `lookup` | `query` dài ("tin tức AI mới nhất hôm nay") thay vì "AI" | v2: ghi rõ `query` là từ khóa ngắn |
| R13_parallel_web_and_tweets | wrong_tool | `lookup` | Chỉ gọi một tool, thiếu `social_search`; `query` dài | v1 (gọi đủ hai tool), v2 (query ngắn) |
| M02_carryover_timeframe | wrong_arg_value | `lookup` | `query="robotics news"` thay vì "robotics" | v2 (v1 còn gọi thừa `social_search`) |

Hai lỗi còn lại sau v1 và v2:
- **R01_user_tweets_routing** (v1): agent hỏi `clarify` dù câu "Tweet mới nhất của Sam Altman" đã đủ thông tin. Rule "không đoán" ở v1 có thể làm agent hỏi lại quá tay. Hết lỗi ở v2, cùng lúc `timeline` được thêm mô tả "dùng khi người dùng nêu tên một người" và ví dụ Sam Altman -> sama (nhóm chưa tách riêng để chứng minh đây là nguyên nhân).
- **R06_timeframe_arg** (v2): agent gọi `lookup` hai lần (tiếng Việt và tiếng Anh). Hết lỗi ở v3 nhưng chưa có thay đổi nào nhắm riêng vào lỗi này, nên có thể do dao động giữa các lần chạy.

## B3. Team Eval Cases

16 case trong `data/eval_group.json` (10 case ban đầu: 5 một lượt, 5 nhiều lượt; thêm 3 case cho hackernews/wikipedia và 3 case cho math_solve). Kết quả 10 case đầu chạy trên v3 (`runs/v3_B_group_gemini_20261110T111334673629.json`): 10/10. Chạy trên v2 (`runs/v2_B_group_gemini_20261110T111412860116.json`): 10/10.

| Case ID | What It Tests | Expected Tool/Behavior | Result (v3) |
|---|---|---|---|
| G01_timeline_name_to_handle | Đổi tên người nổi tiếng thành handle, route `timeline` | `timeline(screenname=billgates)` | PASS |
| G02_social_top_viral | "viral nhất" map sang `search_type=Top` | `social_search(query=Claude, search_type=Top)` | PASS |
| G03_lookup_month_news | "trong tháng này" map sang `timeframe=month` | `lookup(topic=news, timeframe=month)` | PASS |
| G04_send_with_text_still_confirm | Đã có nội dung nhưng gửi vẫn phải xác nhận | `clarify(response_type=yes_no)` | PASS |
| G05_out_of_scope_poem | Sáng tác thơ là ngoài phạm vi | không gọi tool | PASS |
| GM01_carry_handle_new_limit | Giữ handle ở lượt 1, đổi `limit=7` ở lượt 2 | `timeline(screenname=sama, limit=7)` | PASS |
| GM02_social_then_top | Giữ query, đổi sang Top ở lượt 2 | `social_search(query=OpenAI, search_type=Top)` | PASS |
| GM03_timeframe_switch | Sửa timeframe week thành day | `lookup(topic=news, timeframe=day)` | PASS |
| GM04_confirm_after_content | Sau khi có nội dung vẫn xác nhận yes_no | `clarify(response_type=yes_no)` | PASS |
| GM05_search_paper_then_read | Đổi ý: bỏ tìm paper, đọc luôn theo ID | `paper_text(arxiv_url=1706.03762, max_pages=2)` | PASS |
| G06_hackernews_front_page | Nhắc Hacker News phải route tới tool mới | `hackernews` | PASS (v4) |
| G07_wikipedia_vi_definition | Câu định nghĩa tiếng Việt: route `wikipedia` với `lang=vi` | `wikipedia(lang=vi)` | PASS (v4) |
| GM06_hn_then_wikipedia | Lượt 2 đổi từ hackernews sang wikipedia | `wikipedia` | PASS (v4) |
| G08_math_solve_equation | Giải phương trình phải gọi math_solve, task=solve | `math_solve(task=solve)` | PASS (v5) |
| G09_math_integral | Nguyên hàm nay trong phạm vi, task=integral | `math_solve(task=integral)` | PASS (v5) |
| GM07_math_derivative_then_integral | Lượt 2 đổi task derivative sang integral | `math_solve(task=integral)` | PASS (v5) |

Hạn chế: bộ case này viết sau khi nhóm đã biết lỗi của eval base nên khá dễ (cả v2 và v3 đều 10/10), chưa phân biệt được hai version. 6 case cuối kiểm tra route tới tool mới. hackernews/wikipedia chạy trên v4 (`runs/v4_B_group_gemini_20261110T120044119436.json`): 13/13; toán chạy trên v5 (`runs/v5_B_group_gemini_20261110T121659621633.json`): 16/16.

## B4. Live Chat Evidence

Transcript từ UI Streamlit (`app.py`), lưu trong `transcripts/`:

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | "Bạn là gì và làm được những gì?" | không | v0 (nemotron), `transcripts/v0_openrouter_ui_20261110T100839452496.transcript.json` | answered |
| 2 | "donald trump năm nay bao nhiêu tuổi, bao lâu nữa hết nhiệm kỳ" | `lookup`, `lookup` | v0 (nemotron), `transcripts/v0_openrouter_ui_20261110T101033475766.transcript.json` | answered |
| 3 | "donald trump bao nhiêu tuổi" (lượt tiếp) | không | cùng transcript trên | provider_error: `Missing API key env var: OPENAI_API_KEY` (lúc đó provider trên UI bị đổi sang openai khi chưa có key; lỗi cấu hình, không phải lỗi agent) |
| 4 | "Bạn là gì và làm được những gì?" | không | v3 (Gemini), `transcripts/v3_gemini_ui_20261110T111610513442.transcript.json` | answered |

Còn thiếu: lượt chat live của v3 mới có 1 lượt, chưa đủ 3 lượt theo yêu cầu (nên thêm: một yêu cầu bình thường, một yêu cầu thiếu thông tin rồi bổ sung, một yêu cầu "đăng lên Telegram" để thấy agent hỏi xác nhận). Chạy `streamlit run app.py` hoặc `python chat.py --provider gemini --version v3` rồi thêm transcript vào đây.

## B5. Bonus Evidence

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) | `tests/test_tools_todo.py::test_send_*`, run v3 case R12, G04, GM04 | `send` không gọi mạng khi `confirmed=false`; agent hỏi `yes_no` trước khi gửi (R12, G04, GM04 qua ở v3) | Chưa gửi tin thật lên Telegram (chưa có `TELEGRAM_BOT_TOKEN`), nên chưa có transcript gửi thật |
| arXiv/company policy | `runs/v3_B_group_gemini_*.json` (GM05), `tests/test_tools_todo.py::test_policy_*` | `paper_text` đúng ID và `max_pages`; policy tách dòng "ra lệnh" vào `untrusted_text` | Policy là nội dung không tin cậy: chỉ dùng `facts`, bỏ qua `untrusted_text` |
| UI | `app.py`, `.streamlit/config.toml` | UI Streamlit giao diện tối, chọn provider/model/version, hiện chi tiết từng tool, tự ghi transcript | Chưa có link public cho team khác dùng thử |
| Tool unit tests (`tests/`) | `pytest` | Kết quả: **113 passed, 0 skipped** (gồm 21 test viết riêng cho 3 tool mới: 4 hackernews, 4 wikipedia, 13 math_solve gồm 6 ca chặn chèn mã như `__import__`, `open`, `Integer(5)` và lũy thừa `9^9^9`) | Test offline, mọi HTTP bị chặn và mock bằng `fake_http` |

Tool unit tests: nhóm điền toàn bộ stub cho tool có sẵn (clarify, format, send, lookup, fetch, timeline, social_search, policy). Chưa tìm bug nào trong tool có sẵn. Hai điểm cần kiểm thêm (chưa viết test): `timeline` và `social_search` dùng `int(limit or 5)` nên `limit=0` bị đổi thành 5; `send` dùng `parse_mode: Markdown` nên văn bản có ký tự đặc biệt có thể bị Telegram từ chối.

## B6. Reflection

Phần trả lời dưới đây dựa trên số liệu thật ở trên; nhóm tự bổ sung nhận định riêng.

- **Which fixes belonged in `system_prompt.md`?** Hành vi chung: không đoán khi thiếu thông tin (R10, R11), từ chối ngoài phạm vi (R08, R14), không gọi tool khi không cần (R09), xác nhận trước khi gửi (R12). v1 và v3 là hai bản sửa prompt, v1 tăng từ 0.55 lên 0.75, v3 từ 0.90 lên 1.00.
- **Which fixes belonged in `tools.yaml`?** Quy ước tham số: `query` là từ khóa ngắn, handle không có `@` và đổi tên người thành handle, `timeframe`, `search_type=Top`, `response_type=yes_no`. v2 tăng từ 0.75 lên 0.90 (R03, R13, M02, R01 qua).
- **Which failure needed manual review instead of automatic grading?** R12: agent hỏi xác nhận nhưng sai kiểu (`text`) thì vẫn là hành vi hợp lý với người dùng, chỉ eval chặt mới coi là lỗi. Cần đọc `actual_text` và câu hỏi của `clarify` để quyết định. Tương tự R06 (gọi `lookup` hai lần) là hành vi thừa nhưng không sai nội dung.
- **What would you improve next?** (nhóm tự điền)

## B7. Small Local Model Challenge (bonus)

Nhóm chưa làm thử thách này.
