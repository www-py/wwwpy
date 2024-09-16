from dataclasses import dataclass
from pathlib import Path

from tests.common import dyn_sys_path
from wwwpy.common.designer.element_editor import ElementEditor
from wwwpy.common.designer.element_library import ElementDef, EventDef
from wwwpy.common.designer.element_path import ElementPath
from wwwpy.common.designer.html_locator import Node


def test_events__no_event(dyn_sys_path):
    # GIVEN
    source = '''
class Component2: 
    pass
    '''
    # WHEN
    target_fixture = TargetFixture(dyn_sys_path, source)
    target = target_fixture.target

    # THEN
    assert len(target.events) == 1
    assert target.events[0].definition == target_fixture.event_def
    assert not target.events[0].handled


def test_events__event_present(dyn_sys_path):
    # GIVEN
    source = '''
class Component2:     
    def button1__click(self, event):
        pass
    '''

    # WHEN
    target_fixture = TargetFixture(dyn_sys_path, source)
    target = target_fixture.target

    # THEN
    assert len(target.events) == 1
    assert target.events[0].definition == target_fixture.event_def
    assert target.events[0].handled


class TargetFixture:
    def __init__(self, dyn_sys_path, source: str):
        dyn_sys_path.write_module('', 'component2.py', source)
        from component2 import Component2
        component2 = Component2()

        path = [Node("button", 1, {'data-name': 'button1'})]

        self.event_def = EventDef('click')
        element_def = ElementDef('button', 'js.HTMLButtonElement', events=[self.event_def])

        self.target = ElementEditor(ElementPath(component2, path), element_def)

