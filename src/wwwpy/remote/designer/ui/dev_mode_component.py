from __future__ import annotations

from pathlib import Path

import wwwpy.remote.component as wpc
import js

from wwwpy.common import files
from wwwpy.common.designer import dev_mode
from wwwpy.remote import dict_to_js, dict_to_py
from pyodide.ffi import create_proxy
from .toolbox import ToolboxComponent


def show():
    js.document.body.append(DevModeComponent().element)


class classproperty(property):
    def __get__(self, cls, owner):
        return classmethod(self.fget).__get__(None, owner)()


class DevModeComponent(wpc.Component, tag_name='wwwpy-dev-mode'):
    toolbox: ToolboxComponent = wpc.element()

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

        # from wwwpy.common.quickstart import is_empty_project
        # if is_empty_project(Path(files._bundle_path)):
        #     self.toolbox.element.style.display = 'none'
