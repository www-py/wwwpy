from wwwpy.common.designer.source_edit import ClassInfo, Attribute, Info, info, add_attribute, html_edit


def test_info():
    target = info(
        """
import wwwpy.remote.component as wpc

class MyElement(wpc.Component):
    btn1: HTMLButtonElement = wpc.element()
    """
    )

    expect = Info(classes=[ClassInfo('MyElement', [Attribute('btn1', 'HTMLButtonElement', 'wpc.element()')])])
    assert target == expect


def test_info_with_js_element():
    target = info(
        """
import wwwpy.remote.component as wpc

class MyElement(wpc.Component):
    btn1: js.HTMLButtonElement = wpc.element()
    """
    )

    expect = Info(classes=[ClassInfo('MyElement', [Attribute('btn1', 'js.HTMLButtonElement', 'wpc.element()')])])
    assert target == expect


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

    modified_source = add_attribute(original_source, Attribute('btn2', 'HTMLButtonElement', 'wpc.element()'))

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

    modified_source = add_attribute(original_source, Attribute('btn2', 'js.HTMLButtonElement', 'wpc.element()'))

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

    modified_source = add_attribute(original_source, Attribute('btn2', 'js.HTMLButtonElement', 'wpc.element()'))

    assert modified_source == expected_source


def test_html_edit():
    common_piece = '''
import wwwpy.remote.component as wpc
# comment1
class MyElement(wpc.Component): # comment2
    btn1: HTMLButtonElement = wpc.element()
    def connectedCallback(self):        
        self.element.innerHTML = """
        <div>my-element5 a</div>
        <button data-name='btn1'>list async tasks</button>
        '''

    original_source = common_piece + '"""'
    exepct_source = common_piece + '''<button data-name='btn2'>list files in folder</button>"""'''

    def manipulate_html(html):
        return html + "<button data-name='btn2'>list files in folder</button>"

    actual_source = html_edit(original_source, manipulate_html)

    assert actual_source == exepct_source


def todo__test_add_component_should_add_attribute_type_js_import():
    """If I add a HTMLInputElement, be sure to import it from js"""

    # so, we need to take care of wpc.element() import and js import(s)
    # if there is already a wpc alias, we should add on it
    # the same for js imports
    # btw, the import just need to be
    # import wwwpy.remote.component as wpc
    # import js
