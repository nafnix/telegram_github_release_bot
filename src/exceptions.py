from typing import ClassVar, Generic, Literal, TypeVar

from fastapi import Response
from fastapi.responses import JSONResponse
from fastapi.utils import is_body_allowed_for_status_code
from pydantic import BaseModel, create_model
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from src.models import CamelModel
from src.utils.alias_generators import to_camel


BaseModelT = TypeVar('BaseModelT', bound=BaseModel)
ErrorCodeT = TypeVar('ErrorCodeT', bound=str)
TargetT = TypeVar('TargetT', bound=str)


class BaseHTTPErrorModel(CamelModel, Generic[ErrorCodeT]):
    code: ErrorCodeT
    message: str


BaseErrorModelT = TypeVar('BaseErrorModelT', bound=BaseHTTPErrorModel)


class Error(CamelModel, Generic[BaseModelT]):
    error: BaseModelT


class BaseHTTPError(
    Exception,
    Generic[ErrorCodeT, BaseErrorModelT],
):
    model_class: type[BaseErrorModelT]
    STATUS_CODE: int

    def __init__(
        self,
        *,
        code: ErrorCodeT,
        message: str,
        headers: dict[str, str] | None = None,
    ) -> None:
        model = self.model_class(code=code, message=message)
        self.code = code
        self.data = Error(error=model)
        self.headers = headers

    def __str__(self) -> str:
        return f'{self.STATUS_CODE}: {self.data.error.code}'

    def __repr__(self) -> str:
        return f'{self.model_class: str(self.error)}'

    @classmethod
    def response_scheme(cls):
        return {cls.STATUS_CODE: {'model': Error[cls.model_class]}}


# >>>>>>>>>>>>>>>>>>>>>>>
# Default


class ErrorModel(BaseHTTPErrorModel, Generic[ErrorCodeT]): ...


class HTTPError(BaseHTTPError[ErrorCodeT, ErrorModel], Generic[ErrorCodeT]):
    model_class = ErrorModel
    STATUS_CODE = HTTP_500_INTERNAL_SERVER_ERROR


# Default
# <<<<<<<<<<<<<<<<<<<<<<<


# >>>>>>>>>>>>>>>>>>>>>>>
# Bad Request


class BaseBadRequestErrorModel(
    BaseHTTPErrorModel[ErrorCodeT],
    Generic[ErrorCodeT, TargetT],
):
    target: TargetT | None = None


class BaseBadRequestError(
    BaseHTTPError[ErrorCodeT, BaseBadRequestErrorModel[ErrorCodeT, TargetT]],
    Generic[ErrorCodeT, TargetT],
):
    model_class = BaseBadRequestErrorModel  # type: ignore

    STATUS_CODE = HTTP_400_BAD_REQUEST

    def __init__(
        self,
        *,
        code: ErrorCodeT,
        message: str,
        target: TargetT | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        model = self.model_class(
            code=code,
            message=message,
            target=target,
        )
        self.data = Error(error=model)
        self.headers = headers


# Bad Request
# <<<<<<<<<<<<<<<<<<<<<<<


class ForbiddenErrorModel(ErrorModel[Literal['forbidden']]): ...


class ForbiddenError(HTTPError[Literal['forbidden']]):
    model_class = ForbiddenErrorModel
    STATUS_CODE = HTTP_403_FORBIDDEN

    def __init__(
        self,
        *,
        message: str = (
            'You do not have permission to access or '
            'perform actions on this resource'
        ),
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(
            code='forbidden',
            message=message,
            headers=headers,
        )


class NamedHTTPError(Exception):
    STATUS_CODE: int = HTTP_400_BAD_REQUEST
    ERROR_CODE: str | None = None
    targets: ClassVar[tuple[str, ...] | None] = None

    @classmethod
    def name(cls):
        return cls.__name__.removesuffix('Error')

    @classmethod
    def model_class(cls):
        type_ = cls.name()
        error_code = cls.ERROR_CODE or type_
        kwargs = {}
        if cls.targets:
            kwargs['target'] = (Literal[*cls.targets_()], ...)
        kwargs['message'] = (str, ...)
        return create_model(
            f'{type_}Model',
            code=(Literal[error_code], ...),
            **kwargs,
        )

    @classmethod
    def code(cls):
        return cls.ERROR_CODE or cls.name()

    @classmethod
    def targets_(cls) -> list[str]:
        if cls.targets:
            return [to_camel(i) for i in cls.targets]
        return []

    def __init__(
        self,
        *,
        message: str,
        target: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        kwargs = {
            'code': self.code(),
            'message': message,
        }

        if target is not None:
            target = to_camel(target)
            kwargs['target'] = target
            kwargs['message'] = kwargs['message'].format(target=target)

        model = self.model_class()(**kwargs)
        self.data = Error(error=model)
        self.headers = headers

    def __str__(self) -> str:
        return f'{self.STATUS_CODE}: {self.data.error.code}'  # type: ignore

    def __repr__(self) -> str:
        return f'{self.model_class: str(self.error)}'

    @classmethod
    def response_scheme(cls):
        return {cls.STATUS_CODE: {'model': Error[cls.model_class()]}}


class ConflictError(NamedHTTPError):
    STATUS_CODE = HTTP_409_CONFLICT

    def __init__(
        self,
        *,
        target: str,
        message: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        message = message or '{target} is already in use'

        super().__init__(target=target, message=message, headers=headers)


class NotFoundError(NamedHTTPError):
    STATUS_CODE = HTTP_404_NOT_FOUND

    def __init__(
        self,
        *,
        target: str,
        message: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        message = message or '{target} not found'

        super().__init__(target=target, message=message, headers=headers)


def http_error_handler(_, exc: BaseHTTPError | NamedHTTPError):
    headers = getattr(exc, 'headers', None)
    if not is_body_allowed_for_status_code(exc.STATUS_CODE):
        return Response(status_code=exc.STATUS_CODE, headers=headers)

    return JSONResponse(
        exc.data.model_dump(exclude_none=True),
        status_code=exc.STATUS_CODE,
        headers=headers,
    )
