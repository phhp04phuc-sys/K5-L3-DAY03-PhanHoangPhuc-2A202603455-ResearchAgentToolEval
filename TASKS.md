# TASKS — Chia việc và nhánh làm việc (Day 03, nhóm Nhomnhom)

Repo nhóm: https://github.com/phhp04phuc-sys/K5-L3-DAY03-PhanHoangPhuc-2A202603455-ResearchAgentToolEval
Hạn nộp lên LMS: **23:59 hôm nay**. Commit càng sớm càng tốt để còn thời gian sửa lỗi và gộp.

## Cách tổ chức nhánh

| Nhánh | Chủ | Nội dung |
|---|---|---|
| `main` | cả nhóm | Bản **nộp bài**. Hiện đang là bản starter gốc của giảng viên; cuối cùng Phúc gộp `phucphan/core` vào đây |
| `phucphan/core` | Phúc | Toàn bộ code hiện tại: agent, UI, 3 tool mới, nguồn uy tín, test, eval, báo cáo. **Đây là nền để mọi người làm tiếp** |
| `kegacua/tools` | kegacua | Phần file của kegacua (bảng bên dưới) |
| `cuong-sadboi/tools` | cuong-sadboi | Phần file của cuong-sadboi |
| `lythanhlap/ui` | lythanhlap | Phần file của lythanhlap |
| `hoanglv2k9/eval-report` | hoanglv2k9 | Phần file của hoanglv2k9 |

Quy trình: mỗi người làm trên **nhánh của mình**, commit bằng **tài khoản của mình**, rồi mở Pull Request vào `phucphan/core`. Khi mọi PR đã gộp và `pytest` xanh, Phúc gộp `phucphan/core` vào `main`. **Commit chỉ được tính vào đóng góp của repo sau khi gộp vào nhánh mặc định (`main`).**

> Lưu ý: nhánh của bạn mới tạo từ bản starter, chưa có code của nhóm. Việc đầu tiên là kéo `phucphan/core` về nhánh của bạn (Bước 1 bên dưới).

## Hiện trạng trên `phucphan/core` (đã xong, đừng làm lại)
- Agent chạy với Gemini, giao diện `app.py`, prompt/tools đến bản v6, log `runs/`, `REPORT.md`.
- 3 tool mới: `hackernews`, `wikipedia`, `math_solve`; phân tầng nguồn uy tín (`tools/source_trust.py`).
- `pytest`: 131 qua, 0 skip. Eval nhóm: 19 case, đều qua. Eval base: 19/20 (R08 lỗi **chủ ý**, đừng sửa).
- Slide ghi điểm thưởng khi có **UI và hơn 3 tool mới**: nhóm cần **thêm tool**.

## Phần file của mỗi người (trong `starter_v0/`)

| Người | Phần file được giao | Tool mới (gợi ý, không cần key) | Việc thêm |
|---|---|---|---|
| **kegacua** | `tools/clarify`, `tools/format`, `tools/send`, `tools/lookup`, `tools/fetch` (đọc kỹ, viết thêm test nếu thiếu) | `github_repo` (sao, ngôn ngữ, release mới nhất; `https://api.github.com/repos/{owner}/{repo}`) và `rss_feed` (tiêu đề từ RSS/Atom) | |
| **cuong-sadboi** | `tools/timeline`, `tools/social_search`, `tools/policy`, `tools/papers`, `tools/paper_text` (đọc kỹ, viết thêm test nếu thiếu) | `currency_convert` (`https://open.er-api.com/v6/latest/USD`, có VND) và `unit_convert` (tính cục bộ, không cần mạng) | |
| **lythanhlap** | `app.py`, `.streamlit/`, `chat.py`, `providers/` | `weather` (2 bước: `https://geocoding-api.open-meteo.com/v1/search?name=...` rồi `https://api.open-meteo.com/v1/forecast?...&current=temperature_2m`) | Chạy UI, mở link dùng thử, ghi vào `artifacts/REPORT.md` mục A1 |
| **hoanglv2k9** | `data/eval_group.json`, `artifacts/REPORT.md`, `company_policy/`, `scripts/` | `pypi_package` (`https://pypi.org/pypi/{tên}/json`) | Viết B6 trong `REPORT.md`, thêm 3 lượt chat live trên UI (transcript) |
| **Phúc** | `artifacts/` (prompt, `tools.yaml`, `version_log.csv`), `run_eval.py`, `runs/`, `tools/source_trust.py`, gộp nhánh và nộp bài | | |

Mỗi người làm **1 đến 2 tool**. Đổi tool khác được nếu: **không trùng người khác**, **không cần API key**, **chỉ đọc dữ liệu** (không gửi, xóa, ghi ra ngoài). Mình đã kiểm tra các địa chỉ API ở bảng trên đều trả về 200.

## Một tool được tính là xong khi đủ 5 thứ
1. `tools/<tên>/tool.py` và `tools/<tên>/TOOL.md`. Copy khuôn từ `tools/hackernews/`.
2. Đăng ký trong `starter_v0/tools/__init__.py` (1 dòng import, 1 dòng trong `TOOL_FUNCTIONS`).
3. Khai báo trong `starter_v0/artifacts/tools.yaml`: **thêm ở cuối file**, mô tả phải nói rõ **khi nào dùng và khi nào không dùng**.
4. **Ít nhất 3 unit test**: đúng, input xấu (rỗng, sai kiểu, ngoài khoảng), nhánh lỗi (HTTP lỗi trả `error` dict, không văng lỗi). Viết ở **cuối** `starter_v0/tests/test_tools_todo.py`, mock mạng bằng `fake_http` (xem test của `hackernews`).
5. **Ít nhất 2 case eval** trong `starter_v0/data/eval_group.json` (1 một lượt, 1 nhiều lượt), thêm **ở cuối** danh sách `cases`. ID theo đầu số riêng để không trùng: kegacua `G2x`/`GM2x`, cuong-sadboi `G3x`/`GM3x`, lythanhlap `G4x`/`GM4x`, hoanglv2k9 `G5x`/`GM5x`.

Kiểm tra trước khi commit:

```bash
cd starter_v0 && source .venv/bin/activate
python -m pytest -q
python run_eval.py --provider gemini --suite group --eval-cases data/eval_group.json --version v7-<tên-bạn>
```

Case nào lỗi thì đọc `runs/...json` xem agent gọi gì, rồi sửa **mô tả tool** cho rõ hơn (đừng sửa đáp án để ép cho qua).

## Cách làm việc và commit (để được tính đóng góp)

Đóng góp chỉ hiện trên GitHub khi **email trong commit khớp với tài khoản GitHub của bạn**.

**Bước 0. Một lần duy nhất: đặt đúng tên và email**

Lấy email đã xác minh ở GitHub: Settings → Emails (hoặc địa chỉ dạng `<số>+<username>@users.noreply.github.com` ở cùng trang).

```bash
git config --global user.name "Tên của bạn"
git config --global user.email "email-da-xac-minh@..."
git config user.email          # in ra để kiểm tra
```

**Bước 1. Về nhánh của bạn và kéo code nền về**

Thay `<nhánh-của-bạn>` bằng nhánh ở bảng trên (ví dụ `kegacua/tools`).

```bash
git clone https://github.com/phhp04phuc-sys/K5-L3-DAY03-PhanHoangPhuc-2A202603455-ResearchAgentToolEval.git
cd K5-L3-DAY03-PhanHoangPhuc-2A202603455-ResearchAgentToolEval
git checkout <nhánh-của-bạn>
git merge origin/phucphan/core -m "Merge core into my branch"     # kéo code nền của nhóm vào nhánh của bạn
cd starter_v0 && python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && cp .env.example .env              # tự điền key model của bạn
```

**Bước 2. Làm việc, rồi chỉ thêm đúng file của bạn**

```bash
git status
git add starter_v0/tools/<tên-tool> starter_v0/tools/__init__.py starter_v0/artifacts/tools.yaml starter_v0/tests/test_tools_todo.py starter_v0/data/eval_group.json
git status                       # kiểm tra lần cuối: KHÔNG được có file .env
git commit -m "Add <tên-tool> tool with tests and eval cases"
```

Không dùng `git add .` hay `git add -A`. **Tuyệt đối không commit `.env`** (chứa key). Không thêm dòng `Co-Authored-By` vào commit, để lịch sử ghi đúng tên bạn.

**Bước 3. Đẩy nhánh và mở Pull Request vào `phucphan/core`**

```bash
git push origin <nhánh-của-bạn>
```

Rồi vào GitHub, tab **Pull requests**, **New pull request**, chọn **base: `phucphan/core`**, **compare: nhánh của bạn**, đặt tiêu đề rõ ràng, và nhắn Phúc: "PR xong". Bạn có quyền Write nên cũng tự bấm **Merge** được sau khi `pytest` xanh.

**Bước 4. Nếu bị xung đột (conflict) ở `tools.yaml`, `__init__.py` hoặc `eval_group.json`**

Đây là 3 file mọi người cùng sửa. Giữ **cả hai** phần (của bạn và của người khác), không xóa phần của ai.

```bash
git fetch origin
git merge origin/phucphan/core
# mở file bị báo conflict, giữ cả hai khối giữa <<<<<<< và >>>>>>>, xóa các dòng dấu đó
python -m pytest -q
git add <file-vừa-sửa> && git commit
git push origin <nhánh-của-bạn>
```

Không biết xử lý thì nhắn Phúc, đừng xóa code của người khác.

## Việc thêm cho lythanhlap: UI và link dùng thử

```bash
cd starter_v0 && source .venv/bin/activate
streamlit run app.py                         # http://localhost:8501
```

Cửa sổ terminal khác (cài trước: `brew install cloudflared`):

```bash
cloudflared tunnel --url http://localhost:8501
```

Copy link `https://....trycloudflare.com` vào `starter_v0/artifacts/REPORT.md` mục **A1, dòng URL**. Link chỉ sống khi lệnh còn chạy, nên giữ lệnh chạy lúc demo.

## Việc thêm cho hoanglv2k9: báo cáo
- Mục **B6** trong `REPORT.md`: dòng "What would you improve next?" bạn **tự viết bằng ý của mình** (phần nhận định, đừng nhờ AI viết hộ).
- Chạy UI và hỏi 3 lượt: một yêu cầu bình thường, một yêu cầu thiếu thông tin rồi bổ sung, một yêu cầu "đăng lên Telegram" để thấy agent hỏi xác nhận. Transcript tự lưu trong `starter_v0/transcripts/`; commit các file đó và ghi vào mục **B4**.

## Cả nhóm: điền phần của mình trong `TEAM.md`
Họ tên thật, MSSV, và 1 đến 3 dòng "Đóng góp cá nhân" (chỉ ghi việc đã làm thật). Thêm vào cùng PR với phần của bạn.

## Lưu ý quan trọng
- **Không đổi tên** `hackernews`, `wikipedia`, `math_solve`, và không sửa case trong `data/eval_base.json` (bài cấm). Case base **R08** lỗi là chủ ý.
- Không sửa `artifacts/system_prompt.md` mà không báo Phúc (file chung, dễ làm hỏng điểm).
- Kẹt hơn 10 phút thì hỏi trong nhóm. Thiếu thời gian thì làm **1 tool cho thật chắc** (đủ 5 thứ) còn hơn 2 tool dở dang.
- Nhánh `test0911` trong repo là nhánh có sẵn từ repo gốc của giảng viên, không phải của nhóm; đừng đụng vào.
- **Nộp bài:** chỉ nộp link repo trên LMS **sau khi** Phúc đã gộp vào `main`. Trước đó `main` chỉ là bản starter, chấm sẽ không thấy gì.
