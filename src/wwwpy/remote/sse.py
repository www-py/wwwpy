# server-side events - implementation for the remote
from __future__ import annotations

from typing import Callable

from js import document, EventSource

from wwwpy.http_sansio import SansIOHttpProtocol, SansIOHttpResponse, SansIOHttpRoute, SansIOHttpRequest


def harness():
    document.body.innerHTML = ''

    def log(msg):
        document.body.innerHTML += f'|{msg}'

    es = EventSource.new('/sse')
    es.onopen = lambda e: log('open')
    es.onmessage = lambda e: log('message:' + e.data)


class SseClient:
    pass