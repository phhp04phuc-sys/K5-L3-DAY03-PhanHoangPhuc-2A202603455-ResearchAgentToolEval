---
name: math_solve
track: bonus
kind: local_compute
provider: sympy (chạy cục bộ)
requires_env: []
inputs: [expression, task, variable]
outputs: [result, solutions, numeric, note]
side_effect: false
---
# math_solve

Giải toán bằng thư viện `sympy`, chạy cục bộ, không cần key.

`task`:
- `evaluate`: tính giá trị một biểu thức (có thêm `numeric` nếu là số thực).
- `simplify`: rút gọn. `factor`: phân tích thành nhân tử.
- `solve`: giải phương trình (có `=`) hoặc tìm nghiệm của biểu thức bằng 0; trả về danh sách `solutions`.
- `derivative`: đạo hàm theo `variable`. `integral`: nguyên hàm theo `variable` (nhớ cộng hằng số C).

Viết biểu thức bằng ký hiệu thường: `x^2`, `2x+6=0`, `sqrt(16)`, `sin(x)`, `pi`.

Bảo mật: `sympy` phân tích chuỗi bằng `eval`, nên đầu vào bị lọc chặt trước khi parse: chỉ nhận ký tự toán học,
biến một chữ cái và các hàm sin, cos, tan, asin, acos, atan, exp, log, ln, sqrt, abs; chặn tên lạ (ví dụ `__import__`),
chuỗi quá dài và lũy thừa khổng lồ hoặc lồng nhau (ví dụ `9^9^9`).

Dùng khi người dùng yêu cầu tính toán hoặc giải toán. Không dùng cho viết code hay bài toán chữ phải tự lập luận.
