from enum import StrEnum, auto
from functools import wraps
import inspect
from typing_extensions import ParamSpec
from typing import (
    Annotated,
    Any,
    Coroutine,
    Callable,
    Generic,
    Literal,
    TypeVar,
    get_origin,
    get_args,
    TypeVar,
    Union,
    Concatenate,
    overload,
    Protocol,
    Type,
)
from inspect import _ParameterKind, signature
from starlette.applications import Starlette
from starlette.authentication import AuthCredentials, AuthenticationBackend, requires
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware

from starlette.routing import Route
import starlette.requests
import starlette.types

import starlette.types

from typing import Generic, TypeVar, overload, Any, Literal

P = ParamSpec("P")
T = TypeVar("T")

class AuthScope(StrEnum):
    Authenticated = auto()
    Admin = auto()

class App(Starlette):
    def url_wrapper(
        self, func: Callable[Concatenate[Any, P], Any]
    ) -> Callable[P, str]: ...
    def get(self, endpoint: str, auth_scopes: list[AuthScope] = []): ...
    def path_function(
        self, method: str, endpoint: str, auth_scopes: list[AuthScope] = []
    ): ...

class Scope(starlette.types.Scope):
    @overload
    def __getitem__(self, key: Literal["from_htmx"]) -> bool: ...
    @overload
    def __getitem__(self, key: str) -> Any: ...

class Request(Generic[T]):
    scope: Scope
    user: T

def init_app(
    auth_func: Callable[
        [starlette.requests.HTTPConnection],
        Coroutine[Any, Any, tuple[AuthCredentials, T] | None],
    ]
) -> tuple[App, Type[Request[T]]]: ...
