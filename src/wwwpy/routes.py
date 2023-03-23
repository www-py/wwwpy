from typing import List, Callable, NamedTuple

from .response import HttpRequest, HttpResponse


class HttpRoute(NamedTuple):
    path: str
    callback: Callable[[HttpRequest], HttpResponse]


