from __future__ import annotations

from enum import Enum
from typing import NamedTuple, Protocol, List

from wwwpy.common.rpc.serializer import RpcRequest


class WebsocketRoute(NamedTuple):
    path: str
    on_connect: Callable[[WebsocketEndpointIO], None]


class Change(Enum):
    add = 'add'
    remove = 'remove'


class PoolEvent(NamedTuple):
    change: Change
    endpoint: WebsocketEndpoint
    pool: WebsocketPool

    @property
    def add(self) -> bool:
        return self.change == Change.add

    @property
    def remove(self) -> bool:
        return self.change == Change.remove


class PoolChangeCallback(Protocol):
    def __call__(self, change: PoolEvent) -> None: ...


class WebsocketPool:

    def __init__(self, route: str):
        self.clients: list[WebsocketEndpoint] = []
        self.http_route = WebsocketRoute(route, self._on_connect)
        self.on_before_change: List[PoolChangeCallback] = []

    def _notify_change(self, change: PoolEvent) -> None:
        for callback in self.on_before_change:
            callback(change)

    def _on_connect(self, endpoint: WebsocketEndpointIO) -> None:

        self._notify_change(PoolEvent(Change.add, endpoint, self))

        def handle_remove(msg: str | bytes | None):
            if msg is None:
                self._notify_change(PoolEvent(Change.remove, endpoint, self))
                self.clients.remove(endpoint)

        endpoint.listeners.append(handle_remove)
        self.clients.append(endpoint)


class ListenerProtocol(Protocol):
    def __call__(self, message: str | bytes | None) -> None: ...


class SendEndpoint:
    def send(self, message: str | bytes | None) -> None: ...


class DispatchEndpoint(Protocol):
    def dispatch(self, module: str, func_name: str, *args) -> None: ...


from typing import TypeVar, Callable

T = TypeVar('T')


class WebsocketEndpoint(SendEndpoint):
    listeners: list[ListenerProtocol]

    # part to be called by user code to send a outgoing message
    def send(self, message: str | bytes | None) -> None: ...

    def rpc(self, factory: Callable[..., T]) -> T:
        instance = factory(self)
        return instance


class WebsocketEndpointIO(WebsocketEndpoint):
    def __init__(self, send: ListenerProtocol):
        """The send argument is called by the IO implementation: it will deliver outgoing messages"""
        self._send = send
        self.listeners: list[ListenerProtocol] = []

    # part to be called by user code to send a outgoing message
    def send(self, message: str | bytes | None) -> None:
        self._send(message)

    # parte to be used by IO implementation to be called to notify incoming messages
    def on_message(self, message: str | bytes | None) -> None:
        for listener in self.listeners:
            listener(message)

    def dispatch(self, module: str, func_name: str, *args) -> None:
        j = RpcRequest.build_request(module, func_name, *args).json()
        self.send(j)
