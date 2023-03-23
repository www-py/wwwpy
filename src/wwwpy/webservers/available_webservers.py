from __future__ import annotations

from typing import Iterator, List

from ..webserver import Webserver


class AvailableWebservers:
    def __init__(self) -> None:
        self.classes = _webservers_classes()
        self.ids = list(map(lambda w: w.__name__, _webservers_classes()))

    def new_instance(self) -> Webserver:
        return self.classes[0]()

    def instances(self) -> Iterator[Webserver]:
        for webserver_class in self.classes:
            yield webserver_class()


def _webservers_classes() -> List[type[Webserver]]:
    result: List[type[Webserver]] = []

    from .python_embedded import WsPythonEmbedded
    result.append(WsPythonEmbedded)

    return result


_available_webservers: AvailableWebservers | None = None


def available_webservers() -> AvailableWebservers:
    global _available_webservers
    if _available_webservers is None:
        av = AvailableWebservers()
        _available_webservers = av
    else:
        av = _available_webservers
    return av
