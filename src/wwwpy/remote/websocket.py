from __future__ import annotations

from typing import Callable

from wwwpy.common.rpc.serializer import RpcRequest
import asyncio

import logging

logger = logging.getLogger(__name__)


async def setup_websocket():
    from js import window, console
    import importlib
    def log(msg):
        console.log(msg)

    def message(msg):
        log(f'message:{msg}')
        r = RpcRequest.from_json(msg)
        # _debug_requested_module(r.module)
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

        async def reconnect():
            await asyncio.sleep(1)
            self._connect()

        es.onclose = lambda e: asyncio.create_task(reconnect())  # for now, we just retry forever and ever


def _debug_requested_module(module_name: str):
    from wwwpy.common import modlib
    mp = modlib._find_module_path(module_name)
    logger.debug(f'requested module: {module_name} path: {mp}')
    if mp:
        logger.debug(f'content: ```{mp.read_text()}```')
