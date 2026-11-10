# Day 03 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. **Xong trước 16:30** để làm tài liệu phụ trợ khi demo.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. **Có thể hoàn thiện sau buổi debate để nộp bài.**

## Team

- Team: `<Điền tên nhóm>`
- Trưởng nhóm: **Phan Hoàng Phúc (`2A202603455`)** — `<Điền phần việc phụ trách>`
- Thành viên:
  - **Nguyễn Tiến Cường (`2A202603425`)** — Phát triển & kiểm thử 2 tool mới (`sentiment`, `extract_keywords`), viết `TOOL.md`, 6 unit tests và kiểm tra live routing cho 2 tool mới.
  - **Lý Thành Lập (`2A202603414`)** — Phát triển & kiểm thử 2 tool mới (`github_search`, `hf_models`), viết `TOOL.md`, 6 unit tests (`tests/test_tools_lap.py`), tối ưu prompt/eval và dựng Streamlit UI.
  - **Lê Văn Hoàng (`2A202603357` — `@hoanglv2k9`)** — Phát triển & kiểm thử 2 tool mới (`citation_format`, `url_check`), viết `TOOL.md`, 6 unit tests (`tests/test_tools_hoang.py`), rà soát schema và đồng bộ hợp đồng tool contract.
 - **Lưu Đăng Tuấn (`2A202603454`)** — Phát triển & kiểm thử 2 tool mới (`tool_1`, `tool_2`), viết `TOOL.md`, xây dựng 6 unit tests (`tests/test_tools_tuan.py`), kiểm tra live routing cho 2 tool và tích hợp tool vào hệ thống.
- Provider/model: `<Điền provider/model chính của bản merge vào main>` *(2 tool mới đã kiểm thử trên Google Gemini `gemini-3.5-flash` & OpenRouter `openai/gpt-4o-mini`)*

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

> `<Trưởng nhóm / thành viên phụ trách bản main bổ sung mô tả tổng quan sau khi ghép xong các tool của nhóm>`

Research agent: tìm tin theo từ khóa / theo tài khoản, đọc URL, tổng hợp thành digest, gửi lên Telegram khi được xác nhận, đồng thời hỗ trợ phân tích cảm xúc văn bản (`sentiment`), trích xuất từ khóa / thống kê đọc (`extract_keywords`), tìm kiếm mã nguồn mở trên GitHub (`github_search`) và tìm kiếm mô hình AI/ML trên Hugging Face Hub (`hf_models`).

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
| `papers` | Tìm bài báo khoa học trên arXiv | **Có (Mới)** | **Lưu Đăng Tuấn** |
| `paper_text` | Tải PDF arXiv và trích xuất văn bản | **Có (Mới)** | **Lưu Đăng Tuấn** |
| `sentiment` | Phân tích sắc thái cảm xúc (tích cực, tiêu cực, trung lập), chấm điểm `[-1.0, 1.0]` và chỉ báo cảm xúc (hỗ trợ tiếng Việt & tiếng Anh) | **Có (Mới)** | **Nguyễn Tiến Cường** |
| `extract_keywords` | Trích xuất `top_n` từ khóa chính (lọc stopwords), hashtag (`#tag`), tổng số từ và thời gian đọc ước tính | **Có (Mới)** | **Nguyễn Tiến Cường** |
| `github_search` | Tìm kiếm mã nguồn mở và GitHub repositories theo từ khóa, sắp xếp theo `stars`/`forks`/`updated` | **Có (Mới)** | **Lý Thành Lập** |
| `hf_models` | Tìm kiếm mô hình AI/ML trên Hugging Face Hub theo từ khóa, sắp xếp theo `downloads`/`likes`/`lastModified` | **Có (Mới)** | **Lý Thành Lập** |
| `citation_format` | Tạo chuỗi trích dẫn chuẩn học thuật (APA, BibTeX, Markdown) từ tiêu đề, URL, tác giả và năm | **Có (Mới)** | **Lê Văn Hoàng** |
| `url_check` | Kiểm tra cú pháp URL và phân loại độ tin cậy nguồn tin theo chuẩn công ty (tier_1/2/3) | **Có (Mới)** | **Lê Văn Hoàng** |

## A3. Câu hỏi mẫu để thử

1. `<Câu hỏi mẫu cho core agent — thành viên phụ trách main điền>`
2. `<Câu hỏi mẫu cho core agent — thành viên phụ trách main điền>`
3. *(Test tool `sentiment` — Nguyễn Tiến Cường)*: `"Phân tích cảm xúc đoạn tin: 'Công nghệ AI vừa đạt bước đột phá xuất sắc và thành công vang dội'"`
4. *(Test tool `extract_keywords` — Nguyễn Tiến Cường)*: `"Trích xuất 3 từ khóa chính, hashtag và thời gian đọc của bài viết này: 'Artificial Intelligence #AI and Machine Learning #ML transform modern research. AI enables fast analysis.'"`
5. *(Test tool `github_search` — Lý Thành Lập)*: `"Tìm giúp mình 5 GitHub repository nhiều sao (stars) nhất về langgraph"`
6. *(Test tool `hf_models` — Lý Thành Lập)*: `"Tìm 3 model trên Hugging Face về Qwen2.5 được tải nhiều nhất"`
7. *(Test tool `citation_format` — Lê Văn Hoàng)*: `"Tạo trích dẫn chuẩn APA cho bài báo 'Attention Is All You Need' của tác giả 'Vaswani et al.' năm '2017' tại link https://arxiv.org/abs/1706.03762"`
8. *(Test tool `url_check` — Lê Văn Hoàng)*: `"Kiểm tra độ tin cậy và phân loại source tier của đường link này giúp mình: https://arxiv.org/abs/2210.03629"`
9. *(Test tool `papers` — Lưu Đăng Tuấn)*: `"Tìm giúp mình 3 bài báo trên arXiv về retrieval augmented generation"`
10. *(Test tool `paper_text` — Lưu Đăng Tuấn)*: `"Tóm tắt nội dung PDF tại https://arxiv.org/abs/2401.00001 cho mình"`


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
| *(Đề xuất cho tool mới — Lý Thành Lập)* | `G01_github_repo_routing`, `G02_hf_models_routing`, `GM02_multiturn_switch_to_github`: kiểm tra single-turn & multi-turn routing vào `github_search` và `hf_models` | `github_search(query="langgraph", sort="stars", max_results=5)` / `hf_models(query="Qwen2.5", sort="downloads", max_results=3)` | PASS 100% trên nhánh cá nhân `lythanhlap-2A202603414` | Lý Thành Lập |
| *(Đề xuất cho tool mới — Lê Văn Hoàng)* | Kiểm tra model route đúng vào `citation_format` khi yêu cầu định dạng trích dẫn & `url_check` khi yêu cầu kiểm tra link/phân loại nguồn | `citation_format(...)` / `url_check(...)` | PASS trên nhánh cá nhân `LeVanHoang-2A202603357` | Lê Văn Hoàng |
| *(Đề xuất cho tool mới — Lưu Đăng Tuấn)* | Kiểm tra model route đúng vào `papers` khi tìm bài báo & `paper_text` khi đọc nội dung cụ thể | `papers(...)` / `paper_text(...)` | PASS trên nhánh cá nhân `luutuan` | Lưu Đăng Tuấn |
## B4. Live Chat Evidence

Use `transcripts/*.transcript.json`:

| Turn | User Request | Tool Calls | Version Evidence | Outcome | Người test |
|---|---|---|---|---|---|
| `<Turn của bản main>` | | | | | `<Thành viên phụ trách main>` |
| Tool `sentiment` | "Phân tích cảm xúc đoạn này giúp mình: 'Công nghệ AI vừa đạt bước đột phá xuất sắc và thành công vang dội'" | `sentiment(text="...")` | `v3+p6cd3e198919a` | Trả về đúng `positive`, `score=1.0` | Nguyễn Tiến Cường |
| Tool `extract_keywords` | "Trích xuất 3 từ khóa chính, hashtag và thời gian đọc của bài viết này..." | `extract_keywords(top_n=3, text="...")` | `v3-gemini+p604e6c0a7a2e` | Gemini gọi đúng tool, trích xuất `AI`, `Artificial`, `Intelligence`, `#AI`, `#ML`, 14 từ | Nguyễn Tiến Cường |
| Tool `policy` (`external_publishing`) | "Theo policy công ty, đăng bản tin lên Telegram channel có cần xác nhận trước không?" | `policy(query="đăng bản tin lên Telegram", policy_area="external_publishing")` | `v3+pada960ec5ce4+t5b22a2476d41` | Trích xuất đúng mục `Telegram channel` và `Publishing approval` từ handbook nội bộ | Lý Thành Lập |
| Tool `github_search` & `hf_models` | "Tìm giúp mình 5 GitHub repository nhiều sao nhất về langgraph" / "Tìm 3 model trên Hugging Face về Qwen2.5 được tải nhiều nhất" | `github_search(query="langgraph", sort="stars", max_results=5)` / `hf_models(query="Qwen2.5", sort="downloads", max_results=3)` | `v3+pc46c75e36ae9+tb8c05fc889da` | Model chọn đúng tool và truyền chính xác `sort`, `max_results` | Lý Thành Lập |
| Tool `citation_format` | "Tạo trích dẫn chuẩn APA cho bài báo 'Attention Is All You Need'..." | `citation_format(style="apa", title="Attention Is All You Need", authors=["Vaswani et al."], year=2017, url="https://arxiv.org/abs/1706.03762")` | `v3+citation_format` | Trả về đúng định dạng chuẩn APA và BibTeX | Lê Văn Hoàng |
| Tool `url_check` | "Kiểm tra độ tin cậy của link https://arxiv.org/abs/2210.03629" | `url_check(url="https://arxiv.org/abs/2210.03629")` | `v3+url_check` | Trả về `valid=True`, `tier="tier_1"` (academic source) | Lê Văn Hoàng |
| Tool `papers` | "Cho mình 5 paper mới nhất về diffusion model trên arXiv" | `papers(query="diffusion model", max_results=5, sort_by="date")` | `v3+papers` | `items` tối đa 5 phần tử, sắp xếp theo `published` giảm dần | Lưu Đăng Tuấn |
|Tool `paper_text` | "Đọc giúp mình nội dung bài arXiv 2401.00001" | `paper_text(arxiv_id="2401.00001")` | `v3+paper_text` | `tool: "get_paper_text"`, `text` không rỗng, `pages_read` không vượt quá 10 | Lưu Đăng Tuấn |

## B5. Bonus Evidence

| Bonus | Evidence File | What Worked | Risk / Guardrail | Người thực hiện |
|---|---|---|---|---|
| send (Telegram) | | | | `<Thành viên phụ trách main>` |
| arXiv/company policy | | | | `<Thành viên phụ trách main>` |
| UI | | | | `<Thành viên phụ trách main>` |
| 2 Tool mới (`sentiment`, `extract_keywords`) | `tools/sentiment/`, `tools/extract_keywords/` | `sentiment` xử lý tiếng Việt có dấu & tiếng Anh; `extract_keywords` tách từ khóa ≥ 2 ký tự, `#tag` & tính reading time | Kiểm tra kiểu dữ liệu đầu vào (`TypeError`/`ValueError`), trả về error dict an toàn thay vì crash | **Nguyễn Tiến Cường** |
| 2 Tool mới (`github_search`, `hf_models`) | `tools/github_search/`, `tools/hf_models/` | Tìm kiếm repo trên GitHub REST API (`stars`/`forks`/`updated`) và model trên Hugging Face Hub API (`downloads`/`likes`/`lastModified`) | Giới hạn `max_results` trong `[1, 10]`, kiểm tra chuỗi rỗng và bắt lỗi mạng qua `err()` | **Lý Thành Lập** |
| 2 Tool mới (`citation_format`, `url_check`) | `tools/citation_format/`, `tools/url_check/` | `citation_format` sinh định dạng APA, BibTeX, Markdown; `url_check` kiểm tra regex URL, phân loại domain tier 1/2/3 | Bắt lỗi thiếu field bắt buộc, URL sai cú pháp hoặc kiểu dữ liệu không hợp lệ qua dict error | **Lê Văn Hoàng** |
| 2 Tool mới (`papers`, `paper_text`) | `tools/papers.py`, `tools/paper_text.py`, `tests/testtools<TenBan>.py` | `papers` tìm bài arXiv qua API, parse Atom XML thành danh sách có `arxiv_id`, `title`, `authors`, `published`, `pdf_url`; `paper_text` chuẩn hoá ID hoặc URL arXiv, tải PDF và trích văn bản bằng `pypdf` | `papers` kiểm tra query rỗng, giới hạn `max_results` từ 1 đến 20, timeout 20 giây; `paper_text` validate ID bằng regex, giới hạn trang đọc (mặc định 10) và số ký tự trả về (mặc định 8000), timeout 30 giây; các lỗi đầu vào trả về error dict thay vì crash | ` **Lưu Đăng Tuấn** |
| Tool unit tests (`tests/`) | `tests/test_tools_cuong.py`, `tests/test_tools_lap.py`, `tests/test_tools_hoang.py` | **6 unit tests** của Cường + **6 unit tests** của Lập + **6 unit tests** của Hoàng pass 100% | Cô lập hoàn toàn offline, kiểm tra happy path, bad input và edge cases | **Nguyễn Tiến Cường, Lý Thành Lập, Lê Văn Hoàng** |

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

### Phần đúc kết của Lý Thành Lập (đóng góp 2 tool mới `github_search`, `hf_models` & unit test):
- Với các công cụ gọi REST API bên ngoài (`github_search`, `hf_models`), việc chuẩn hoá tham số đầu vào (cắt khoảng trắng thừa của `query`, giới hạn `max_results` trong khoảng `1..10`, ép `sort` về giá trị hợp lệ) giúp công cụ hoạt động ổn định ngay cả khi LLM truyền giá trị biên.
- Viết unit test với fixture `fake_http` giúp xác minh đồng thời cả URL/query params gửi lên server lẫn cấu trúc dữ liệu trả về (`items`, `source`, `url`) hoàn toàn offline mà không phụ thuộc vào hạn mức rate-limit của GitHub hay Hugging Face.

### Phần đúc kết của Lê Văn Hoàng (đóng góp 2 tool mới `citation_format`, `url_check` & unit test):
- Thiết kế tool học thuật (`citation_format`) và kiểm tra nguồn (`url_check`) cần định nghĩa rõ kiểu dữ liệu trong `tools.yaml` (ví dụ `style` enum, `authors` list/string), giúp LLM không tự ý sinh tham số sai lệch.
- Việc bổ sung unit test (≥ 3 tests mỗi tool) với các trường hợp biên (URL không có scheme, tác giả dạng chuỗi/danh sách) đảm bảo tool luôn trả kết quả ổn định và bắt lỗi an toàn trước khi tích hợp vào agent.
### Phần đúc kết của Lưu Đăng Tuấn (đóng góp 2 tool mới `papers`, `paper_text` & unit test):
- Khi thiết kế tool mới cho Research Agent (`papers`, `paper_text`), phần mô tả "khi nào dùng / KHÔNG dùng" trong `tools.yaml` và chuẩn frontmatter `TOOL.md` giúp model phân biệt rạch ròi với các tool sẵn có (`lookup`, `format`), không gây nhiễu cho bộ core eval. `papers` chỉ dùng cho nghiên cứu học thuật trên arXiv, không dùng cho tin tức; `paper_text` chỉ dùng khi đã có arXiv ID hoặc URL, còn nếu user chỉ có tên bài thì gọi `papers` trước.
- Unit test offline (kiểm tra happy path, kiểu dữ liệu lỗi từ model, input rỗng) là lớp bảo vệ bắt buộc vì eval chỉ kiểm tra model có chọn đúng tên tool và tham số hay không, chứ không bắt được lỗi logic bên trong hàm thực thi tool. Bộ test của `papers` và `paper_text` dùng mock nên không cần mạng hay API key, bao phủ parse Atom XML, chuẩn hoá ID/URL.

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
