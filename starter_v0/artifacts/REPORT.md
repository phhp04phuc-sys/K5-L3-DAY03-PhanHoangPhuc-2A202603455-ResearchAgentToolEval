# Day 03 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. **Xong trước 16:30** để làm tài liệu phụ trợ khi demo.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. **Có thể hoàn thiện sau buổi debate để nộp bài.**

## Team

- Team: `<Điền tên nhóm>`
- Trưởng nhóm: **Phan Hoàng Phúc (`2A202603455`)** — `<Điền phần việc phụ trách>`
- Thành viên:
  - **Nguyễn Tiến Cường (`2A202603425`)** — Phát triển & kiểm thử 2 tool mới (`sentiment`, `extract_keywords`), viết `TOOL.md`, 6 unit tests và kiểm tra live routing cho 2 tool mới.
  - `<Thành viên 3 — Họ tên (MSSV) — Phần việc phụ trách>`
  - `<Thành viên 4 — Họ tên (MSSV) — Phần việc phụ trách>`
- Provider/model: `<Điền provider/model chính của bản merge vào main>` *(2 tool mới đã kiểm thử trên Google Gemini `gemini-3.5-flash` & OpenRouter `openai/gpt-4o-mini`)*

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

> `<Trưởng nhóm / thành viên phụ trách bản main bổ sung mô tả tổng quan sau khi ghép xong các tool của nhóm>`

Research agent: tìm tin theo từ khóa / theo tài khoản, đọc URL, tổng hợp thành digest, gửi lên Telegram khi được xác nhận, đồng thời hỗ trợ phân tích cảm xúc văn bản (`sentiment`) và trích xuất từ khóa / thống kê đọc (`extract_keywords`).

**Link dùng thử (deploy):**

> URL: `<Dán link public deploy (Cloudflare Tunnel / Streamlit Cloud / Vercel) tại đây>`

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? | Người phụ trách |
|---|---|---|---|
| `clarify` | Hỏi lại người dùng khi thiếu thông tin hoặc cần xác nhận | Không | Có sẵn (Starter) |
| `timeline` | Lấy các bài đăng gần đây của một tài khoản | Không | Có sẵn (Starter) |
| `social_search` | Tìm bài đăng trên mạng xã hội theo từ khóa | Không | Có sẵn (Starter) |
| `lookup` | Tra cứu thông tin / tin tức trên web | Không | Có sẵn (Starter) |
| `fetch` | Đọc nội dung từ một URL cụ thể | Không | Có sẵn (Starter) |
| `format` | Trình bày các item thành markdown digest | Không | Có sẵn (Starter) |
| `send` | Gửi tin lên Telegram (chỉ gửi khi `confirmed=true`) | Không | Có sẵn (Starter) |
| `policy` | Tìm kiếm trong company policy nội bộ | Không | Có sẵn (Starter) |
| `papers` | Tìm bài báo khoa học trên arXiv | Không | Có sẵn (Starter) |
| `paper_text` | Tải PDF arXiv và trích xuất văn bản | Không | Có sẵn (Starter) |
| `sentiment` | Phân tích sắc thái cảm xúc (tích cực, tiêu cực, trung lập), chấm điểm `[-1.0, 1.0]` và chỉ báo cảm xúc (hỗ trợ tiếng Việt & tiếng Anh) | **Có (Mới)** | **Nguyễn Tiến Cường** |
| `extract_keywords` | Trích xuất `top_n` từ khóa chính (lọc stopwords), hashtag (`#tag`), tổng số từ và thời gian đọc ước tính | **Có (Mới)** | **Nguyễn Tiến Cường** |
| `<tool_moi_3>` | `<Thành viên khác điền mô tả tool mới tại đây>` | Có | `<Tên thành viên>` |
| `<tool_moi_4>` | `<Thành viên khác điền mô tả tool mới tại đây>` | Có | `<Tên thành viên>` |

## A3. Câu hỏi mẫu để thử

1. `<Câu hỏi mẫu cho core agent — thành viên phụ trách main điền>`
2. `<Câu hỏi mẫu cho core agent — thành viên phụ trách main điền>`
3. *(Test tool `sentiment` — Nguyễn Tiến Cường)*: `"Phân tích cảm xúc đoạn tin: 'Công nghệ AI vừa đạt bước đột phá xuất sắc và thành công vang dội'"`
4. *(Test tool `extract_keywords` — Nguyễn Tiến Cường)*: `"Trích xuất 3 từ khóa chính, hashtag và thời gian đọc của bài viết này: 'Artificial Intelligence #AI and Machine Learning #ML transform modern research. AI enables fast analysis.'"`
5. `<Câu hỏi mẫu cho tool mới của thành viên khác>`

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

Fill from `artifacts/version_log.csv` and `runs/*.json` của bản chính trên `main`:

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | | | | |
| v1 | | | | | |
| v2 | | | | | |
| v3 | | | | | |

## B2. Failure Analysis

Use actual failures from `results[*].result.failures` của bản chính trên `main`:

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| | | | | |

## B3. Team Eval Cases

List the 10 cases added to `data/eval_group.json` (5 single turn + 5 multi turn):

| Case ID | What It Tests | Expected Tool/Behavior | Result | Người viết |
|---|---|---|---|---|
| `<G01...>` | | | | `<Thành viên phụ trách main>` |
| | | | | |
| *(Đề xuất cho tool mới — Nguyễn Tiến Cường)* | Kiểm tra model route đúng vào `sentiment` khi yêu cầu phân tích cảm xúc & `extract_keywords` khi yêu cầu rút trích từ khóa | `sentiment(...)` / `extract_keywords(...)` | PASS trên nhánh cá nhân `nguyentiencuong-2A202603425` | Nguyễn Tiến Cường |

## B4. Live Chat Evidence

Use `transcripts/*.transcript.json`:

| Turn | User Request | Tool Calls | Version Evidence | Outcome | Người test |
|---|---|---|---|---|---|
| `<Turn của bản main>` | | | | | `<Thành viên phụ trách main>` |
| Tool `sentiment` | "Phân tích cảm xúc đoạn này giúp mình: 'Công nghệ AI vừa đạt bước đột phá xuất sắc và thành công vang dội'" | `sentiment(text="...")` | `v3+p6cd3e198919a` | Trả về đúng `positive`, `score=1.0` | Nguyễn Tiến Cường |
| Tool `extract_keywords` | "Trích xuất 3 từ khóa chính, hashtag và thời gian đọc của bài viết này..." | `extract_keywords(top_n=3, text="...")` | `v3-gemini+p604e6c0a7a2e` | Gemini gọi đúng tool, trích xuất `AI`, `Artificial`, `Intelligence`, `#AI`, `#ML`, 14 từ | Nguyễn Tiến Cường |
| `<Turn của thành viên khác>` | | | | | |

## B5. Bonus Evidence

| Bonus | Evidence File | What Worked | Risk / Guardrail | Người thực hiện |
|---|---|---|---|---|
| send (Telegram) | | | | `<Thành viên phụ trách main>` |
| arXiv/company policy | | | | `<Thành viên phụ trách main>` |
| UI | | | | `<Thành viên phụ trách main>` |
| 2 Tool mới (`sentiment`, `extract_keywords`) | `tools/sentiment/`, `tools/extract_keywords/` | `sentiment` xử lý tiếng Việt có dấu & tiếng Anh; `extract_keywords` tách từ khóa ≥ 2 ký tự, `#tag` & tính reading time | Kiểm tra kiểu dữ liệu đầu vào (`TypeError`/`ValueError`), trả về error dict an toàn thay vì crash | **Nguyễn Tiến Cường** |
| Tool unit tests (`tests/`) | `tests/test_tools_todo.py` / `pytest` | **6 unit tests** riêng cho 2 tool mới (`sentiment` + `extract_keywords`) pass offline 100% *(chờ ghép tổng hợp với unit tests của nhánh `main` và các thành viên khác)* | Cô lập hoàn toàn offline, kiểm tra cả happy path, bad input type và empty input | **Nguyễn Tiến Cường** *(+ thành viên khác điền thêm)* |
| `<Tool mới khác của nhóm>` | | | | `<Thành viên khác>` |

**Ví dụ lỗi thực tế ở 2 tool mới mà Unit test / Live test bắt được nhưng Eval không bắt được (Nguyễn Tiến Cường):**
1. **Tool `sentiment`**: Khi test live câu tiếng Việt có dấu *"Công nghệ AI vừa đạt bước đột phá xuất sắc và thành công vang dội"*, Eval chỉ chấm tên tool (`name == "sentiment"`) nên vẫn báo PASS, nhưng thực tế kết quả trả về `score = 0.0 (neutral)` vì logic tách từ đơn lẻ không khớp cụm 2 chữ có dấu (`"xuất sắc"`, `"thành công"`). Sau khi dùng `fold_text` + regex khớp cụm từ và viết test kiểm chứng tiếng Việt có dấu, tool trả về chuẩn `score = 1.0 (positive)`.
2. **Tool `extract_keywords`**: Unit test `test_extract_keywords_happy_path` phát hiện điều kiện `len(tok) > 2` làm rơi mất các từ khóa quan trọng dài 2 ký tự như `ai`, `ml`. Đã sửa thành `len(tok) >= 2` kết hợp bộ lọc stopwords để giữ nguyên các thuật ngữ này.

## B6. Reflection

### Phần đúc kết của nhóm về Core Prompt & Tools (bản `main`):
- Which fixes belonged in `system_prompt.md`? `<Thành viên phụ trách main điền>`
- Which fixes belonged in `tools.yaml`? `<Thành viên phụ trách main điền>`
- Which failure needed manual review instead of automatic grading? `<Thành viên phụ trách main điền>`
- What would you improve next? `<Thành viên phụ trách main điền>`

### Phần đúc kết của Nguyễn Tiến Cường (đóng góp 2 tool mới & unit test):
- Khi thiết kế tool mới cho Research Agent (`sentiment`, `extract_keywords`), phần mô tả "khi nào dùng / KHÔNG dùng" trong `tools.yaml` và chuẩn frontmatter `TOOL.md` giúp model phân biệt rạch ròi với các tool sẵn có (`lookup`, `format`), không gây nhiễu cho bộ core eval.
- Unit test offline (kiểm tra happy path, kiểu dữ liệu lỗi từ model, input rỗng) là lớp bảo vệ bắt buộc vì eval chỉ kiểm tra model có chọn đúng tên tool và tham số hay không, chứ không bắt được lỗi logic bên trong hàm thực thi tool.

### Phần nhận xét / bổ sung của Trưởng nhóm (Phan Hoàng Phúc) & các thành viên khác:
- `<Phan Hoàng Phúc và các thành viên khác viết cảm nhận & đúc kết tại đây>`

---

## B7. Small Local Model Challenge (bonus)

Only fill if your team did the local model challenge.

| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---|---|---|---|---|
| v3 | (cloud) | v3 | | | | | |
| v3-... | (ollama) | v3 | | | | | |
| v3-... | (ollama) | v3 | | | | | |
| v4-local | | | | | | | |
| v5-local | | | | | | | |

Lỗi đặc thù của model nhỏ (đếm từ run JSON):

| Failure Pattern | Count | Example Case | Fix Tried | Helped? |
|---|---|---|---|---|
| wrong / hallucinated tool | | | | |
| invalid JSON args (`_invalid_json_arguments`) | | | | |
| no tool call / answered directly | | | | |
| missed `clarify` | | | | |
| repeated / unnecessary calls | | | | |

- Cái gì giúp model nhỏ gọi tool đúng hơn nhất? Bằng chứng?
- Bản prompt tối ưu cho local chạy trên model cloud thì sao?
- Khi nào nhóm sẽ chọn model local thay vì cloud cho agent này?
