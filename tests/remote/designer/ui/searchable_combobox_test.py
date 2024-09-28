from dataclasses import dataclass

from wwwpy.remote.designer.ui.searchable_combobox2 import SearchableComboBox
from js import document, window

import pytest


@pytest.fixture()
def target():
    target = SearchableComboBox()
    document.body.innerHTML = ''
    document.body.append(target.element)
    return target


def test_text_value(target):
    # GIVEN
    assert 'foo123' not in target.root_element().innerHTML

    # WHEN
    target.text_value = 'foo123'

    # THEN
    assert 'foo123' == target.text_value


def test_input_click__should_open_search(target):
    # GIVEN

    # WHEN
    target._input.click()

    # THEN


def test_find_by_placeholder(target):
    target.placeholder = 'search...'
    assert '' == target.text_value
    target._input_element().value = 'foo123'
    assert 'foo123' == target.text_value


def test_popup_activate(target):
    options_str = ['foo', 'bar', 'baz']
    target.option_popup.options = options_str

    popup = target.option_popup.root_element()

    element_state(popup).assert_not_visible()
    target.option_popup.activate()
    element_state(popup).assert_visible()

    html = popup.innerHTML
    for o in options_str:
        assert o in html


def test_popup_activate__with_input_click(target):
    # GIVEN
    options_str = ['foo', 'bar', 'baz']
    target.option_popup.options = options_str

    popup = target.option_popup.root_element()

    # WHEN
    target._input_element().click()

    # THEN
    element_state(popup).assert_visible()


def test_popup__click_option(target):
    # GIVEN

    target.option_popup.options = ['foo', 'bar', 'baz']

    # WHEN
    target._input_element().click()
    target.option_popup.options[1].root_element().click()

    # THEN
    assert target.text_value == 'bar'

    popup = target.option_popup.root_element()
    element_state(popup).assert_not_visible()


@dataclass
class ElementState:
    document_contains: bool
    display: str
    visibility: str
    opacity: str
    width: float
    height: float

    @property
    def visible(self):
        return (self.display != 'none' and self.visibility != 'hidden' and
                self.opacity != '0' and self.width > 0 and self.height > 0)

    def assert_visible(self):
        __tracebackhide__ = True
        assert self.visible, self

    def assert_not_visible(self):
        __tracebackhide__ = True
        assert not self.visible, self


def element_state(element) -> ElementState:
    e = element
    #  document.contains(element)
    style = window.getComputedStyle(e)
    rect = e.getBoundingClientRect()
    return ElementState(
        document_contains=document.contains(element),
        display=style.display,
        visibility=style.visibility,
        opacity=style.opacity,
        width=rect.width,
        height=rect.height,
    )


def is_element_visible(element):
    if not element:
        return False  # Element doesn't exist

    # Check if element is part of the DOM
    if not document.contains(element):
        return False

    # Check if the element or its parents have `display: none`, `visibility: hidden`, or `opacity: 0`
    style = window.getComputedStyle(element)
    if style.display == 'none' or style.visibility == 'hidden' or style.opacity == '0':
        return False

    # Check if the element has zero dimensions
    rect = element.getBoundingClientRect()
    if rect.width == 0 or rect.height == 0:
        return False

    # The element is visible
    return True
