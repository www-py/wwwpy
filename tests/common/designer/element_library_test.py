from wwwpy.common.designer import element_library


def test_element_library():
    el = element_library.element_library()
    assert len(el.elements) > 0
