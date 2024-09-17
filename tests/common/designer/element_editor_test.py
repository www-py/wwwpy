from pathlib import Path

from tests.common import dyn_sys_path
from wwwpy.common.designer import code_info
from wwwpy.common.designer.element_editor import ElementEditor
from wwwpy.common.designer.element_library import ElementDef, EventDef, AttributeDef
from wwwpy.common.designer.element_path import ElementPath
from wwwpy.common.designer.html_locator import Node, NodePath


class TestEvents:

    def test_events__no_event(self, dyn_sys_path):
        # GIVEN
        source = '''
class Component2: 
    def connectedCallback(self):
        self.element.innerHTML = """<button data-name='button1'>bar</button>"""
    '''
        # WHEN
        target_fixture = TargetFixture(dyn_sys_path, source)
        target = target_fixture.target

        # THEN
        assert len(target.events) == 1
        ev = target.events[0]
        assert ev.definition == target_fixture.click_ed
        assert not ev.handled
        assert ev.method is None

    def test_events__event_present(self, dyn_sys_path):
        # GIVEN
        source = '''
class Component2:     
    def connectedCallback(self):
        self.element.innerHTML = """<button data-name='button1'>bar</button>"""

    def button1__click(self, event):
        pass
    '''

        # WHEN
        target_fixture = TargetFixture(dyn_sys_path, source)
        target = target_fixture.target

        # THEN
        assert len(target.events) == 1
        ev = target.events[0]
        assert ev.definition == target_fixture.click_ed
        assert ev.handled
        assert ev.method is not None
        assert ev.method.name == 'button1__click'
        assert not ev.method.is_async

    def test_events__add_event(self, dyn_sys_path):
        # GIVEN
        source = '''
class Component2:
    some_prop = 1
    def connectedCallback(self):
        self.element.innerHTML = """<button data-name='button1'>bar</button>"""
'''

        # WHEN
        target_fixture = TargetFixture(dyn_sys_path, source)
        target = target_fixture.target
        target.events[0].do_action()

        # THEN
        ci = code_info.class_info(Path(target_fixture.element_path.concrete_path).read_text(), 'Component2')
        actual_method = ci.methods_by_name.get('button1__click', None)
        assert actual_method

    def test_events__add_event_when_it_already_exists_should_leave_source_the_same(self, dyn_sys_path):
        # GIVEN
        source = '''
class Component2:
    some_prop = 1
    
    def connectedCallback(self):
        self.element.innerHTML = """<button data-name='button1'>bar</button>"""

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


class TestAttributes:

    def test_attributes__no_attribute(self, dyn_sys_path):
        # GIVEN
        source = '''
class Component2():

    def connectedCallback(self):
        self.element.innerHTML = """<button data-name='button1'>bar</button>"""
    '''

        # WHEN
        target_fixture = TargetFixture(dyn_sys_path, source)

        # THEN test attribute 'name' is empty
        assert len(target_fixture.target.attributes) >= 1
        name_ae = target_fixture.target.attributes.get('name')
        assert name_ae
        assert name_ae.definition == target_fixture.name_ad
        assert not name_ae.exists
        assert name_ae.value is None

    def test_attributes__attribute_present(self, dyn_sys_path):
        # GIVEN
        source = '''
class Component2():
    def connectedCallback(self):
        self.element.innerHTML = """<button data-name='button1' name='foo'>bar</button>"""
    '''

        # WHEN
        target_fixture = TargetFixture(dyn_sys_path, source)

        # THEN
        assert len(target_fixture.target.attributes) >= 1
        name_ae = target_fixture.target.attributes.get('name')
        assert name_ae
        assert name_ae.definition == target_fixture.name_ad
        assert name_ae.exists
        assert name_ae.value == 'foo'


class TargetFixture:
    def __init__(self, dyn_sys_path, source: str):
        dyn_sys_path.write_module('', 'component2.py', source)
        from component2 import Component2  # noqa - dynamically created module
        component2 = Component2()

        # artificially create a NodePath; in production it is created by the element_path that uses the browser DOM
        # NodePath([Node("button", 1, {'data-name': 'button1'})])
        path: NodePath = _node_path(source, 'Component2', [0])

        self.click_ed = EventDef('click')
        self.name_ad = AttributeDef('name', mandatory=False, closed_values=False)
        element_def = ElementDef('button', 'js.HTMLButtonElement',
                                 events=[self.click_ed], attributes=[self.name_ad])

        self.element_path = ElementPath(component2, path)
        self.target = ElementEditor(self.element_path, element_def)


def _node_path(source: str, class_name, indexed_path: list[int]) -> NodePath:
    from wwwpy.common.designer import code_strings as cs, html_parser as hp, html_locator as hl
    html = cs.html_from_source(source, class_name)
    nodes = hp.html_to_tree(html)
    path = hl.tree_to_path(nodes, indexed_path)
    return path
