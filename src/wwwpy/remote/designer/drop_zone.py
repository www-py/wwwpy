from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from js import document, MouseEvent
from pyodide.ffi import create_proxy

from wwwpy.common.designer.html_edit import Position
from wwwpy.remote.widgets.filesystem_tree_widget import HTMLElement


@dataclass
class DropZone:
    target: HTMLElement
    position: Position


class _DropZoneSelector:
    def __init__(self):
        self._last_zone: DropZone | None = None
        self._callback: SelectorProtocol | None = None
        self._mousemove_proxy = create_proxy(self._mousemove)

    def start_selector(self, callback: SelectorProtocol = None):
        """It starts the process for the user to select a drop zone.
        While moving the mouse, it highlights the drop zones.
        """
        self._callback = callback
        _ensure_drop_zone_style()
        document.addEventListener('mousemove', self._mousemove_proxy)

    def stop(self) -> DropZone | None:
        """It stops the process of selecting a drop zone.
        It will remove the highlights and the event listener.
        It will return the selected DropZone
        """
        document.removeEventListener('mousemove', self._mousemove_proxy)
        self._remove_marker()
        result = self._last_zone
        return result

    def _mousemove(self, event: MouseEvent):
        position = _calc_position(event)
        element: HTMLElement = event.target
        zone_event = DropZone(element, position)
        if self._last_zone != zone_event:
            self._remove_marker()
            # console.log(f'candidate sending zone_event', zone_event.position, zone_event.target)
            css_class = _beforebegin_css_class if position == Position.beforebegin else _afterend_css_class
            element.classList.add(css_class)
            self._last_zone = zone_event
            if self._callback:
                self._callback(zone_event)
        else:
            pass
            # console.log(f'candidate discarded zone_event: {zone_event}')

    def _remove_marker(self):
        if self._last_zone is not None:
            _remove_class(self._last_zone.target, _beforebegin_css_class)
            _remove_class(self._last_zone.target, _afterend_css_class)


drop_zone_selector = _DropZoneSelector()

_beforebegin_css_class = 'drop-zone-beforebegin'
_afterend_css_class = 'drop-zone-afterend'


class SelectorProtocol(Protocol):
    def __call__(self, event: DropZone) -> None: ...


def _remove_class(target: HTMLElement, class_name: str):
    target.classList.remove(class_name)
    if target.classList.length == 0:
        target.removeAttribute('class')


def _ensure_drop_zone_style():
    drop_zone_highlight_style = 'drop-zone-highlight-style'
    _ensure_style_element(drop_zone_highlight_style, f"""
    .{_beforebegin_css_class} {{
        box-shadow: -4px -4px 0 green;
        position: relative;
        z-index: 10;
    }}
    .{_afterend_css_class} {{
        box-shadow: 2px 2px 2px 2px green;
        position: relative;
        z-index: 10;
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


def _calc_position(event: MouseEvent) -> Position:
    element: HTMLElement = event.target
    rect = element.getBoundingClientRect()

    # Calculate the position of the mouse relative to the element
    x = event.clientX - rect.left
    y = rect.height - (event.clientY - rect.top)
    h = rect.height
    w = rect.width
    if w == 0:
        return Position.inside
    m = h / w
    y2 = m * x
    res = Position.afterend if y <= y2 else Position.beforebegin
    # console.log(f'x={x}, y={y}, w={w}, h={h} m={m}, y2={y2} res={res}')
    return res
