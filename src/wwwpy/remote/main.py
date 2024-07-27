from __future__ import annotations

from inspect import iscoroutinefunction
from typing import Callable, Awaitable, Union

import js
from js import console, window

import wwwpy.common.reloader as reloader
import wwwpy.remote.rpc as rpc
from wwwpy.common import modlib
from wwwpy.common.rpc.serializer import RpcRequest

bro = modlib._find_module_path('remote').parent
root = bro.parent


def _setup_browser_dev_mode():
    def file_changed(event_type: str, filename: str, content: str):
        content_sub = None if content is None else content[:100]
        console.log(f'filename={filename}, content={content_sub}')
        f = root / filename
        do_reload = True
        if event_type == 'deleted':
            console.log(f'deleting {f}')
            f.unlink(missing_ok=True)
        elif not f.exists() or f.read_text() != content:
            console.log(f'writing {f}')
            f.write_text(content)
        else:
            do_reload = False

        if do_reload:
            _reload()

    rpc.file_changed_listeners_add(file_changed)


def _reload():
    async def reload():
        console.log('reloading')
        reloader.unload_path(str(bro))
        await _invoke_browser_main(True)

    _set_timeout(reload)


async def entry_point(dev_mode: bool = False):
    # from wwwpy.common.tree import print_tree
    # print_tree('/wwwpy_bundle')

    await setup_websocket()
    if dev_mode:
        _setup_browser_dev_mode()

    await _invoke_browser_main()


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
        msg = 'module remote load failed. Error: ' + str(e) + '\n\n' + traceback.format_exc() + '\n\n'
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
