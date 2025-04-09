from datetime import UTC, datetime
from typing import Annotated, Any, Generic, TypeVar

from fastapi import Query
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    PlainSerializer,
    WrapSerializer,
)

from src.utils.alias_generators import to_camel
from src.utils.datetime import to_naive, to_utc, to_utc_naive


class Model(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )


ModelT = TypeVar("ModelT", bound=Model)


class CamelModel(Model):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        field_title_generator=to_camel,
    )


DBSmallInt = Annotated[int, Field(ge=-32768, le=32767)]
DBInt = Annotated[int, Field(ge=-2147483648, le=2147483647)]
DBBigInt = Annotated[
    int, Field(ge=-9223372036854775808, le=9223372036854775807)
]
DBSmallSerial = Annotated[int, Field(ge=1, le=32767)]
DBIntSerial = Annotated[int, Field(ge=1, le=2147483647)]
DBBigintSerial = Annotated[int, Field(ge=1, le=9223372036854775807)]

ExternalID = DBIntSerial

T = TypeVar("T")


class BaseDBModel(Model, Generic[T]):
    id: T


class DBModel(BaseDBModel[DBBigintSerial]): ...


class External:
    origin_id: ExternalID


# 去除时区信息
NaiveDatetime = Annotated[datetime, PlainSerializer(to_naive)]
# 将时区转成 UTC
UTCDateTime = Annotated[datetime, PlainSerializer(to_utc)]
# 将时间转成 UTC, 并且去除时区信息
UTCNaiveDateTime = Annotated[datetime, PlainSerializer(to_utc_naive)]


def _to_utc(v: datetime):
    if v.tzinfo is None:
        return v.replace(tzinfo=UTC)
    return v.astimezone(UTC)


class _TimeStampModel(Model):
    # class UTCTimeStampModel(Model):
    created_at: Annotated[datetime, PlainSerializer(_to_utc)] = Field(
        description="utc datetime"
    )
    updated_at: Annotated[datetime, PlainSerializer(_to_utc)] | None = Field(
        None, description="utc datetime"
    )


def convert_to_utc(value: Any, handler, info) -> dict[str, datetime]:
    # Note that `helper` can actually help serialize the `value` for
    # further custom serialization in case it's a subclass.
    partial_result = handler(value, info)
    if info.mode == "json":
        return {
            k: to_utc(datetime.fromisoformat(v))
            for k, v in partial_result.items()
        }

    return {k: to_utc(v) for k, v in partial_result.items()}


UTCTimeStampModel = Annotated[_TimeStampModel, WrapSerializer(convert_to_utc)]


class UTCNaiveEventDatetimeParams:
    def __init__(
        self,
        start: datetime | None = Query(None, description="start datetime"),
        end: datetime | None = Query(None, description="end datetime"),
    ) -> None:
        self.start = start and to_utc_naive(start)
        self.end = end and to_utc_naive(end)


class _EventDatetimeModel(Model):
    start: datetime | None = None
    end: datetime = Field(datetime.now())


UTCNaiveEventDatetimeModel = Annotated[
    _EventDatetimeModel, WrapSerializer(convert_to_utc)
]
