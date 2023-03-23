from typing import List, Callable, NamedTuple

from .response import HttpRequest, HttpResponse


class HttpRoute(NamedTuple):
    path: str
    callback: Callable[[HttpRequest], HttpResponse]


class Routes:
    def __init__(self):
        self.list: List[HttpRoute] = []

    def add_route(self, path: str, callback: Callable[[HttpRequest], HttpResponse]) -> 'Routes':
        self.list.append(HttpRoute(path, callback))
        return self

    def add_route_obj(self, route: HttpRoute) -> 'Routes':
        self.list.append(route)
        return self

    @property
    def is_empty(self) -> bool:
        return len(self.list) == 0
