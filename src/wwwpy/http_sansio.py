from __future__ import annotations

from http import HTTPStatus
from typing import Callable


class SansIOHttpRequest:
    method: str
    """request method, e.g., GET, POST, etc."""

    path: str
    """request path, e.g., /, /index.html, etc."""

    headers: dict[str, str]
    """request headers, e.g., {'Host': 'example.com', 'Content-Length': '1234'}"""

    params: dict[str, str]
    """request query parameters, e.g., /index.html?name=John -> {'name': 'John'}"""

    content_type: str
    """request content type, e.g., application/json, text/html, etc."""


class SansIOHttpResponse:
    """This represents only the status line and headers, the body bytes chunks are sent separately"""

    status_code: HTTPStatus
    """response status code, e.g., 200, 404, etc."""

    headers: dict[str, str]
    """response headers, e.g., {'Content-Type': 'text/html', 'Content-Length': '1234'}"""


class SansIOHttpProtocol:

    def connect(self, request: SansIOHttpRequest) -> None:
        """Called when the http request is received"""

    def on_send_ready(self, send_bytes: Callable[[SansIOHttpResponse | bytes | None], None]) -> None:
        """send_bytes will be called when bytes are ready to be sent to the network.
        The client code is responsible for sending the bytes to the network.
        The send_bytes callback should be called in three phases:
        1. SansIOHttpResponse, to signal the start of the response, this will include the status code and headers
        2. bytes, the protocol can call this as many times as needed
        3. None, when the protocol is terminated, this signals the io implementation to close the connection.
        """

    def receive_bytes(self, data: bytes | None) -> None:
        """This is called when bytes are available for the protocol, usually as a consequence of
        some bytes received from the network.
        When the client code detects the end of the stream, it should call receive_bytes(None)"""


class SansIOHttpRoute:
    path: str
    protocol_factory: Callable[[], SansIOHttpProtocol]
