# server-side events - implementation for the server
from __future__ import annotations

from typing import Callable, List

from wwwpy.common.typing import Protocol
from wwwpy.http_sansio import SansIOHttpProtocol, SansIOHttpResponse, SansIOHttpRoute, SansIOHttpRequest


class SendEndpoint(Protocol):
    def send(self, message: str) -> None: ...


class SseServer:

    def __init__(self, route: str):
        self.clients: list[SendEndpoint] = []
        self.http_route = SansIOHttpRoute(route, self._on_request)

    def _on_request(self, request: SansIOHttpRequest) -> SansIOHttpProtocol:
        protocol = _SseServerProtocol()
        self.clients.append(protocol)
        return protocol


class _SseServerProtocol(SansIOHttpProtocol, SendEndpoint):
    _send: Callable[[bytes], None]

    def on_send(self, send: Callable[[SansIOHttpResponse | bytes | None], None]) -> None:
        send(SansIOHttpResponse('text/event-stream'))
        self._send = send

    def receive(self, data: bytes | None) -> None:
        super().receive(data)

    def send(self, message: str) -> None:
        self._send(create_event(message).encode())


def create_event(data, event_type=None):
    if data is None or data == "":
        raise ValueError("Data field cannot be empty")

    event_str = ""
    if event_type:
        event_str += f"event: {event_type}\n"
    if data:
        for line in data.splitlines():
            event_str += f"data: {line}\n"
    event_str += "\n"
    return event_str
