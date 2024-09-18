from pathlib import Path

import pytest

from tests.common import dyn_sys_path, DynSysPath
from wwwpy.common.designer import code_info
from wwwpy.common.designer.element_editor import ElementEditor
from wwwpy.common.designer.element_library import ElementDef, EventDef, AttributeDef
from wwwpy.common.designer.element_path import ElementPath
from wwwpy.common.designer.html_locator import Node, NodePath


class TestEvents:

    def test_events__no_event(self, target_fixture):
        # GIVEN
        target_fixture.source = '''
class Component2: 
    def connectedCallback(self):
        self.element.innerHTML = """<button data-name='button1'>bar</button>"""
    '''
        # WHEN
        target = target_fixture.target

        # THEN
        assert len(target.events) == 1
        ev = target.events[0]
        assert ev.definition == target_fixture.click_ed
        assert not ev.handled
        assert ev.method is None

    def test_events__event_present(self, target_fixture):
        # GIVEN
        target_fixture.source = '''
class Component2:     
    def connectedCallback(self):
        self.element.innerHTML = """<button data-name='button1'>bar</button>"""

    def button1__click(self, event):
        pass
    '''

        # WHEN
        target = target_fixture.target

        # THEN
        assert len(target.events) == 1
        ev = target.events[0]
        assert ev.definition == target_fixture.click_ed
        assert ev.handled
        assert ev.method is not None
        assert ev.method.name == 'button1__click'
        assert not ev.method.is_async

    def test_events__add_event(self, target_fixture):
        # GIVEN
        target_fixture.source = '''
class Component2:
    some_prop = 1
    def connectedCallback(self):
        self.element.innerHTML = """<button data-name='button1'>bar</button>"""
'''

        # WHEN
        target = target_fixture.target
        target.events[0].do_action()

        # THEN
        ci = code_info.class_info(Path(target_fixture.element_path.concrete_path).read_text(), 'Component2')
        actual_method = ci.methods_by_name.get('button1__click', None)
        assert actual_method

    def test_events__add_event_when_it_already_exists_should_leave_source_the_same(self, target_fixture):
        # GIVEN
        target_fixture.source = '''
class Component2:
    some_prop = 1
    
    def connectedCallback(self):
        self.element.innerHTML = """<button data-name='button1'>bar</button>"""

    def button1__click(self, event): # could be async
        pass
'''

        # WHEN
        target = target_fixture.target
        target.events[0].do_action()

        # THEN
        current_source = Path(target_fixture.element_path.concrete_path).read_text()
        assert current_source == target_fixture.source


class TestAttributes:

    def test_no_attribute(self, target_fixture):
        # GIVEN
        target_fixture.source = '''
class Component2():

    def connectedCallback(self):
        self.element.innerHTML = """<button data-name='button1'>bar</button>"""
    '''

        # WHEN
        target = target_fixture.target

        # THEN test attribute 'name' is empty
        assert len(target.attributes) >= 1
        name_ae = target.attributes.get('name')
        assert name_ae
        assert name_ae.definition == target_fixture.name_ad
        assert not name_ae.exists
        assert name_ae.value is None

    def test_attribute_present(self, target_fixture):
        # GIVEN
        target_fixture.source = '''
class Component2():
    def connectedCallback(self):
        self.element.innerHTML = """<button data-name='button1' name='foo'>bar</button>"""
    '''

        # WHEN
        target = target_fixture.target

        # THEN
        assert len(target.attributes) >= 1
        name_ae = target.attributes.get('name')
        assert name_ae
        assert name_ae.definition == target_fixture.name_ad
        assert name_ae.exists
        assert name_ae.value == 'foo'

    def test_attribute_correct_escaping(self, target_fixture):
        # GIVEN
        target_fixture.source = '''
class Component2():
    def connectedCallback(self):
        self.element.innerHTML = """<button data-name='button1' name="<'&quot;&amp;>">bar</button>"""
    '''

        # WHEN

        # THEN
        name_ae = target_fixture.target.attributes.get('name')
        assert name_ae
        assert name_ae.value == """<'"&>"""

    def test_update_existing_attribute_value(self, target_fixture):
        # GIVEN
        target_fixture.source = '''
class Component2():
    def connectedCallback(self):
        self.element.innerHTML = """<button data-name='button1' name='foo'>bar</button>"""
    '''
        # WHEN
        target = target_fixture.target
        target.attributes.get('name').value = 'btn1'

        # THEN
        # language=html
        assert "<button data-name='button1' name='btn1'>bar</button>" == target_fixture.current_html

    def test_add_attribute(self, target_fixture):
        # GIVEN
        target_fixture.source = '''
class Component2():
    def connectedCallback(self):
        self.element.innerHTML = """<button id='foo'>bar</button>"""
    '''
        # WHEN
        target = target_fixture.target
        target.attributes.get('name').value = 'btn1'

        # THEN
        # language=html
        assert """<button id='foo' name="btn1">bar</button>""" == target_fixture.current_html

    def test_remove_attribute(self, target_fixture):
        # GIVEN
        target_fixture.source = '''
class Component2():
    def connectedCallback(self):
        self.element.innerHTML = """<button id='foo' name="btn1">bar</button>"""
    '''
        # WHEN
        target = target_fixture.target
        target.attributes.get('name').remove()

        # THEN
        # language=html
        assert """<button id='foo' >bar</button>""" == target_fixture.current_html


@pytest.fixture
def target_fixture(dyn_sys_path):
    return TargetFixture(dyn_sys_path)


class TargetFixture:

    def __init__(self, dyn_sys_path, source: str = None):
        self._source = None
        self.dyn_sys_path: DynSysPath = dyn_sys_path
        self.click_ed = EventDef('click')
        self.events = [self.click_ed]
        self.name_ad = AttributeDef('name', mandatory=False, closed_values=False)
        self.attributes = [self.name_ad]
        self.element_def = ElementDef('button', 'js.HTMLButtonElement', events=self.events, attributes=self.attributes)
        self.element_path: ElementPath = None
        self.target: ElementEditor = None
        if source:
            self.source = source

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, value):
        assert self._source is None, 'source can be written only once'
        self._source = value
        source = value
        self.dyn_sys_path.write_module('', 'component2.py', source)
        from component2 import Component2  # noqa - dynamically created module
        component2 = Component2()

        # artificially create a NodePath; in production it is created by the element_path that uses the browser DOM
        # NodePath([Node("button", 1, {'data-name': 'button1'})])
        path: NodePath = _node_path(source, 'Component2', [0])

        self.element_path = ElementPath(component2, path)
        self.target = ElementEditor(self.element_path, self.element_def)

    @property
    def current_source(self) -> str:
        comp_path = self.dyn_sys_path.path / 'component2.py'
        return comp_path.read_text()

    @property
    def current_html(self) -> str:
        from wwwpy.common.designer import code_strings as cs
        html = cs.html_from_source(self.current_source, self.element_path.class_name)
        return html


def _node_path(source: str, class_name, indexed_path: list[int]) -> NodePath:
    from wwwpy.common.designer import code_strings as cs, html_parser as hp, html_locator as hl
    html = cs.html_from_source(source, class_name)
    nodes = hp.html_to_tree(html)
    path = hl.tree_to_path(nodes, indexed_path)
    return path
