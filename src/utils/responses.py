from collections.abc import Sequence
from typing import cast

from src.exceptions import BaseHTTPError, Error, NamedHTTPError
from src.models import CamelModel, Model
from src.utils.utils import deep_merge_dict, on_env


def _get_error_type(value: type[Model]):
    error = value.model_fields.get("error")
    assert error is not None
    return cast(type[Model], error.annotation)


def error_responses(*errors: type[BaseHTTPError | NamedHTTPError]):
    source = {}

    for e in errors:
        if e.STATUS_CODE in source:
            current: type[Error] = source[e.STATUS_CODE]["model"]
            new_value = e.response_scheme()[e.STATUS_CODE]["model"]

            source[e.STATUS_CODE] = {
                "model": Error[_get_error_type(current)]
                | Error[_get_error_type(new_value)]
            }
        else:
            deep_merge_dict(source, e.response_scheme())
    return source


_Response = (
    type[BaseHTTPError]
    | type[NamedHTTPError]
    | tuple[int, type[CamelModel]]
    | int
)


def responses(
    *args: _Response,
    local: Sequence[_Response] | None = None,
    testing: Sequence[_Response] | None = None,
    production: Sequence[_Response] | None = None,
):
    result = {}
    errors = []

    on_env_result = on_env(local=local, testing=testing, production=production)

    for arg in (*args, *on_env_result) if on_env_result else args:
        if type(arg) is tuple:
            result[arg[0]] = {"model": arg[1]}  # type: ignore
        elif type(arg) is int:
            result[arg] = {}
        else:
            errors.append(arg)

    return {**result, **error_responses(*errors)}
