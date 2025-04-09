from datetime import UTC, datetime


def to_utc(v: datetime):
    if v.tzinfo is None:
        return v.replace(tzinfo=UTC)
    return v.astimezone(UTC)


def to_naive(v: datetime):
    return v.replace(tzinfo=None)


def to_utc_naive(v: datetime):
    return to_naive(to_utc(v))
