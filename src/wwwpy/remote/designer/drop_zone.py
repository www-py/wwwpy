from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Protocol

from js import document, MouseEvent, console
from pyodide.ffi.wrappers import add_event_listener, remove_event_listener
from pyodide.ffi import create_proxy

from wwwpy.remote.widgets.filesystem_tree_widget import HTMLElement


class _DropZoneSelector:
    def __init__(self):
        self._future = None

    def start(self):
        """It starts the process for the user to select a drop zone.
        While moving the mouse, it highlights the drop zones.
        It will intercept (and prevent) the mouse click event.
        On such a mouse click event, it will stop the process and set the result.
        """
        self._future = asyncio.Future()

    def stop(self):
        """It stops the process of selecting a drop zone.
        It will remove the highlights and the event listener.
        """

    async def result(self):
        """It returns the result. It could be:
        - the drop zone if selected
        - None if the process was stopped before selection
        """
        pass


drop_zone_selector = _DropZoneSelector()

from enum import Enum


class Position(Enum):
    beforebegin = 1
    afterend = 2


_beforebegin_css_class = 'drop-zone-beforebegin'
_afterend_css_class = 'drop-zone-afterend'


@dataclass
class DropZoneEvent:
    target: HTMLElement
    position: Position


class SelectorProtocol(Protocol):
    def __call__(self, event: DropZoneEvent) -> None: ...


def _remove_class(target: HTMLElement, class_name: str):
    target.classList.remove(class_name)
    if target.classList.length == 0:
        target.removeAttribute('class')


def start_selector(callback: SelectorProtocol):
    last_event: DropZoneEvent | None = None

    def mousemove(event: MouseEvent):
        element: HTMLElement = event.target
        rect = element.getBoundingClientRect()

        # Calculate the position of the mouse relative to the element
        mouse_x = event.clientX - rect.left
        mouse_y = event.clientY - rect.top

        # Determine the position relative to the diagonal
        if mouse_x + mouse_y < rect.width:  # Below the diagonal
            position = Position.beforebegin
        else:  # Above the diagonal
            position = Position.afterend

        zone_event = DropZoneEvent(element, position)
        nonlocal last_event
        if last_event != zone_event:
            if last_event is not None:
                _remove_class(last_event.target, _beforebegin_css_class)
                _remove_class(last_event.target, _afterend_css_class)
            console.log(f'candidate sending zone_event: {zone_event}')
            element.classList.add(_beforebegin_css_class if position == Position.beforebegin else _afterend_css_class)
            last_event = zone_event
            callback(zone_event)
        else:
            console.log(f'candidate discarded zone_event: {zone_event}')

    mmp = create_proxy(mousemove)
    document.addEventListener('mousemove', mmp)
    # add_event_listener(document, 'mousemove', create_proxy(mousemove))


def _ensure_drop_zone_style():
    drop_zone_highlight_style = 'drop-zone-highlight-style'
    _ensure_style_element(drop_zone_highlight_style, f"""
    .{_beforebegin_css_class} {{
        box-shadow: -2px -2px 0 green;
    }}
    .{_afterend_css_class} {{
        box-shadow: 2px 2px 2px 2px green;
    }}
""")


def _ensure_style_element(element_id: str, style_content: str):
    st = document.head.querySelector(f'#{element_id}')
    if st is None:
        st = document.createElement('style')
        st.id = element_id
        document.head.appendChild(st)

    if st.innerHTML != style_content:
        st.innerHTML = style_content