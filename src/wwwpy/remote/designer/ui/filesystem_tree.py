# Browse pyscript virtual filesystem
from __future__ import annotations

import os
from pathlib import Path
from typing import List

import js
from js import console

from wwwpy.common.files import zip_in_memory
from wwwpy.remote.designer.ui.draggable_component import DraggableComponent
from wwwpy.remote.files import download_bytes
import wwwpy.remote.component as wpc


class FilesystemTree(wpc.Component):
    path: Path
    _indent: int = 0
    children: List[FilesystemTree]

    _entity: js.HTMLElement = wpc.element()
    entity_actions: js.HTMLElement = wpc.element()
    _children: js.HTMLElement = wpc.element()
    _download: js.HTMLElement = wpc.element()
    _view: js.HTMLElement = wpc.element()

    def init_component(self):
        # language=html
        self.element.innerHTML = """<div>
    <span data-name="_entity" style="cursor: pointer"></span>
    <span data-name="entity_actions" style="cursor: pointer">
        <span data-name="_download" >&nbsp ⬇</span>
        <span data-name="_view"> 👁 &nbsp</span>
    </span>
    <div data-name="_children" style="margin-left: 1em"></div>
</div>
        """

    async def _entity__click(self, event):
        self._toggle_display()

    async def _download__click(self, event):
        self._do_download()

    def show_path(self, path: str | Path, indent=1):
        self.path = Path(path)
        self._indent = indent
        self.children = []
        self._view.style.display = 'none' if self.is_dir() else ''

        if self._indent > 1:
            self._toggle_display()

        self._update_caption()

        if self.is_dir():
            self._recurse()

    def is_dir(self):
        # return self.path.is_dir() # in pyodide: `PermissionError: [Errno 63] Operation not permitted: '/proc/self/fd'`
        return os.path.isdir(self.path)

    def is_file(self):
        return os.path.isfile(self.path)

    def _toggle_display(self, *args):
        self._children.style.display = '' if self._children_hidden() else 'none'
        self._update_caption()

    def _do_download(self, *args):
        console.log(f'click {self.path.absolute()}')
        if self.is_dir():
            download_bytes(self.path.name + '.zip', zip_in_memory(self.path))
        else:
            download_bytes(self.path.name, self.path.read_bytes())

    def _update_caption(self):
        if_dir = '▸' if self._children_hidden() else '▼'
        pre = if_dir if self.is_dir() else ' '
        self._entity.innerHTML = (f'<span style="display:inline-block; width: 1em">{pre}</span>'
                                  + ' ' + self.path.name)

    def _children_hidden(self):
        s = self._children.style
        return not s.display == ''

    def _recurse(self):
        for child in self.path.glob('*'):
            w = FilesystemTree()
            w.show_path(child, self._indent + 1)
            self.children.append(w)
            self._children.append(w.root_element())

    def _view__click(self, event):
        if not self.is_file():
            return
        component = DraggableComponent()
        js.document.body.append(component.element)
        fragment = js.document.createRange().createContextualFragment(f"""
        <span slot='title'>{self.path} <button data-name="close" style="cursor:pointer">X</button></span>
        <pre data-name="pre1"></pre>
        """)
        selector = fragment.querySelector(f'[data-name="close"]')
        selector.onclick = lambda ev: component.element.remove()
        pre1: js.HTMLElement = fragment.querySelector(f'[data-name="pre1"]')
        pre1.innerText = self.path.read_text()
        component.element.append(fragment)