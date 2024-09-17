from pathlib import Path

from tests.common import dyn_sys_path
from wwwpy.common.designer import code_info
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


def test_events__add_event(dyn_sys_path):
    # GIVEN
    source = '''
class Component2:
    some_prop = 1
'''

    # WHEN
    target_fixture = TargetFixture(dyn_sys_path, source)
    target = target_fixture.target
    target.events[0].do_action()

    # THEN
    ci = code_info.class_info(Path(target_fixture.element_path.concrete_path).read_text(), 'Component2')
    actual_method = ci.methods_by_name.get('button1__click', None)
    assert actual_method


def test_events__add_event_when_it_already_exists_should_leave_source_the_same(dyn_sys_path):
    # GIVEN
    source = '''
class Component2:
    some_prop = 1
    
    def button1__click(self, event): # could be async
        pass
'''

    # WHEN
    target_fixture = TargetFixture(dyn_sys_path, source)
    target = target_fixture.target
    target.events[0].do_action()

    # THEN
    current_source = Path(target_fixture.element_path.concrete_path).read_text()
    assert current_source == source


class TargetFixture:
    def __init__(self, dyn_sys_path, source: str):
        dyn_sys_path.write_module('', 'component2.py', source)
        from component2 import Component2
        component2 = Component2()

        path = [Node("button", 1, {'data-name': 'button1'})]

        self.event_def = EventDef('click')
        element_def = ElementDef('button', 'js.HTMLButtonElement', events=[self.event_def])

        self.element_path = ElementPath(component2, path)
        self.target = ElementEditor(self.element_path, element_def)
