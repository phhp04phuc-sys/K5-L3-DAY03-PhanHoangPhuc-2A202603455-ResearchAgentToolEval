# TASKS — Chia việc cho cả nhóm (Day 03, nhóm Nhomnhom)

Repo nhóm: https://github.com/phhp04phuc-sys/K5-L3-DAY03-PhanHoangPhuc-2A202603455-ResearchAgentToolEval
Hạn nộp lên LMS: **23:59 hôm nay**. Commit càng sớm càng tốt để còn thời gian sửa lỗi.

## Hiện trạng (đã xong, đừng làm lại)
- Agent chạy được với Gemini, giao diện `app.py`, prompt/tools đến bản v6, log `runs/`, `REPORT.md`.
- Đã có 3 tool mới: `hackernews`, `wikipedia`, `math_solve`, cộng phân tầng nguồn uy tín (`tools/source_trust.py`).
- `pytest`: 131 qua, 0 skip. Eval nhóm: 19 case, đều qua.
- Slide ghi điểm thưởng khi có **UI và hơn 3 tool mới**. Nhóm đã đủ UI và có 3 tool, nên cần **thêm tool** để vượt 3.

## Việc của mỗi người: làm 1 đến 2 tool mới + các case eval cho tool đó

| Người | Tool mới (gợi ý, không cần key) | Việc thêm |
|---|---|---|
| **kegacua** | `github_repo` (thông tin repo: sao, ngôn ngữ, release mới nhất; API `https://api.github.com/repos/{owner}/{repo}`) và `rss_feed` (đọc tiêu đề từ một RSS/Atom) | |
| **cuong-sadboi** | `currency_convert` (đổi tiền, API `https://open.er-api.com/v6/latest/USD`, có VND) và `unit_convert` (đổi đơn vị, tính cục bộ bằng Python, không cần mạng) | |
| **lythanhlap** | `weather` (thời tiết, 2 bước: `https://geocoding-api.open-meteo.com/v1/search?name=...` rồi `https://api.open-meteo.com/v1/forecast?...&current=temperature_2m`) | Chạy UI, mở link dùng thử (xem mục UI bên dưới), ghi vào `REPORT.md` mục A1 |
| **hoanglv2k9** | `pypi_package` (thông tin một thư viện Python: `https://pypi.org/pypi/{tên}/json`) | Điền `REPORT.md` mục B6 ("What would you improve next?") và chạy thêm 3 lượt chat live trên UI để có transcript |

Mỗi người có thể đổi tool nếu có ý tưởng hay hơn, miễn là: **không trùng người khác**, **không cần API key** (để cả nhóm chạy được), và **chỉ đọc dữ liệu** (không gửi, không xóa, không ghi gì ra ngoài).
Mình đã kiểm tra các địa chỉ API ở bảng trên đều trả về 200 (riêng `restcountries.com` bị chuyển hướng nên bỏ).

## Một tool được tính là xong khi đủ 5 thứ
1. `tools/<tên>/tool.py` và `tools/<tên>/TOOL.md`. Copy khuôn từ `tools/hackernews/` (cùng cách xử lý lỗi và ép tham số).
2. Đăng ký trong `starter_v0/tools/__init__.py` (thêm 1 dòng import và 1 dòng trong `TOOL_FUNCTIONS`).
3. Khai báo trong `starter_v0/artifacts/tools.yaml`: **thêm ở cuối file**, mô tả phải nói rõ **khi nào dùng và khi nào không dùng**, và mô tả từng tham số.
4. **Ít nhất 3 unit test**: đúng, input xấu (chuỗi rỗng, sai kiểu, ngoài khoảng), và nhánh lỗi (HTTP lỗi trả `error` dict, không văng lỗi). Viết ở **cuối** `starter_v0/tests/test_tools_todo.py`, mock mạng bằng fixture `fake_http`. Xem các test của `hackernews` làm mẫu.
5. **Ít nhất 2 case eval** cho tool đó trong `starter_v0/data/eval_group.json` (1 case một lượt, 1 case nhiều lượt), thêm **ở cuối** danh sách `cases`, ID theo mẫu `G20_<tên>`, `GM20_<tên>` (mỗi người dùng đầu số riêng để không trùng: kegacua `G2x`, cuong-sadboi `G3x`, lythanhlap `G4x`, hoanglv2k9 `G5x`).

Kiểm tra trước khi commit:

```bash
cd starter_v0 && source .venv/bin/activate
python -m pytest -q                      # phải không có test lỗi
python run_eval.py --provider gemini --suite group --eval-cases data/eval_group.json --version vX
```

(đổi `vX` thành `v7-<tên bạn>` để không lẫn với bản chung). Case nào lỗi thì đọc `runs/...json` xem agent gọi gì, rồi sửa **mô tả tool** trong `tools.yaml` cho rõ hơn (đừng sửa đáp án để ép cho qua).

## Cách commit để được tính là có đóng góp

Một đóng góp chỉ hiện trên GitHub (trang repo và biểu đồ đóng góp của bạn) khi **email trong commit khớp với tài khoản GitHub của bạn**, và commit nằm trên nhánh `main` (sau khi gộp). Làm đúng các bước sau.

**Bước 0. Một lần duy nhất: đặt đúng tên và email**

Lấy email đã xác minh ở GitHub: Settings → Emails (hoặc dùng địa chỉ dạng `<số>+<username>@users.noreply.github.com` ở cùng trang).

```bash
git config --global user.name "Tên của bạn"
git config --global user.email "email-da-xac-minh@..."
git config user.email          # in ra để kiểm tra
```

**Bước 1. Lấy code mới nhất và tạo nhánh riêng**

```bash
git clone https://github.com/phhp04phuc-sys/K5-L3-DAY03-PhanHoangPhuc-2A202603455-ResearchAgentToolEval.git
cd K5-L3-DAY03-PhanHoangPhuc-2A202603455-ResearchAgentToolEval
git checkout -b <username>/tool-<tên-tool>        # ví dụ: kegacua/tool-github-repo
cd starter_v0 && python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && cp .env.example .env     # tự điền key model của bạn (không cần key cho tool mới)
```

(đã clone từ trước thì chỉ cần `git checkout main && git pull` rồi tạo nhánh.)

**Bước 2. Làm việc, rồi chỉ thêm đúng file của bạn**

```bash
git status
git add starter_v0/tools/<tên-tool> starter_v0/tools/__init__.py starter_v0/artifacts/tools.yaml starter_v0/tests/test_tools_todo.py starter_v0/data/eval_group.json
git status                       # kiểm tra lần cuối: KHÔNG được có file .env
git commit -m "Add <tên-tool> tool with tests and eval cases"
```

Không dùng `git add .` hay `git add -A`. **Tuyệt đối không commit `.env`** (chứa key). Không thêm dòng `Co-Authored-By` vào commit, để lịch sử đóng góp ghi đúng tên bạn.

**Bước 3. Đẩy nhánh và mở Pull Request**

```bash
git push -u origin <username>/tool-<tên-tool>
```

Rồi mở link GitHub in ra (hoặc vào tab Pull requests, bấm **New pull request**), chọn nhánh của bạn vào `main`, đặt tiêu đề rõ ràng, và nhắn Phúc vào nhóm: "PR xong, gộp giúp mình". **Commit chỉ được tính vào đóng góp của repo sau khi gộp vào `main`.** Nếu bạn có quyền Write (đã có), bạn tự bấm **Merge** cũng được sau khi `pytest` xanh.

**Bước 4. Nếu bị xung đột (conflict) ở `tools.yaml`, `__init__.py` hoặc `eval_group.json`**

Đây là 3 file mọi người cùng sửa. Cách xử lý: giữ **cả hai** phần (của bạn và của người khác), không xóa phần của ai.

```bash
git checkout main && git pull
git checkout <nhánh-của-bạn> && git merge main
# mở file bị báo conflict, giữ cả hai khối giữa <<<<<<< và >>>>>>>, xóa các dòng dấu đó
python -m pytest -q
git add <file-vừa-sửa> && git commit
git push
```

Không biết xử lý thì nhắn Phúc, đừng xóa code của người khác.

## Việc thêm cho lythanhlap: UI và link dùng thử

```bash
cd starter_v0 && source .venv/bin/activate
streamlit run app.py                         # chạy ở http://localhost:8501
```

Mở cửa sổ terminal khác để tạo link công khai (cài trước: `brew install cloudflared`):

```bash
cloudflared tunnel --url http://localhost:8501
```

Copy link `https://....trycloudflare.com` vào `starter_v0/artifacts/REPORT.md` mục **A1, dòng URL**. Link chỉ sống khi lệnh còn chạy, nên giữ lệnh chạy trong lúc demo. Nhớ commit và mở PR như hướng dẫn trên.

## Việc thêm cho hoanglv2k9: báo cáo

- Mục **B6** trong `REPORT.md`: dòng "What would you improve next?" bạn tự viết bằng ý của mình (đây là phần nhận định, đừng nhờ AI viết hộ).
- Chạy UI (`streamlit run app.py`) và hỏi 3 lượt: một yêu cầu bình thường, một yêu cầu thiếu thông tin rồi bổ sung, một yêu cầu "đăng lên Telegram" để thấy agent hỏi xác nhận. Transcript tự lưu trong `starter_v0/transcripts/`, commit các file đó và ghi vào mục **B4**.

## Cả nhóm: điền phần của mình trong `TEAM.md`
Họ tên thật, MSSV, và 1 đến 3 dòng "Đóng góp cá nhân" (chỉ ghi việc đã làm thật). Thêm vào cùng PR với tool của bạn.

## Lưu ý quan trọng
- **Không đổi tên** `hackernews`, `wikipedia`, `math_solve`, và không sửa case trong `data/eval_base.json` (bài cấm).
- Case base **R08** lỗi là chủ ý (agent giờ giải được tích phân). Đừng "sửa" nó.
- Không sửa `artifacts/system_prompt.md` mà không báo Phúc (file chung, dễ làm hỏng điểm).
- Hỏi nhau trong nhóm khi bị kẹt hơn 10 phút. Còn thiếu thời gian thì làm **1 tool cho thật chắc** (đủ 5 thứ ở trên) còn hơn 2 tool dở dang.
