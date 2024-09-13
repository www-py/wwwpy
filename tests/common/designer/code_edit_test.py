from wwwpy.common.designer.code_edit import Attribute, info, add_attribute, add_component, ComponentDef, add_method
from wwwpy.common.designer.html_edit import Position
from wwwpy.common.designer.html_locator import Node


def test_add_attribute():
    original_source = """
import wwwpy.remote.component as wpc

class MyElement(wpc.Component):
    btn1: HTMLButtonElement = wpc.element()
    """

    # Expected source after adding the new attribute
    expected_source = """
import wwwpy.remote.component as wpc

class MyElement(wpc.Component):
    btn1: HTMLButtonElement = wpc.element()
    btn2: HTMLButtonElement = wpc.element()
    """

    modified_source = add_attribute(original_source, 'MyElement',
                                    Attribute('btn2', 'HTMLButtonElement', 'wpc.element()'))

    modified_info = info(modified_source)
    expected_info = info(expected_source)

    assert modified_info == expected_info, "The attribute was not added correctly."


def test_add_attribute__should_retain_comments_and_style():
    original_source = """
import wwwpy.remote.component as wpc
# comment1
class MyElement(wpc.Component): # comment2
    btn1: HTMLButtonElement = wpc.element()
    """

    expected_source = """
import wwwpy.remote.component as wpc
# comment1
class MyElement(wpc.Component): # comment2
    btn1: HTMLButtonElement = wpc.element()
    btn2: js.HTMLButtonElement = wpc.element()
    """

    modified_source = add_attribute(original_source, 'MyElement',
                                    Attribute('btn2', 'js.HTMLButtonElement', 'wpc.element()'))

    assert modified_source == expected_source


def test_add_attribute__should_add_it_on_top_after_other_attributes():
    original_source = """
import wwwpy.remote.component as wpc
# comment1
class MyElement(wpc.Component): # comment2
    btn1: HTMLButtonElement = wpc.element()
    def foo(self):
        pass
    """

    expected_source = """
import wwwpy.remote.component as wpc
# comment1
class MyElement(wpc.Component): # comment2
    btn1: HTMLButtonElement = wpc.element()
    btn2: js.HTMLButtonElement = wpc.element()
    def foo(self):
        pass
    """

    modified_source = add_attribute(original_source, 'MyElement',
                                    Attribute('btn2', 'js.HTMLButtonElement', 'wpc.element()'))

    assert modified_source == expected_source


def test_add_attribute__should_honor_classname():
    original_source = """
class MyElement(wpc.Component):
        pass
class MyElement2(wpc.Component):
        pass
    """

    expected_source = """
class MyElement(wpc.Component):
        pass
class MyElement2(wpc.Component):
        btn1: js.HTMLButtonElement = wpc.element()
        pass
    """

    modified_source = add_attribute(original_source, 'MyElement2',
                                    Attribute('btn1', 'js.HTMLButtonElement', 'wpc.element()'))

    assert modified_source == expected_source


def test_add_component():
    original_source = """
import wwwpy.remote.component as wpc
class MyElement(wpc.Component):
    def foo(self):
        self.element.innerHTML = '''<div id='foo'><div></div><div id='target'></div></div>'''
    """

    expected_source = """
import wwwpy.remote.component as wpc
class MyElement(wpc.Component):
    btn1: js.Some = wpc.element()
    def foo(self):
        self.element.innerHTML = '''<div id='foo'><div></div><div id='target'></div><b name="btn1"></b></div>'''
    """

    component_def = ComponentDef('btn', 'js.Some', '<b name="#name#"></b>')
    node_path = [Node("DIV", 0, {'id': 'foo'}), Node("DIV", 1, {'id': 'target'})]
    modified_source = add_component(original_source, 'MyElement', component_def, node_path, Position.afterend)

    assert modified_source == expected_source


def test_add_method():
    original_source = """
import wwwpy.remote.component as wpc
class MyElement1(wpc.Component):
    btn1: js.Some = wpc.element()"""

    expected_source = original_source + """
    
    def button1__click(self, event):
        pass
    """
    modified_source = add_method(original_source, 'MyElement1', 'button1__click', 'event')
    assert modified_source == expected_source


def todo__test_add_component_should_add_attribute_type_js_import():
    """If I add a HTMLInputElement, be sure to import it from js"""

    # todo so, we need to take care of wpc.element() import and js import(s)
    # if there is already a wpc alias, we should add on it
    # the same for js imports
    # btw, the import just need to be
    # import wwwpy.remote.component as wpc
    # import js
