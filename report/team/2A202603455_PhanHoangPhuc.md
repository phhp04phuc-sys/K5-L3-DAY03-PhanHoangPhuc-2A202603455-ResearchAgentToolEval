# Báo cáo cá nhân — Phan Hoàng Phúc (2A202603455)

## 1. Thông tin thành viên

- Họ tên: Phan Hoàng Phúc
- MSSV: 2A202603455
- Email: (tự điền)

## 2. Phần việc phụ trách

Prompt và tool declaration (v0 đến v6), chạy eval và ghi log, UI Streamlit, ba tool mới (`hackernews`, `wikipedia`, `math_solve`), phân tầng nguồn tin (`source_trust.py`), unit test cho tool có sẵn, báo cáo nhóm, gộp các nhánh của nhóm vào `main`.

## 3. Đóng góp cụ thể

- Sửa `artifacts/system_prompt.md` và `artifacts/tools.yaml` theo từng giả thuyết, đo lại bằng `run_eval.py`; điểm base trên Gemini tăng từ 0.55 (v0) lên 1.00 (v3), v5 và v6 còn 0.95 vì case R08 (chi tiết ở `report/team/group_report.md` mục B1).
- Viết 3 tool mới và test (`tools/hackernews/`, `tools/wikipedia/`, `tools/math_solver/`); `math_solve` lọc chặt đầu vào trước khi gọi sympy.
- Thêm `tools/source_trust.py` và tham số `lookup(trusted_only)`.
- Điền toàn bộ stub trong `tests/test_tools_todo.py`; hiện `pytest` báo 179 passed, 0 skipped.
- Làm UI Streamlit với trang Chat, Eval và Transcript.
- Viết 19 case trong `data/eval_group.json`.

## 4. Bằng chứng

- File/commit/PR: lịch sử commit của nhánh `phucphan/core` (tác giả `Phuc`) và các merge vào `main`; `runs/v0_*` đến `runs/v6_*` (Gemini); `artifacts/version_log.csv`.
- AI/công cụ đã dùng và cách tự kiểm tra kết quả: Claude Code hỗ trợ viết code, test và báo cáo. Kết quả được kiểm tra bằng `pytest`, bằng `run_eval.py` (run có `provider_error_cases == 0`) và bằng việc đọc lại run JSON. (Phúc bổ sung hoặc sửa phần này theo cách làm thực tế của mình.)

## 5. Tự đánh giá

(Phúc tự viết.)
