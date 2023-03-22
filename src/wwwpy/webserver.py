from abc import ABC, abstractmethod
from time import sleep
from typing import Tuple

from wwwpy.routes import Routes, Route
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

    def set_binding(self, binding: Tuple[str, int]) -> 'Webserver':
        self.set_host(binding[0])
        self.set_port(binding[1])
        return self

    def set_routes(self, routes: Routes) -> 'Webserver':
        if routes is None:
            raise Exception(f'Parameter routes cannot be None')
        self.routes = routes

        for route in self.routes.list:
            self._setup_route(route)

        return self

    def start_listen(self) -> 'Webserver':
        self._start_listen()
        return self

    # todo inline Route type
    @abstractmethod
    def _setup_route(self, route: Route):
        pass

    @abstractmethod
    def _start_listen(self):
        pass

    def wait_ready(self) -> 'Webserver':
        wait_url(self.localhost_url() + '/check_if_webserver_is_accepting_requests')
        return self

    def localhost_url(self) -> str:
        return f'http://127.0.0.1:{self.port}'


def wait_forever():
    while True:
        sleep(10)
