from __future__ import annotations

from dataclasses import dataclass
from typing import List, Union

import js
from pyodide.ffi import create_proxy

import wwwpy.remote.component as wpc
from wwwpy.remote import dict_to_js
from wwwpy.remote.designer.global_interceptor import InterceptorEvent, GlobalInterceptor


@dataclass
class Actions:
    set_input_value = True
    hide_dropdown = True
    dispatch_change_event = True


class Option:
    parent: SearchableComboBox

    def __init__(self, text: str = ''):
        self.text = text
        self.actions = Actions()
        self.on_selected = lambda: None
        self._root_element: js.HTMLElement = self.new_element()
        self._root_element.addEventListener('click', create_proxy(self._on_click))

    def root_element(self) -> js.HTMLElement:
        return self._root_element

    def _on_click(self, event: js.MouseEvent):
        js.console.log('_on_click', self.text)
        if self.actions.set_input_value:
            self.set_input_value()
        if self.actions.hide_dropdown:
            self.hide_dropdown()
        if self.actions.dispatch_change_event:
            self.dispatch_change_event()

        self.on_selected()

    def set_input_value(self):
        self.parent._input.value = self.text

    def hide_dropdown(self):
        self.parent.option_popup.hide()

    def dispatch_change_event(self):
        self.parent._dispatch_change_event()

    def new_element(self) -> js.HTMLElement:
        div: js.HTMLDivElement = js.document.createElement('div')
        div.textContent = self.text
        return div


class OptionPopup:
    _options = []  # type: List[Option]

    def __init__(self, parent: SearchableComboBox):
        self.parent = parent

    def root_element(self) -> js.HTMLElement:
        return self.parent._option_popup_ele

    @property
    def options(self) -> List[Option]:
        return self._options

    @options.setter
    def options(self, value: List[Union[str, Option]]):
        self._options = [v if isinstance(v, Option) else Option(v) for v in value]
        root = self.root_element()
        root.innerHTML = ''
        for option in self._options:
            option.parent = self.parent
            root.append(option.root_element())
        # self.option_popup = self.create_option_popup()
        # self.option_popup.activate()

    def activate(self):
        self.parent._option_popup_ele.style.display = 'block'

    def hide(self):
        self.parent._option_popup_ele.style.display = 'none'


class SearchableComboBox(wpc.Component, tag_name='wwwpy-searchable-combobox2'):
    _input: js.HTMLInputElement = wpc.element()
    _option_popup_ele: js.HTMLElement = wpc.element()
    option_popup: OptionPopup
    """This represents the popoup with the options and eventually a search box at the top to filter the options"""

    def root_element(self):
        return self.shadow

    def init_component(self):
        self.shadow = self.element.attachShadow(dict_to_js({'mode': 'open'}))
        # language=html
        self.shadow.innerHTML = """
        <input data-name="_input">
        <div data-name="_option_popup_ele" style='display: none'></div>
        """
        self.option_popup = OptionPopup(self)

    @property
    def text_value(self) -> str:
        return self._input.value

    @text_value.setter
    def text_value(self, value: str):
        self._input.value = value

    @property
    def placeholder(self) -> str:
        return self._input.placeholder

    @placeholder.setter
    def placeholder(self, value: str):
        self._input.placeholder = value

    def _input_element(self) -> js.HTMLElement:
        return self._input

    def _input__click(self, event):
        self.option_popup.activate()
