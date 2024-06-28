# server-side events - implementation for the server
from __future__ import annotations

from typing import Callable

from wwwpy.http_sansio import SansIOHttpProtocol, SansIOHttpResponse, SansIOHttpRoute, SansIOHttpRequest


class SseServer:

    def __init__(self, route: str):
        self.http_route = SansIOHttpRoute(route, self._on_request)

    def _on_request(self, request: SansIOHttpRequest) -> SansIOHttpProtocol:
        return _SseServerProtocol()


class _SseServerProtocol(SansIOHttpProtocol):

    def on_send(self, send: Callable[[SansIOHttpResponse | bytes | None], None]) -> None:
        send(SansIOHttpResponse('text/event-stream'))
        send(b'data: 42\n\n')

    def receive(self, data: bytes | None) -> None:
        super().receive(data)


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
