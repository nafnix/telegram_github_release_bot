from typing import Annotated, Any, Literal, TypeVar, TypedDict

from fastapi import Depends
from pydantic.main import IncEx


# see pydantic.BaseModel.model_dump
# https://docs.pydantic.dev/2.9/concepts/serialization/#modelmodel_dump
class ModelDumpKwargs(TypedDict):
    mode: Literal["json", "python"]
    include: IncEx | None
    exclude: IncEx | None
    context: Any | None
    by_alias: bool
    exclude_unset: bool
    exclude_defaults: bool
    exclude_none: bool
    round_trip: bool
    warnings: bool | Literal["none", "warn", "error"]
    serialize_as_any: bool


T = TypeVar("T")
Dep = Annotated[T, Depends()]
