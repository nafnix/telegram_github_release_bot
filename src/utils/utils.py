from collections.abc import Mapping
from typing import TypeVar

from src.config import settings
from src.constants import Environment


def deep_merge_dict(
    target: dict,
    source: Mapping,
    exclude_keys: list[str] | None = None,
):
    """深层合并两个字典

    :param target: 存放合并内容的字典
    :param source: 来源, 因为不会修改, 所以只读映射就可以
    :param exclude_keys: 需要排除的 keys
    """

    for ok, ov in source.items():
        if exclude_keys is not None and ok in exclude_keys:
            continue

        v = target.get(ok)
        # 如果两边都是映射类型, 就可以合并
        if isinstance(v, dict) and isinstance(ov, Mapping):
            deep_merge_dict(v, ov, exclude_keys)
        # 如果当前值允许进行相加的操作
        # 并且不是字符串和数字
        # 并且旧字典与当前值类型相同
        elif (
            hasattr(v, "__add__")
            and not isinstance(v, str | int)
            and type(v) is type(ov)
        ):
            target[ok] = v + ov
        # 否则使用有效的值
        else:
            target[ok] = v or ov


T = TypeVar("T")


def on_env(
    *,
    local: T | None = None,
    testing: T | None = None,
    production: T | None = None,
) -> T | None:
    result: T | None = None
    if settings.ENVIRONMENT == Environment.LOCAL:
        result = local
    elif settings.ENVIRONMENT == Environment.TESTING:
        result = testing
    else:
        result = production

    return result


def path(*subpath) -> str:
    return "/" + "/".join(
        f"{i}".removeprefix("/").removesuffix("/") for i in subpath
    )
