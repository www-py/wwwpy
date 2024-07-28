from __future__ import annotations

from inspect import iscoroutinefunction
from typing import Callable, Awaitable, Union

import js
from js import console, window

import wwwpy.common.reloader as reloader
from wwwpy.common import _no_remote_infrastructure_found_text
from wwwpy.common.rpc.serializer import RpcRequest
from wwwpy.remote.designer.dev_mode import _setup_browser_dev_mode
from wwwpy.remote.root_path import _get_dir


async def entry_point(dev_mode: bool = False):
    # from wwwpy.common.tree import print_tree
    # print_tree('/wwwpy_bundle')

    await setup_websocket()
    if dev_mode:
        await _setup_browser_dev_mode()

    await _invoke_browser_main()


def _reload():
    async def reload():
        console.log('reloading')
        reloader.unload_path(str(_get_dir().remote))
        await _invoke_browser_main(True)

    _set_timeout(reload)


async def _invoke_browser_main(reload=False):
    console.log('invoke_browser_main')
    try:
        js.document.body.innerHTML = f'Going to import remote (reload={reload})'
        import remote
        if reload:
            import importlib
            importlib.reload(remote)
    except ImportError as e:
        import traceback
        msg = _no_remote_infrastructure_found_text + ' Exception: ' + str(e) + '\n\n' + traceback.format_exc() + '\n\n'
        js.document.body.innerHTML = msg.replace('\n', '<br>')
        return

    if hasattr(remote, 'main'):
        if iscoroutinefunction(remote.main):
            await remote.main()
        else:
            remote.main()


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
        es.onclose = lambda e: _set_timeout(self._connect, 1000)  # for now, we just retry forever and ever


def _set_timeout(callback: Callable[[], Union[None, Awaitable[None]]], timeout_millis: int | None = 0):
    from pyodide.ffi import create_once_callable
    window.setTimeout(create_once_callable(callback), timeout_millis)


