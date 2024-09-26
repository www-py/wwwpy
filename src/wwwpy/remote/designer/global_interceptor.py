from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import js
from js import Event, document, HTMLElement
from pyodide.ffi import create_proxy


@dataclass
class InterceptorEvent:
    target: HTMLElement | None
    event: Event
    interceptor: GlobalInterceptor

    def uninstall(self):
        self.interceptor.uninstall()

    def preventAndStop(self):
        if self.event:
            self.event.preventDefault()
            self.event.stopImmediatePropagation()
            self.event.stopPropagation()


class GlobalInterceptor:

    def __init__(self, callback: Callable[[InterceptorEvent], None], event_name: str = 'click'):
        self._callback = callback
        self._event_name = event_name
        self._installed = False
        self._proxy = create_proxy(self._handler)

    def install(self):
        if self._installed:
            return
        self._installed = True
        js.document.addEventListener(self._event_name, self._proxy, True)

    def uninstall(self):
        if not self._installed:
            return
        self._installed = False
        js.document.removeEventListener(self._event_name, self._proxy, True)

    def _handler(self, event: Event):
        ev = InterceptorEvent(event.target, event, self)
        self._callback(ev)


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
