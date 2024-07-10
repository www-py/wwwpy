from __future__ import annotations

from inspect import iscoroutinefunction
from typing import Callable, Awaitable

from wwwpy.common.rpc.serializer import RpcRequest
import js
from js import console, window


def _setup_browser_dev_mode():
    import wwwpy.remote.rpc as rpc
    import wwwpy.common.reloader as reloader

    def listener(filename, content: str):
        console.log(f'filename={filename}, content={content[:100]}')
        bro = reloader._find_package_location('remote').parent
        root = bro.parent
        f = root / filename
        if f.read_text() != content:
            f.write_text(content)
            reloader.unload_path(filename)
            async def reload():
                console.log('reloading')
                await _invoke_browser_main(True)
            _set_timeout(reload)

    rpc.add_listener(listener)


async def entry_point(dev_mode: bool = False):
    from wwwpy.common.tree import print_tree
    print_tree('/wwwpy_bundle')

    await setup_websocket()
    if dev_mode:
        _setup_browser_dev_mode()

    await _invoke_browser_main()


async def _invoke_browser_main(reload=False):
    console.log('invoke_browser_main')
    try:
        js.document.body.innerHTML = 'Going to import remote'
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
    from js import document, WebSocket, window, console
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
    es = WebSocket.new(f'{proto}://{l.host}/wwwpy/ws')
    es.onopen = lambda e: log('open')
    es.onmessage = lambda e: message(e.data)


def _set_timeout(callback: Callable[[], Awaitable[None]], timeout: int | None = 0):
    from pyodide.ffi import create_once_callable
    window.setTimeout(create_once_callable(callback), timeout)