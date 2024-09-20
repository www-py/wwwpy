from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from js import Event, console, document, HTMLElement
from pyodide.ffi import create_proxy


@dataclass
class InterceptorEvent:
    target: HTMLElement | None
    event: Event
    _uninstall: callable

    def uninstall(self):
        self._uninstall()

    def preventAndStop(self):
        if self.event:
            self.event.preventDefault()
            self.event.stopImmediatePropagation()
            self.event.stopPropagation()


def global_interceptor_start(callback: Callable[[InterceptorEvent], None]):
    proxy = []

    def _uninstall():
        document.removeEventListener('click', proxy[0], True)
        proxy.clear()

    def global_click(event: Event):
        ev = InterceptorEvent(event.target, event, _uninstall)
        callback(ev)

    proxy.append(create_proxy(global_click))
    document.addEventListener('click', proxy[0], True)
