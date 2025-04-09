from typing import TypeVarTuple, overload

from pydantic import alias_generators
from pydantic.fields import ComputedFieldInfo, FieldInfo


Ts = TypeVarTuple("Ts")


@overload
def to_camel(string: str, _: ComputedFieldInfo | FieldInfo) -> str: ...


@overload
def to_camel(string: str) -> str: ...


def to_camel(string: str, *_, **__):
    if string.isupper():
        return string
    return alias_generators.to_camel(string)


@overload
def to_snake(string: str, _: ComputedFieldInfo | FieldInfo) -> str: ...


@overload
def to_snake(string: str) -> str: ...


def to_snake(string: str, *_, **__):
    if string.isupper():
        return string
    return alias_generators.to_snake(string)


@overload
def to_pascal(string: str, _: ComputedFieldInfo | FieldInfo) -> str: ...


@overload
def to_pascal(string: str) -> str: ...


def to_pascal(string: str, *_, **__):
    if string.isupper():
        return string
    return alias_generators.to_pascal(string)
