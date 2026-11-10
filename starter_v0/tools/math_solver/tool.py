from __future__ import annotations

import re
from typing import Any

import sympy as sp
from sympy.parsing.sympy_parser import convert_xor, implicit_multiplication_application, parse_expr, standard_transformations

from tools._shared import err

TASKS = {"evaluate", "simplify", "solve", "derivative", "integral", "factor"}
MAX_LEN = 200

# Chỉ cho phép các hàm và hằng này. sympy phân tích chuỗi bằng eval nên PHẢI lọc trước khi parse.
ALLOWED_NAMES: dict[str, Any] = {
    "sin": sp.sin, "cos": sp.cos, "tan": sp.tan, "asin": sp.asin, "acos": sp.acos, "atan": sp.atan,
    "exp": sp.exp, "log": sp.log, "ln": sp.log, "sqrt": sp.sqrt, "abs": sp.Abs,
    "pi": sp.pi, "e": sp.E,
}
TRANSFORMS = standard_transformations + (convert_xor, implicit_multiplication_application)


class MathInputError(ValueError):
    pass


def _validate(text: str) -> str:
    s = " ".join((text or "").split())
    if not s:
        raise MathInputError("expression is empty")
    if len(s) > MAX_LEN:
        raise MathInputError(f"expression is longer than {MAX_LEN} characters")
    if not re.fullmatch(r"[0-9A-Za-z+\-*/^().,=\s]+", s):
        raise MathInputError("expression has characters that are not allowed")
    for name in re.findall(r"[A-Za-z_]+", s):
        if name in ALLOWED_NAMES or len(name) == 1:
            continue
        raise MathInputError(f"unknown name '{name}': only single-letter variables and basic functions are allowed")
    if re.search(r"\d{13,}", s):
        raise MathInputError("number is too long")
    # Chặn lũy thừa khổng lồ (ví dụ 9^9^9) có thể treo máy
    if re.search(r"[\^]\s*\(?\s*\d{4,}", s) or len(re.findall(r"\^|\*\*", s)) > 6 or re.search(r"\^[^,)=+\-]*\^", s):
        raise MathInputError("exponent is too large or nested")
    return s


def _parse(s: str) -> sp.Expr:
    # global_dict chỉ có các lớp mà bộ biến đổi của sympy tự sinh ra (Integer, Symbol...). Người dùng không gõ
    # được tên nhiều chữ cái ngoài ALLOWED_NAMES nên không gọi được chúng trực tiếp.
    safe_globals = {"Integer": sp.Integer, "Float": sp.Float, "Rational": sp.Rational, "Symbol": sp.Symbol}
    return parse_expr(s, local_dict=dict(ALLOWED_NAMES), global_dict=safe_globals, transformations=TRANSFORMS, evaluate=True)


def _fmt(value: Any) -> str:
    return sp.sstr(value).replace("**", "^")


def solve_math(expression: str = "", task: str = "evaluate", variable: str = "x") -> dict[str, Any]:
    """Giải toán bằng sympy: tính, rút gọn, phân tích, giải phương trình, đạo hàm, tích phân."""
    try:
        kind = (task or "evaluate").strip().lower()
        if kind not in TASKS:
            kind = "evaluate"
        var_name = (variable or "x").strip()
        if not re.fullmatch(r"[A-Za-z]", var_name):
            var_name = "x"
        var = sp.Symbol(var_name)
        s = _validate(expression)

        if "=" in s:
            if s.count("=") != 1 or kind not in {"solve", "evaluate"}:
                raise MathInputError("only one '=' is allowed, and only for solving an equation")
            left, right = s.split("=")
            if not left.strip() or not right.strip():
                raise MathInputError("equation needs both sides")
            kind = "solve"
            expr: sp.Expr = _parse(left) - _parse(right)
        else:
            expr = _parse(s)

        note = ""
        if kind == "evaluate":
            exact = sp.simplify(expr)
            numeric = None
            if not exact.free_symbols:
                numeric = float(sp.N(exact)) if exact.is_real else None
            result: Any = _fmt(exact)
            out: dict[str, Any] = {"result": result}
            if numeric is not None and _fmt(exact) != repr(numeric):
                out["numeric"] = round(numeric, 10)
        elif kind == "simplify":
            out = {"result": _fmt(sp.simplify(expr))}
        elif kind == "factor":
            out = {"result": _fmt(sp.factor(expr))}
        elif kind == "solve":
            symbols = sorted(expr.free_symbols, key=lambda x: x.name)
            target = var if var in expr.free_symbols else (symbols[0] if symbols else var)
            solutions = sp.solve(expr, target)
            out = {"variable": target.name, "solutions": [_fmt(item) for item in solutions]}
        elif kind == "derivative":
            out = {"variable": var_name, "result": _fmt(sp.diff(expr, var))}
        else:  # integral
            out = {"variable": var_name, "result": _fmt(sp.integrate(expr, var))}
            note = "Nguyên hàm (tích phân bất định): cộng thêm hằng số C"
            out["note"] = note
        if "zoo" in str(out.get("result", "")) or "nan" in str(out.get("result", "")):
            raise MathInputError("result is undefined (division by zero or indeterminate form)")
        return {"tool": "solve_math", "task": kind, "input": s, **out}
    except MathInputError as exc:
        return {"tool": "solve_math", "error": "InvalidExpression", "message": str(exc)}
    except (sp.SympifyError, SyntaxError, TypeError, ValueError, ZeroDivisionError, NotImplementedError) as exc:
        return {"tool": "solve_math", "error": "InvalidExpression", "message": f"Cannot compute: {type(exc).__name__}"}
    except Exception as exc:
        return err("solve_math", exc)
