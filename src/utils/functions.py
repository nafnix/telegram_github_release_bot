import asyncio
import inspect
from typing import Callable, ParamSpec, TypeVar

from src.config import settings

from .alias_generators import to_snake


FnT = TypeVar("FnT", bound=Callable)
T = TypeVar("T")
P = ParamSpec("P")


def update_signature(fn: Callable, signature: inspect.Signature):
    fn.__signature__ = signature  # type: ignore


def name(fn: Callable) -> str:
    return fn.__name__


def wrap_fn(wrapper) -> Callable[[FnT], FnT]:
    def decorator(fn: FnT) -> FnT:
        return wrapper(fn)

    return decorator


def add_document(fn: Callable, document: str):
    if fn.__doc__ is None:
        fn.__doc__ = document
    else:
        fn.__doc__ += f"\n\n{document}"


def get_parameters(fn: Callable) -> list[inspect.Parameter]:
    signature = inspect.signature(fn)
    return list(signature.parameters.values())


async def execute(fn: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
    if asyncio.iscoroutinefunction(fn):
        return await fn(*args, **kwargs)

    result = fn(*args, **kwargs)

    if inspect.isawaitable(result):
        return await result

    return result


def key(*args, separator: str = ":", **kwargs):
    items = [to_snake(settings.PROJECT_NAME)]
    items.extend(str(i) for i in args)
    items.extend(f"{k}{separator}{v!s}" for k, v in kwargs.items())

    return separator.join(items)
