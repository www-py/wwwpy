from __future__ import annotations

from dataclasses import dataclass
from typing import List, Union

import js
from pyodide.ffi import create_proxy

import wwwpy.remote.component as wpc
from wwwpy.remote import dict_to_js
from wwwpy.remote.designer.global_interceptor import InterceptorEvent, GlobalInterceptor


class Option:
    parent: SearchableComboBox

    def __init__(self, text: str = ''):
        self.text = text
        div: js.HTMLDivElement = js.document.createElement('div')
        div.textContent = self.text
        self._root_element: js.HTMLElement = div
        self._root_element.addEventListener('click', create_proxy(self.click))

    def root_element(self) -> js.HTMLElement:
        return self._root_element

    def click(self, *event):
        self.parent._input.value = self.text
        self.parent.option_popup.hide()


class OptionPopup(wpc.Component, tag_name='wwwpy-searchable-combobox2-option-popup'):
    _options = []  # type: List[Option]
    parent: SearchableComboBox

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

    @property
    def search_placeholder(self) -> str:
        pass

    def show(self):
        self.element.style.display = 'block'

    def hide(self):
        self.element.style.display = 'none'


class SearchableComboBox(wpc.Component, tag_name='wwwpy-searchable-combobox2'):
    _input: js.HTMLInputElement = wpc.element()
    option_popup: OptionPopup = wpc.element()
    """This represents the popoup with the options and eventually a search box at the top to filter the options"""

    def root_element(self):
        return self.shadow

    def init_component(self):
        self.shadow = self.element.attachShadow(dict_to_js({'mode': 'open'}))
        # language=html
        self.shadow.innerHTML = """
        <input data-name="_input">
        <wwwpy-searchable-combobox2-option-popup 
            data-name="option_popup" style='display: none'>
        </wwwpy-searchable-combobox2-option-popup>
        """
        self.option_popup.parent = self

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
        self.option_popup.show()
