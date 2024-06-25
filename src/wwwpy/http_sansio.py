from __future__ import annotations

from http import HTTPStatus
from typing import Callable, NamedTuple


class SansIOHttpRequest(NamedTuple):
    """This represents only the status line and headers, the body bytes chunks are sent separately"""

    method: str
    """request method, e.g., GET, POST, etc."""

    # path: str
    # """request path, e.g., /, /index.html, etc."""

    # headers: dict[str, str]
    # """request headers, e.g., {'Host': 'example.com', 'Content-Length': '1234'}"""

    # params: dict[str, str]
    # """request query parameters, e.g., /index.html?name=John -> {'name': 'John'}"""

    content_type: str
    """request content type, e.g., application/json, text/html, etc."""


class SansIOHttpResponse(NamedTuple):
    """This represents only the status line and headers, the body bytes chunks are sent separately"""

    # status_code: HTTPStatus
    # """response status code, e.g., 200, 404, etc."""

    content_type: str
    """request content type, e.g., application/json, text/html, etc."""

    # headers: dict[str, str]
    # """response headers, e.g., {'Content-Length': '1234'}"""


class SansIOHttpProtocol:
    """The IO implementation:
     - use this interface to communicate with the protocol implementation
     - calls the on_send() method once (!) in order to be notified by the protocol implementation.
     - calls the receive() method as many times as needed in order to process the bytes received from the network.
    """

    def on_send(self, send: Callable[[SansIOHttpResponse | bytes | None], None]) -> None:
        """send_bytes will be called when bytes are ready to be sent to the network.
        The client code is responsible for sending the bytes to the network.
        The send() callback should be called in three phases:
        1. SansIOHttpResponse, to signal the start of the response, this can be called only once.
        2. bytes, the protocol can call this as many times as needed.
        3. None, when the protocol is terminated, this signals the IO implementation to close the connection.
        """

    def receive(self, data: bytes | None) -> None:
        """This is called when bytes are available for the protocol, usually as a consequence of
        some bytes received from the network.
        When the IO implementation detects the end of the stream, it should call receive(None) so the protocol implementation is aware of it.
        """


class SansIOHttpRoute(NamedTuple):
    path: str
    protocol_factory: Callable[[SansIOHttpRequest], SansIOHttpProtocol]

# todo next: layer1 implement in python_embedded.py the above
# todo next: layer5 implement sse

# https://rxdb.info/articles/websockets-sse-polling-webrtc-webtransport.html
# https://github.com/Azure/fetch-event-source
