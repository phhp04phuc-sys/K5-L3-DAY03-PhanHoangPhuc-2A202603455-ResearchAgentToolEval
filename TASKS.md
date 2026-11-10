# TASKS — Việc của cả nhóm (Day 03, nhóm Nhomnhom)

Repo nhóm (cũng là bài nộp): https://github.com/phhp04phuc-sys/K5-L3-DAY03-PhanHoangPhuc-2A202603455-ResearchAgentToolEval
Hạn nộp lên LMS: **23:59 hôm nay**. Commit và gộp càng sớm càng tốt để còn thời gian sửa lỗi.

## Tóm tắt phân việc
- **Phúc** đã làm xong phần nền (đang nằm trên `main`): agent, giao diện, prompt/tools đến bản v6, 3 tool mới, nguồn uy tín, test, eval, báo cáo.
- **Mỗi bạn còn lại (kegacua, cuong-sadboi, lythanhlap, hoanglv2k9) thêm 1 đến 2 tool mới, kèm test và case eval cho tool đó.**
- Các bạn tự thống nhất với nhau ai làm tool nào để **không trùng** (gợi ý bên dưới). Làm xong thì push nhánh của mình lên rồi gộp vào `main`.

Lý do cần thêm tool: slide ghi điểm thưởng khi có **UI và hơn 3 tool mới**. Nhóm đang có 3 tool mới (`hackernews`, `wikipedia`, `math_solve`), nên chỉ cần thêm.

## Hiện trạng trên `main` (đã xong, đừng làm lại)
- Agent chạy với Gemini, UI `app.py`, log `runs/`, `REPORT.md`, `TEAM.md`.
- `pytest`: 131 qua, 0 skip. Eval nhóm: 19 case, đều qua. Eval base: 19/20.
- Case base **R08** lỗi là **chủ ý** (agent giờ giải được tích phân). Đừng sửa.

## Gợi ý tool (không cần API key, chỉ đọc dữ liệu)
Mỗi người chọn 1 đến 2 tool, hoặc tự nghĩ tool khác miễn là **không trùng**, **không cần key**, **không gửi/xóa/ghi gì ra ngoài**.

| Gợi ý | Mô tả | API |
|---|---|---|
| `github_repo` | sao, ngôn ngữ, release mới nhất của một repo | `https://api.github.com/repos/{owner}/{repo}` |
| `rss_feed` | tiêu đề từ một RSS/Atom | URL feed người dùng đưa |
| `currency_convert` | đổi tiền, có VND | `https://open.er-api.com/v6/latest/USD` |
| `unit_convert` | đổi đơn vị | tính cục bộ bằng Python, không cần mạng |
| `weather` | thời tiết (2 bước) | `https://geocoding-api.open-meteo.com/v1/search?name=...` rồi `https://api.open-meteo.com/v1/forecast?...&current=temperature_2m` |
| `pypi_package` | thông tin một thư viện Python | `https://pypi.org/pypi/{tên}/json` |

Mình đã kiểm tra các địa chỉ API trên đều trả về 200.

## Một tool được tính là xong khi đủ 5 thứ
1. `starter_v0/tools/<tên>/tool.py` và `TOOL.md`. Copy khuôn từ `tools/hackernews/` (cùng cách ép tham số và xử lý lỗi).
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

Mỗi người **tự tạo nhánh của mình** từ `main`, commit bằng **tài khoản của mình**, push nhánh lên, rồi gộp vào `main`. Đóng góp chỉ hiện trên GitHub khi **email trong commit khớp với tài khoản GitHub của bạn** và commit nằm trên `main` (sau khi gộp).

**Bước 0. Một lần duy nhất: đặt đúng tên và email**

Lấy email đã xác minh ở GitHub: Settings → Emails (hoặc địa chỉ dạng `<số>+<username>@users.noreply.github.com` ở cùng trang).

```bash
git config --global user.name "Tên của bạn"
git config --global user.email "email-da-xac-minh@..."
git config user.email          # in ra để kiểm tra
```

**Bước 1. Lấy code và tạo nhánh riêng**

Đặt tên nhánh dạng `<username>/<tên-tool>`, ví dụ `kegacua/github-repo`.

```bash
git clone https://github.com/phhp04phuc-sys/K5-L3-DAY03-PhanHoangPhuc-2A202603455-ResearchAgentToolEval.git
cd K5-L3-DAY03-PhanHoangPhuc-2A202603455-ResearchAgentToolEval
git checkout -b <username>/<tên-tool>
cd starter_v0 && python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && cp .env.example .env              # tự điền key model của bạn
```

(đã clone từ trước thì chạy `git checkout main && git pull` rồi tạo nhánh.)

**Bước 2. Làm việc, rồi chỉ thêm đúng file của bạn**

```bash
git status
git add starter_v0/tools/<tên-tool> starter_v0/tools/__init__.py starter_v0/artifacts/tools.yaml starter_v0/tests/test_tools_todo.py starter_v0/data/eval_group.json
git status                       # kiểm tra lần cuối: KHÔNG được có file .env
git commit -m "Add <tên-tool> tool with tests and eval cases"
```

Không dùng `git add .` hay `git add -A`. **Tuyệt đối không commit `.env`** (chứa key). Không thêm dòng `Co-Authored-By` vào commit, để lịch sử ghi đúng tên bạn.

**Bước 3. Đẩy nhánh và gộp vào `main`**

```bash
git push -u origin <username>/<tên-tool>
```

Rồi vào GitHub, tab **Pull requests**, **New pull request**, base là `main`, compare là nhánh của bạn, đặt tiêu đề rõ ràng. Bạn có quyền Write nên tự bấm **Merge** được sau khi `pytest` xanh, hoặc nhắn Phúc.

**Bước 4. Nếu bị xung đột (conflict) ở `tools.yaml`, `__init__.py` hoặc `eval_group.json`**

Đây là 3 file mọi người cùng sửa (ai gộp sau sẽ gặp). Giữ **cả hai** phần (của bạn và của người khác), không xóa phần của ai.

```bash
git fetch origin
git merge origin/main
# mở file bị báo conflict, giữ cả hai khối giữa <<<<<<< và >>>>>>>, xóa các dòng dấu đó
python -m pytest -q
git add <file-vừa-sửa> && git commit
git push
```

Không biết xử lý thì nhắn Phúc, đừng xóa code của người khác.

## Việc thêm nhỏ (tự thống nhất ai làm)
- **Link dùng thử:** chạy UI rồi mở link công khai, ghi vào `starter_v0/artifacts/REPORT.md` mục A1.
  ```bash
  cd starter_v0 && source .venv/bin/activate && streamlit run app.py          # http://localhost:8501
  cloudflared tunnel --url http://localhost:8501                              # cửa sổ khác; brew install cloudflared nếu chưa có
  ```
  Link chỉ sống khi lệnh còn chạy.
- **Chat live:** hỏi UI 3 lượt (một yêu cầu bình thường, một yêu cầu thiếu thông tin rồi bổ sung, một yêu cầu "đăng lên Telegram"). Transcript tự lưu trong `starter_v0/transcripts/`; commit chúng và ghi vào mục B4 của `REPORT.md`.
- **`REPORT.md` mục B6:** dòng "What would you improve next?" do nhóm **tự viết bằng ý của mình**.
- **`TEAM.md`:** mỗi người điền họ tên thật, MSSV và 1 đến 3 dòng "Đóng góp cá nhân" (chỉ ghi việc đã làm thật).

## Lưu ý quan trọng
- **Không đổi tên** `hackernews`, `wikipedia`, `math_solve`, và không sửa case trong `data/eval_base.json` (bài cấm).
- Không sửa `artifacts/system_prompt.md` mà không báo Phúc (file chung, dễ làm hỏng điểm).
- Kẹt hơn 10 phút thì hỏi trong nhóm. Thiếu thời gian thì làm **1 tool cho thật chắc** (đủ 5 thứ) còn hơn 2 tool dở dang.
- Nhánh `test0911` trong repo là nhánh có sẵn từ repo gốc của giảng viên, không phải của nhóm; đừng đụng vào.
