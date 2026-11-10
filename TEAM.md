# TEAM — Day 03: Research Agent Tool Eval

- **Tên nhóm:** Nhomnhom
- **Lớp:** L3A
- **Repo nộp:** https://github.com/phhp04phuc-sys/K5-L3-DAY03-PhanHoangPhuc-2A202603455-ResearchAgentToolEval
- **Nhánh nộp:** `main`
- **Commit chốt:** (điền mã commit cuối của `main` sau khi mọi người push xong)

## Thành viên

| STT | Họ và tên | MSSV | GitHub | Vai trò |
|---|---|---|---|---|
| 1 | Phan Hoàng Phúc | 2A202603455 | [phhp04phuc-sys](https://github.com/phhp04phuc-sys) | Prompt, tool declaration, eval v0–v6, UI, 3 tool mới, báo cáo nhóm |
| 2 | Lưu Đăng Tuấn (xác nhận lại) | (điền MSSV) | [kegacua](https://github.com/kegacua) | `tests/test_tool_tuan.py` (liên quan `papers`, `paper_text`) |
| 3 | Nguyễn Tiến Cường | 2A202603425 | [cuong-sadboi](https://github.com/cuong-sadboi) | Tool `sentiment`, `extract_keywords` và test |
| 4 | Thanh Lập (xác nhận lại họ tên) | 2A202603414 | [lythanhlap](https://github.com/lythanhlap) | Tool `github_search`, `hf_models` và test |
| 5 | Lê Văn Hoàng (xác nhận lại) | 2A202603357 | [hoanglv2k9](https://github.com/hoanglv2k9) | Tool `citation_format`, `url_check` và test |

Họ tên và MSSV của thành viên 2 đến 5 lấy từ tên nhánh và commit; mỗi người kiểm tra lại phần của mình.

## Phân vai

Chỉ ghi việc có commit thật.

| Vai | Phụ trách | Người làm |
|---|---|---|
| Prompt và tool declaration, chạy eval v0 đến v6 | `artifacts/system_prompt.md`, `artifacts/tools.yaml`, `artifacts/version_log.csv`, `runs/` | Phan Hoàng Phúc |
| UI và transcript | `app.py`, `ui_pages.py`, `transcripts/` | Phan Hoàng Phúc |
| Tool mới: `hackernews`, `wikipedia`, `math_solve`, phân tầng nguồn `source_trust.py` | `tools/`, `tests/test_tools_todo.py` | Phan Hoàng Phúc |
| Tool mới: `sentiment`, `extract_keywords` | `tools/`, `tests/test_tools_cuong.py` | Nguyễn Tiến Cường |
| Tool mới: `github_search`, `hf_models` | `tools/`, `tests/test_tools_lap.py` | Thanh Lập |
| Tool mới: `citation_format`, `url_check` | `tools/`, `tests/test_tools_hoang.py` | Lê Văn Hoàng |
| Test cho `papers`, `paper_text` | `tests/test_tool_tuan.py` | Lưu Đăng Tuấn |
| Báo cáo nhóm | `report/team/group_report.md` | Phan Hoàng Phúc |

## Đóng góp cá nhân

Mỗi thành viên tự điền hoặc sửa phần của mình (1 đến 3 dòng, dựa trên commit và log thật). Báo cáo cá nhân đầy đủ nằm ở `report/team/MSSV_HoTen.md`.

- **Phan Hoàng Phúc:** viết lại prompt và tool declaration qua v1–v6, chạy eval và ghi `version_log.csv`; làm UI Streamlit (Chat, Eval, Transcript); thêm 3 tool (`hackernews`, `wikipedia`, `math_solve`) và phân tầng nguồn; điền test cho tool có sẵn; viết báo cáo nhóm.
- **Lưu Đăng Tuấn:** (tự điền)
- **Nguyễn Tiến Cường:** thêm tool `sentiment`, `extract_keywords` kèm 6 test (commit `e4523f6` và PR #1).
- **Thanh Lập:** thêm tool `github_search`, `hf_models` kèm 6 test (commit `42cd73c`, PR #1).
- **Lê Văn Hoàng:** thêm tool `citation_format`, `url_check` kèm 6 test (commit `158ad11`).
