from wwwpy.common.designer import cst
from wwwpy.common.designer.cst import ClassInfo, AttrInfo, SourceInfo


def test_info():
    target = cst.source_info(
        """
import wwwpy.remote.component as wpc

class MyElement(wpc.Component):
    btn1: HTMLButtonElement = wpc.element()
    """
    )

    expect = SourceInfo(classes=[ClassInfo('MyElement', [AttrInfo('btn1', 'HTMLButtonElement', 'wpc.element()')])])
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
    btn2: HTMLButtonElement = wpc.element()
    btn1: HTMLButtonElement = wpc.element()
    """

    # Add a new attribute
    modified_source = cst.source_add_attribute(original_source, cst.AttrInfo('btn2', 'HTMLButtonElement', 'wpc.element()'))

    # Parse the modified source to verify the addition
    modified_info = cst.source_info(modified_source)
    expected_info = cst.source_info(expected_source)

    # Assert that the modified source info matches the expected info
    assert modified_info == expected_info, "The attribute was not added correctly."