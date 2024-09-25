from __future__ import annotations

import js
from pyodide.ffi import create_proxy
import wwwpy.remote.component as wpc
from wwwpy.remote import dict_to_js
from wwwpy.remote.designer.global_interceptor import global_interceptor_start, InterceptorEvent


class SearchableComboBox(wpc.Component, metadata=wpc.Metadata('wwwpy-searchable-combobox')):
    input: js.HTMLInputElement = wpc.element()
    dropdown: js.HTMLElement = wpc.element()

    def root_element(self):
        return self.shadow

    def init_component(self):
        self.shadow = self.element.attachShadow(dict_to_js({'mode': 'open'}))
        # language=html
        self.shadow.innerHTML = """
        <style>
    :host {
        display: inline-block;
        position: relative;
        font-family: Arial, sans-serif;
    }
    input {
        width: 90%;
        padding: 5px;
        background-color: #2a2a2a;
        color: #e0e0e0;
        border: 1px solid #444;
        border-radius: 4px;
        font-size: 14px;
    }
    input::placeholder {
        color: #888;
    }
    .dropdown {
        position: absolute;
        width: 100%;
        max-height: 200px;
        resize: both;
        overflow-y: auto;
        border: 1px solid #444;
        background-color: #333;
        color: #e0e0e0;
        z-index: 1000;
        display: none;
        border-radius: 0 0 4px 4px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .dropdown div {
        padding: 8px 12px;
        cursor: pointer;
        transition: background-color 0.2s ease;
    }
    .dropdown div:hover {
        background-color: #444;
    }
    input:focus {
        outline: none;
        border-color: #666;
        box-shadow: 0 0 0 2px rgba(100, 100, 100, 0.3);
    }
</style>
        <input type="text" placeholder="Search..." data-name="input">
        <div class="dropdown" data-name="dropdown"></div>
        """
        self._interceptor = GlobalInterceptor(self._global_click)
        self.options = []
        self._dirty = False
        self.hide_dropdown()

    def _global_click(self, event: InterceptorEvent):
        click_inside = self.element.contains(event.target)
        console.log(f'global click: contains={click_inside}', event.target)
        if click_inside:
            return
        self.hide_dropdown()

    def input__input(self, event):
        self.filter_options()

    def input__change(self, event):
        if self._is_free_edit():
            self._dispatch_change_event()

    def input__click(self, event):
        self.show_dropdown()

    def show_dropdown(self):
        if self._is_free_edit():
            return
        if self._dirty:
            self.filter_options()
        self.dropdown.style.display = 'block'
        self._interceptor.install()

    def _is_free_edit(self):
        return not self.options

    def hide_dropdown(self):
        self.dropdown.style.display = 'none'
        self._interceptor.uninstall()

    def set_options(self, options):
        self.options = options
        self._dirty = True

    def filter_options(self, event=None):
        self._dirty = False
        filter_text = self.input.value.lower()
        self.dropdown.innerHTML = ''

        for option in self.options:
            if filter_text in option.lower():
                div: js.HTMLDivElement = js.document.createElement('div')
                div.textContent = option
                div.onclick = lambda e, opt=option: self.select_option(opt)
                self.dropdown.appendChild(div)

        # self.dropdown.style.display = 'block' if self.dropdown.hasChildNodes() else 'none'

    def select_option(self, option):
        js.console.log(f'option: {option}')
        self.input.value = option
        self.hide_dropdown()
        self._dispatch_change_event()

    def _dispatch_change_event(self):
        self.element.dispatchEvent(js.CustomEvent.new('change', {'detail': self.input.value}))


from dataclasses import dataclass
from typing import Callable

from js import Event, console, document, HTMLElement
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
        self._proxy = create_proxy(self._global_click)

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

    def _global_click(self, event: Event):
        ev = InterceptorEvent(event.target, event, self)
        self._callback(ev)
