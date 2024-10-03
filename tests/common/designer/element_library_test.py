from wwwpy.common.designer import element_library


def test_element_library():
    el = element_library.element_library()
    assert len(el.elements) > 0

def test_hidden_element():
    assert element_library.element_library().by_tag_name('sl-drawer') is None


def test_shown_element():
    assert element_library.element_library().by_tag_name('sl-button') is not None

