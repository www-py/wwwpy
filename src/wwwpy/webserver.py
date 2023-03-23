from abc import ABC, abstractmethod
from time import sleep
from typing import Tuple

from wwwpy.routes import Routes, HttpRoute
from wwwpy.server import wait_url


class Webserver(ABC):
    def __init__(self):
        self.host: str = '0.0.0.0'
        self.port: int = 7777
        self.routes = Routes()

    def set_host(self, host: str) -> 'Webserver':
        self.host = host
        return self

    def set_port(self, port: int) -> 'Webserver':
        self.port = port
        return self

    def start_listen(self) -> 'Webserver':
        self._start_listen()
        return self

    def set_http_route(self, http_route: HttpRoute) -> 'Webserver':
        self._setup_route(http_route)
        return self

    @abstractmethod
    def _setup_route(self, route: HttpRoute):
        pass

    @abstractmethod
    def _start_listen(self):
        pass

    def wait_ready(self) -> 'Webserver':
        wait_url(self.localhost_url() + '/check_if_webserver_is_accepting_requests')
        return self

    def localhost_url(self) -> str:
        return f'http://127.0.0.1:{self.port}'


def wait_forever() -> None:
    while True:
        sleep(10)
