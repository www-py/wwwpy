from wwwpy.common.designer.source_edit import ClassInfo, Attribute, Info, info, add_attribute


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
    btn2: HTMLButtonElement = wpc.element()
    """

    modified_source = add_attribute(original_source, Attribute('btn2', 'HTMLButtonElement', 'wpc.element()'))

    assert modified_source == expected_source
