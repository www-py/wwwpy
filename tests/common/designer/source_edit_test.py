from wwwpy.common.designer import source_edit
from wwwpy.common.designer.source_edit import ClassInfo, Attribute, Info


def test_info():
    target = source_edit.info(
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

    # Add a new attribute
    modified_source = source_edit.add_attribute(original_source, source_edit.Attribute('btn2', 'HTMLButtonElement', 'wpc.element()'))

    # Parse the modified source to verify the addition
    modified_info = source_edit.info(modified_source)
    expected_info = source_edit.info(expected_source)

    # Assert that the modified source info matches the expected info
    assert modified_info == expected_info, "The attribute was not added correctly."