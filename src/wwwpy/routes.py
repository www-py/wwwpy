from typing import List, Callable, NamedTuple

from .http_request import HttpRequest
from .http_response import HttpResponse


class HttpRoute(NamedTuple):
    path: str
    callback: Callable[[HttpRequest], HttpResponse]


