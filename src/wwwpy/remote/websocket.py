from __future__ import annotations

from typing import Callable

from wwwpy.common.rpc.serializer import RpcRequest
from wwwpy.remote import set_timeout


async def setup_websocket():
    from js import window, console
    import importlib
    def log(msg):
        console.log(msg)

    def message(msg):
        log(f'message:{msg}')
        r = RpcRequest.from_json(msg)
        m = importlib.import_module(r.module)
        class_name, func_name = r.func.split('.')
        attr = getattr(m, class_name)
        inst = attr()
        func = getattr(inst, func_name)
        func(*r.args)

    l = window.location
    proto = 'ws' if l.protocol == 'http:' else 'wss'
    url = f'{proto}://{l.host}/wwwpy/ws'
    _WebSocketReconnect(url, message)


class _WebSocketReconnect:
    def __init__(self, url: str, on_message: Callable):
        self._url = url
        self._on_message = on_message
        self._counter = 0
        self._connect()

    def _connect(self):
        from js import WebSocket, console
        self._counter += 1
        console.log(f'connecting to {self._url} counter={self._counter}')
        es = WebSocket.new(self._url)
        es.onopen = lambda e: console.log('open')
        es.onmessage = lambda e: self._on_message(e.data)
        es.onerror = lambda e: es.close()
        es.onclose = lambda e: set_timeout(self._connect, 1000)  # for now, we just retry forever and ever
