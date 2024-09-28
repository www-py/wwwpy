from __future__ import annotations

from dataclasses import dataclass
from typing import List, Union

import js
from js import console
from pyodide.ffi import create_proxy

import wwwpy.remote.component as wpc
from wwwpy.remote import dict_to_js
from wwwpy.remote.designer.global_interceptor import InterceptorEvent, GlobalInterceptor


@dataclass
class Actions:
    set_input_value = True
    # hide_dropdown = True
    # dispatch_change_event = True


class Option:
    parent: SearchableComboBox

    def __init__(self, text: str = ''):
        self.text = text
        self.actions = Actions()
        self.on_selected = lambda: None
        div: js.HTMLDivElement = js.document.createElement('div')
        div.textContent = self.text
        self._root_element: js.HTMLElement = div
        self._root_element.addEventListener('click', create_proxy(self.do_click))

    def root_element(self) -> js.HTMLElement:
        return self._root_element

    def do_click(self, *event):
        if self.actions.set_input_value:
            self.parent._input.value = self.text
        self.parent.option_popup.hide()
        self.on_selected()

    def update_visibility(self, search: str):
        self.visible = search.lower() in self.text.lower()

    @property
    def visible(self) -> bool:
        return not (self._root_element.style.display == 'none')

    @visible.setter
    def visible(self, value):
        self._root_element.style.display = 'block' if value else 'none'


class OptionPopup(wpc.Component, tag_name='wwwpy-searchable-combobox2-option-popup'):
    _options = []  # type: List[Option]
    parent: SearchableComboBox
    _root: js.HTMLElement = wpc.element()
    _search: js.HTMLInputElement = wpc.element()

    def init_component(self):
        # language=html
        self.element.innerHTML = """
        <div><input type="search" data-name="_search"></div>
        <div data-name="_root"></div>
        """
        self._interceptor = GlobalInterceptor(self._global_click)

    def _global_click(self, event: InterceptorEvent):
        target = event.event.composedPath()[0]
        click_inside = self.parent.root_element().contains(target)
        js.console.log(f'global click: contains={click_inside}', target)
        if click_inside:
            return
        self.hide()

    @property
    def visible(self) -> bool:
        return self.element.style.display != 'none'

    @property
    def options(self) -> List[Option]:
        return self._options

    @options.setter
    def options(self, value: List[Union[str, Option]]):
        self._options = [v if isinstance(v, Option) else Option(v) for v in value]
        root = self._root
        root.innerHTML = ''
        for option in self._options:
            option.parent = self.parent
            root.append(option.root_element())

    @property
    def search_placeholder(self) -> str:
        return self._search.placeholder

    @search_placeholder.setter
    def search_placeholder(self, value):
        self._search.placeholder = value

    @property
    def search_value(self):
        return self._search.value

    @search_value.setter
    def search_value(self, value: str):
        self._search.value = value
        self._update_options_vis()

    def _search__input(self, event):
        self._update_options_vis()

    def _update_options_vis(self):
        for option in self._options:
            option.update_visibility(self._search.value)

    def show(self):
        self.element.style.display = 'block'
        self._interceptor.install()

    def hide(self):
        self.element.style.display = 'none'
        self._interceptor.uninstall()

    def focus_search(self):
        self._search.focus()


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
            data-name="option_popup" style="display: none">
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
        vis = self.option_popup.visible
        console.log(f'_input__click: vis={vis}')
        if vis:
            self.option_popup.hide()
        else:
            self.option_popup.show()
            self.option_popup.focus_search()
