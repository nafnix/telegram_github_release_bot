import re
from typing import TypeVar, TypeVarTuple


T = TypeVar("T")
Ts = TypeVarTuple("Ts")

_token_specification = {
    "ATTRIBUTE": r"(?<=\.)[a-zA-Z_]+\w*",  # 属性
    "INDEX": r"(?<=\[)\d+(?=\])",  # 索引
    "VALUE": r"[a-zA-Z_]+\w*",  # 值
}
_nested_attr_pattern = re.compile(
    "|".join(f"(?P<{i}>{j})" for i, j in _token_specification.items())
)


def get_nested_value(obj, nested_value: str):
    """获取嵌套属性的值

    Example:
        >>> data = {"a": {"b": {"c": 42}}}
        >>> get_nested_value(data, "a.b.c")
        42

        >>> data = [{"a": 1}, {"b": 2}]
        >>> get_nested_value(data, "[1].b")
        2
    """
    current = obj
    for mo in _nested_attr_pattern.finditer(nested_value):
        kind = mo.lastgroup
        value = mo.group()

        if kind in ["ATTRIBUTE", "VALUE"]:
            if isinstance(current, dict):
                current = current.get(value)
            else:
                current = getattr(current, value, None)
        elif kind == "INDEX" and isinstance(current, (list, tuple)):
            current = current[int(value)]

        if current is None:
            return current

    return current
