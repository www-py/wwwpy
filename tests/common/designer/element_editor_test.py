from pathlib import Path

from tests.common import dyn_sys_path
from wwwpy.common.designer.element_editor import ElementEditor
from wwwpy.common.designer.element_library import ElementDef, EventDef
from wwwpy.common.designer.element_path import ElementPath
from wwwpy.common.designer.html_locator import Node


def test_add_event(dyn_sys_path):
    # GIVEN
    dyn_sys_path.write_module('', 'component2.py', '''
class Component2: 
    pass
    ''')

    from component2 import Component2
    component2 = Component2()

    path = [Node("div", 1, {'class': 'class1'})]
    event_def = EventDef('click')
    element_def = ElementDef('button', 'js.HTMLButtonElement', events=[event_def])

    # WHEN
    target = ElementEditor(ElementPath(component2, path), element_def)

    # THEN
    assert len(target.events) == 1
    assert not target.events[0].handled
    assert target.events[0].definition == event_def
