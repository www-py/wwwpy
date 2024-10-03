from __future__ import annotations

from typing import Tuple, List, Callable

import js
from js import document, console, ResizeObserver
from pyodide.ffi import create_proxy
from pyodide.ffi.wrappers import add_event_listener, remove_event_listener

import wwwpy.remote.component as wpc
from wwwpy.remote import dict_to_js


class DraggableComponent(wpc.Component, tag_name='wwwpy-draggable-component'):
    container_div: wpc.HTMLElement = wpc.element()
    draggable_component_div: wpc.HTMLElement = wpc.element()
    resize_handle: wpc.HTMLElement = wpc.element()
    client_x = 0
    client_y = 0
    css_border = 2  # 1px border on each side, so we need to subtract 2px from width and height
    geometry_change_listeners: List[Callable[[], None]] = []

    def root_element(self):
        return self.shadow

    def init_component(self):
        self.shadow = self.element.attachShadow(dict_to_js({'mode': 'open'}))
        # language=html
        self.shadow.innerHTML = """
<style>
.wwwpy-container_div {
  position: absolute;
  z-index: 100000;
  background-color: black;
  border: 1px solid #d3d3d3;
  text-align: center;
  resize: both;
  overflow: auto;
}

.wwwpy-draggable_component_div {
  padding: 10px;
  cursor: move;
  z-index: 1001;
  background-color: #2196F3;
  color: #fff;
}

</style>        
<div data-name="container_div" class='wwwpy-container_div'>
    <div  data-name="draggable_component_div" class='wwwpy-draggable_component_div' >
        <slot name='title' >slot=title</slot>
    </div>
    <slot>slot=default</div>    
</div> 
"""
        self.client_x = 0
        self.client_y = 0
        tb = self.container_div

        def tb_print(*args):
            console.log(f'offsets of container_div: {self.geometry()}')

        tb.print = tb_print

        def on_resize(entries, observer):
            tb.print()
            self._on_geometry_change()

        resize_observer = ResizeObserver.new(create_proxy(on_resize))
        resize_observer.observe(self.container_div)

    def _on_geometry_change(self):
        for listener in self.geometry_change_listeners:
            listener()

    def draggable_component_div__touchstart(self, e: js.TouchEvent):
        self._move_start(e)

    def draggable_component_div__mousedown(self, e: js.MouseEvent):
        self._move_start(e)

    def _move_start(self, e: js.MouseEvent | js.TouchEvent):
        e.preventDefault()
        self.client_x = clientX(e)  # e.clientX
        self.client_y = clientY(e)  # e.clientY
        add_event_listener(document, 'mousemove', self._move)
        add_event_listener(document, 'mouseup', self._move_stop)
        add_event_listener(document, 'touchmove', self._move)
        add_event_listener(document, 'touchend', self._move_stop)

    def _move(self, event: js.MouseEvent | js.TouchEvent):
        # event.preventDefault()
        x = clientX(event)
        y = clientY(event)
        delta_x = self.client_x - x
        delta_y = self.client_y - y
        self.client_x = x
        self.client_y = y

        new_left = self.container_div.offsetLeft - delta_x
        new_top = self.container_div.offsetTop - delta_y

        self.set_position(new_left, new_top)
        self._on_geometry_change()

    def _move_stop(self, event):
        remove_event_listener(document, 'mousemove', self._move)
        remove_event_listener(document, 'mouseup', self._move_stop)
        remove_event_listener(document, 'touchmove', self._move)
        remove_event_listener(document, 'touchend', self._move_stop)

    def geometry(self) -> Tuple[int, int, int, int]:
        t = self.container_div
        return t.offsetTop, t.offsetLeft, (t.offsetWidth - self.css_border), (t.offsetHeight - self.css_border)

    def set_geometry(self, geometry_tuple):
        top, left, width, height = geometry_tuple
        self.set_position(left, top)
        self.set_size(f"{height}px", f"{width}px")

    def set_position(self, left, top):
        self.container_div.style.top = f"{top}px"
        self.container_div.style.left = f"{left}px"

    def set_size(self, h, w):
        self.container_div.style.width = w
        self.container_div.style.height = h

    def acceptable_geometry(self) -> bool:
        top, left, width, height = self.geometry()
        return width > 100 and height > 100


def clientX(event: js.MouseEvent | js.TouchEvent):
    #   var top = e.clientY || e.targetTouches[0].pageY;
    # return event.clientX if hasattr(event, 'clientX') else event.targetTouches[0].clientX
    if hasattr(event, 'targetTouches'):
        return list(event.targetTouches)[0].clientX
    return event.clientX


def clientY(event: js.MouseEvent | js.TouchEvent):
    return event.clientY if hasattr(event, 'clientY') else list(event.targetTouches)[0].clientY
