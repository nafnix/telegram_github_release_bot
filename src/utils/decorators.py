import asyncio
import inspect
from collections.abc import Callable
from functools import wraps
from typing import Any

from fastapi import Depends


# 暂时用不上了
def add_dependencies(**kwargs: tuple[str, Any] | Any):
    def decorate(fn):
        sign = inspect.signature(fn)
        parameters = list(sign.parameters.values())
        for dependency_name, value in kwargs.items():
            dependency = None

            if isinstance(value, tuple):
                description, dependency = value
                fn.__doc__ = f"{description}\n\n{fn.__doc__ or ''}"
            else:
                dependency = value

            if dependency is not None:
                parameter = sign.parameters.get(
                    dependency_name,
                    inspect.Parameter(
                        dependency_name,
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    ),
                ).replace(default=Depends(dependency))

                parameters = [
                    i for i in parameters if i.name != dependency_name
                ] + [parameter]

        new_sign = sign.replace(parameters=parameters)
        fn.__signature__ = new_sign  # type: ignore

        @wraps(fn)
        async def wrapper(*args, **kwargs):
            return await fn(*args, **kwargs)

        return wrapper

    return decorate


def rename_kwargs(**kwargs: str):
    def decorate(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs_):
            for old_name, new_name in kwargs.items():
                if old_name in kwargs_:
                    kwargs_.setdefault(new_name, kwargs_.pop(old_name))
            return fn(*args, **kwargs_)

        return wrapper

    return decorate


class MarkRouteStatus:
    @staticmethod
    def __mark(fn: Callable, description: str, name: str):
        fn.__doc__ = f"{description}\n\n{fn.__doc__ or ''}"
        fn.__name__ = f"{name}_{fn.__name__}"
        return fn

    @classmethod
    def work_in_progress(cls, fn: Callable):
        return cls.__mark(fn, "**🧑‍🏭: Work in progress...**", "🚧")

    @classmethod
    def bug_fix(cls, fn: Callable):
        return cls.__mark(fn, "**🧑‍⚕️: Fixing Bugs...**", "🏥")


def sync(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        return asyncio.get_event_loop().run_until_complete(fn(*args, **kwargs))

    return wrapper
