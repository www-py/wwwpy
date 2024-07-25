from typing import Callable

from js import Event, console, document
from pyodide.ffi import create_proxy


def start(callback: Callable[[bool], None]):
    proxy = []

    def global_click(event: Event):
        event.preventDefault()
        event.stopImmediatePropagation()
        event.stopPropagation()

        if len(proxy) > 0:
            document.removeEventListener('click', proxy[0], True)
            proxy.clear()
            callback(True)

    proxy.append(create_proxy(global_click))
    document.addEventListener('click', proxy[0], True)
