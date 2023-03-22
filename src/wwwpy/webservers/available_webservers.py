from typing import Iterator

from ..webserver import Webserver


class AvailableWebservers:
    def __init__(self):
        self.classes = _webservers_classes()
        self.ids = list(map(lambda w: w.__name__, _webservers_classes()))

    def new_instance(self) -> Webserver:
        return self.classes[0]()

    def instances(self) -> Iterator[Webserver]:
        for webserver_class in self.classes:
            yield webserver_class()


def _webservers_classes():
    result = []
    try:
        from .fastapi import WsFastapi
        result.append(WsFastapi)
    except:
        pass
    try:
        from .webservers.flask import WsFlask
        result.append(WsFlask)
    except:
        pass
    try:
        from .webservers.tornado import WsTornado
        result.append(WsTornado)
    except:
        pass

    from .python_embedded import WsPythonEmbedded
    result.append(WsPythonEmbedded)

    return result


_available_webservers = None


def available_webservers() -> AvailableWebservers:
    global _available_webservers
    if _available_webservers is None:
        _available_webservers = AvailableWebservers()
    return _available_webservers
