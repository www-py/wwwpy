from __future__ import annotations

import js

import wwwpy.remote.component as wpc
from wwwpy.common import files
from wwwpy.remote import dict_to_js, dict_to_py
from . import quickstart_ui
from .toolbox import ToolboxComponent


def show():
    js.document.body.append(DevModeComponent().element)


class classproperty(property):
    def __get__(self, cls, owner):
        return classmethod(self.fget).__get__(None, owner)()


class DevModeComponent(wpc.Component, tag_name='wwwpy-dev-mode'):
    toolbox: ToolboxComponent = wpc.element()
    _quickstart: bool

    @classproperty
    def instance(cls) -> DevModeComponent:  # noqa
        element = js.document.getElementsByTagName(DevModeComponent.component_metadata.tag_name)
        if element.length == 0:
            raise Exception('DevModeComponent is not available')
        first_element = element[0]
        component = wpc.get_component(first_element)
        if not isinstance(component, DevModeComponent):
            raise Exception(f'element is not a DevModeComponent: {dict_to_py(first_element)}')
        return component

    def root_element(self):
        return self.shadow

    def init_component(self):
        self.shadow = self.element.attachShadow(dict_to_js({'mode': 'open'}))
        # language=html
        self.shadow.innerHTML = """
<wwwpy-toolbox data-name="toolbox"></wwwpy-toolbox>        
        """
        from wwwpy.common import quickstart
        self._quickstart = quickstart.is_empty_project(files._bundle_path)
        if self._quickstart:
            quickstart_ui.show_selector()

    def quickstart_visible(self) -> bool:
        return self._quickstart
